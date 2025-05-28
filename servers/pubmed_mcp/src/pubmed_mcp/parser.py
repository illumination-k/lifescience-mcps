import logging

import defusedxml.ElementTree as ET  # noqa: N817

from .models import Author, Journal, PubMedArticle, PubMedArticleResult

logger = logging.getLogger(__name__)


def parse_pubmed_xml(xml_data: str) -> PubMedArticleResult:  # noqa: C901,PLR0912,PLR0915
    """
    Parse PubMed XML data into structured PubMedArticle objects.

    Args:
        xml_data (str): XML data from the PubMed API.

    Returns:
        PubMedArticleResult: A Pydantic model containing a list of PubMedArticle objects with structured metadata.
    """
    try:
        root = ET.fromstring(xml_data)
        articles = []

        # Find all PubMed articles in the XML
        for article_element in root.findall(".//PubmedArticle"):
            # Extract PMID - required field
            pmid_element = article_element.find(".//PMID")
            if pmid_element is None or not pmid_element.text:
                continue  # Skip articles without PMID

            pmid = pmid_element.text

            # Extract PMC ID if available
            pmc_id = None
            article_id_elements = article_element.findall(".//ArticleId")
            for article_id_element in article_id_elements:
                if (
                    article_id_element.attrib.get("IdType") == "pmc"
                    and article_id_element.text
                ):
                    pmc_id = article_id_element.text
                    break

            # Extract article title
            title = None
            title_element = article_element.find(".//ArticleTitle")
            if title_element is not None:
                title = title_element.text

            # Extract abstract
            abstract = None
            abstract_elements = article_element.findall(".//AbstractText")
            if abstract_elements:
                abstract_text = " ".join(
                    [elem.text for elem in abstract_elements if elem.text]
                )
                abstract = abstract_text

            # Extract journal information
            journal = None
            journal_element = article_element.find(".//Journal")
            if journal_element is not None:
                journal_title = None
                journal_iso = None
                pub_date = None

                # Journal title
                title_elem = journal_element.find(".//Title")
                if title_elem is not None:
                    journal_title = title_elem.text

                # Journal ISO abbreviation
                iso_elem = journal_element.find(".//ISOAbbreviation")
                if iso_elem is not None:
                    journal_iso = iso_elem.text

                # Publication date
                pub_date_elem = journal_element.find(".//PubDate")
                if pub_date_elem is not None:
                    year = pub_date_elem.find("Year")
                    month = pub_date_elem.find("Month")
                    day = pub_date_elem.find("Day")

                    date_parts = []
                    if year is not None and year.text:
                        date_parts.append(year.text)
                    if month is not None and month.text:
                        date_parts.append(month.text)
                    if day is not None and day.text:
                        date_parts.append(day.text)

                    if date_parts:
                        pub_date = " ".join(date_parts)

                journal = Journal(
                    title=journal_title,
                    iso_abbreviation=journal_iso,
                    pub_date=pub_date,
                )

            # Extract authors
            authors = []
            author_elements = article_element.findall(".//Author")
            for author in author_elements:
                last_name = None
                fore_name = None
                initials = None

                last_name_elem = author.find("LastName")
                if last_name_elem is not None and last_name_elem.text:
                    last_name = last_name_elem.text

                fore_name_elem = author.find("ForeName")
                if fore_name_elem is not None and fore_name_elem.text:
                    fore_name = fore_name_elem.text

                initials_elem = author.find("Initials")
                if initials_elem is not None and initials_elem.text:
                    initials = initials_elem.text

                # Only create Author if we have at least one piece of information
                if any([last_name, fore_name, initials]):
                    authors.append(
                        Author(
                            last_name=last_name,
                            fore_name=fore_name,
                            initials=initials,
                        )
                    )

            # Create PubMedArticle object
            article = PubMedArticle(
                pmid=pmid,
                pmc_id=pmc_id,
                title=title,
                abstract=abstract,
                journal=journal,
                authors=authors,
            )

            articles.append(article)

        return PubMedArticleResult(articles=articles)

    except ET.ParseError as e:
        logger.exception("Failed to parse PubMed XML data")
        msg = "Failed to parse PubMed XML data."
        raise RuntimeError(msg) from e


def parse_pmc_fulltext_xml(xml_data: str) -> str:
    """
    Extract full text content from PMC XML data.

    Args:
        xml_data (str): XML data from the PMC API.

    Returns:
        str: The full text content of the article.

    Raises:
        RuntimeError: If parsing fails or no text content is found.
    """
    try:
        root = ET.fromstring(xml_data)

        # Extract all text from the article body
        text_sections = []

        # Get the title
        title_elements = root.findall(".//article-title")
        if title_elements:
            for title_elem in title_elements:
                if title_elem.text:
                    text_sections.append(title_elem.text)

        # Get the abstract
        abstract_elements = root.findall(".//abstract//p")
        for abstract_elem in abstract_elements:
            if abstract_elem.text:
                text_sections.append(abstract_elem.text)

        # Get all paragraphs from the main text
        body_paragraphs = root.findall(".//body//p")
        for para in body_paragraphs:
            # Recursively extract text from this paragraph and its children
            para_text = "".join(para.itertext()).strip()
            if para_text:
                text_sections.append(para_text)

        # If we found any content, return it
        if text_sections:
            return "\n\n".join(text_sections)

        # If we get here, we didn't find any content
        raise RuntimeError("No text content found in PMC XML")

    except ET.ParseError as e:
        logger.exception("Failed to parse PMC XML data")
        msg = "Failed to parse PMC XML data."
        raise RuntimeError(msg) from e
