# Cellosaurus MCP

This package provides a Model Context Protocol (MCP) server for interfacing with the [Cellosaurus](https://www.cellosaurus.org/) cell line database API.

## Features

- Search for cell lines using the Cellosaurus query syntax
- Get detailed information about specific cell lines by accession number
- Support for field filtering and pagination

## Installation

```bash
pip install cellosaurus-mcp
```

## Usage

### Starting the MCP Server

```bash
python -m cellosaurus_mcp.server
```

### API Tools

#### cellosaurus_search

Search for cell lines in the Cellosaurus database using various criteria.

Example queries:

- `ox:sapiens` (human cell lines)
- `derived-from-site:liver` (cell lines from liver)
- `di:Hepatoblastoma` (cell lines from hepatoblastoma patients)
- `category:"Cancer cell line"` (cancer cell lines)

#### cellosaurus_get_cell_line

Get detailed information about a specific cell line by its accession number (e.g., "CVCL_0030" for HeLa).

## Development

### Testing

Run tests with:

```bash
mise r test
```

## License

This project is licensed under the terms specified in the repository.
