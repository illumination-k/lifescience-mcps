import logging
from io import BytesIO

import fitz  # PyMuPDF
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class PDFTextBlock(BaseModel):
    """Represents a block of text from a PDF with position information."""

    text: str
    page_number: int
    block_type: str  # "text", "heading", "title", "caption", etc.
    font_size: float
    font_name: str
    is_bold: bool = False
    is_italic: bool = False
    bbox: list[float]  # [x0, y0, x1, y1]


class PDFDocument(BaseModel):
    """Structured representation of a PDF document."""

    title: str | None = None
    metadata: dict[str, str] = {}
    text_blocks: list[PDFTextBlock] = []
    full_text: str
    page_count: int


def extract_text_from_pdf(
    pdf_buffer: bytes, structured: bool = False
) -> str | PDFDocument | None:
    """
    Extract full text from a PDF document using PyMuPDF.

    Args:
        pdf_buffer (bytes): The PDF file content as bytes.
        structured (bool): If True, returns a structured PDFDocument object instead of plain text.

    Returns:
        Optional[Union[str, PDFDocument]]: The extracted text or document structure, or None if extraction failed.
    """
    try:
        # Open the PDF from the buffer
        with fitz.open(stream=BytesIO(pdf_buffer), filetype="pdf") as doc:
            text = []
            text_blocks = []

            # Get PDF metadata
            metadata = {
                "title": doc.metadata.get("title", ""),
                "author": doc.metadata.get("author", ""),
                "subject": doc.metadata.get("subject", ""),
                "keywords": doc.metadata.get("keywords", ""),
                "creator": doc.metadata.get("creator", ""),
                "producer": doc.metadata.get("producer", ""),
            }

            # Process each page
            for page_num, page in enumerate(doc):
                # Get plain text
                page_text = page.get_text()
                if page_text:
                    text.append(page_text)

                # If structured output is requested, collect blocks
                if structured:
                    # Extract text blocks with formatting information
                    blocks = page.get_text("dict")["blocks"]
                    for block in blocks:
                        if "lines" in block:
                            for line in block["lines"]:
                                for span in line["spans"]:
                                    text_content = span["text"].strip()
                                    if text_content:
                                        # Determine if text has formatting
                                        font_flags = span.get("flags", 0)
                                        is_bold = bool(font_flags & 2**4)  # 16 = bold
                                        is_italic = bool(
                                            font_flags & 2**0
                                        )  # 1 = italic

                                        # Guess block type based on font size
                                        font_size = span["size"]
                                        block_type = "text"
                                        if font_size > 14:
                                            block_type = "heading"

                                        text_blocks.append(
                                            PDFTextBlock(
                                                text=text_content,
                                                page_number=page_num + 1,
                                                block_type=block_type,
                                                font_size=font_size,
                                                font_name=span["font"],
                                                is_bold=is_bold,
                                                is_italic=is_italic,
                                                bbox=[
                                                    span["bbox"][0],
                                                    span["bbox"][1],
                                                    span["bbox"][2],
                                                    span["bbox"][3],
                                                ],
                                            )
                                        )

            # Combine all page texts into a single string
            full_text = "\n\n".join(text)

            # Return None if no text was extracted
            if not full_text.strip():
                logger.warning("No text content extracted from the PDF")
                return None

            # Return structured document or plain text based on the parameter
            if structured:
                # Try to identify title (typically first large text on first page)
                title = metadata.get("title", "")
                if text_blocks and not title:
                    # Find largest text in first page that's not too long
                    first_page_blocks = [b for b in text_blocks if b.page_number == 1]
                    if first_page_blocks:
                        largest_blocks = sorted(
                            first_page_blocks, key=lambda b: b.font_size, reverse=True
                        )
                        for block in largest_blocks[:3]:  # Check top 3 largest blocks
                            if len(block.text) < 200:  # Reasonable title length
                                title = block.text
                                break

                return PDFDocument(
                    title=title,
                    metadata=metadata,
                    text_blocks=text_blocks,
                    full_text=full_text,
                    page_count=len(doc),
                )
            return full_text

    except Exception as e:
        logger.exception("Failed to extract text from PDF: %s", str(e))
        return None


def extract_text_with_layout(pdf_buffer: bytes) -> str | None:
    """
    Extract text from PDF preserving layout information.

    Args:
        pdf_buffer (bytes): The PDF file content as bytes.

    Returns:
        Optional[str]: The extracted text with layout information or None if extraction failed.
    """
    try:
        with fitz.open(stream=BytesIO(pdf_buffer), filetype="pdf") as doc:
            text = []

            for page in doc:
                # "blocks" mode preserves layout better than plain text
                page_text = page.get_text("blocks")

                # Sort blocks by vertical position to maintain reading order
                # This groups text that appears at similar vertical positions
                page_text.sort(key=lambda b: (b[1], b[0]))  # Sort by y0, then x0

                # Extract text from each block
                block_text = [b[4] for b in page_text]
                text.append("\n".join(block_text))

            result = "\n\n".join(text)
            return result if result.strip() else None

    except Exception as e:
        logger.exception("Failed to extract text with layout from PDF: %s", str(e))
        return None
