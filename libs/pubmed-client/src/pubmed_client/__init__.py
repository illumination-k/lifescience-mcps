def hello() -> str:
    return "Hello from pubmed-client!"


from .search import search_pubmed
from .client import PubMedClient
