"""
Main entry point for the Cellosaurus MCP server.
"""

import logging

from .server import serve

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    serve()
