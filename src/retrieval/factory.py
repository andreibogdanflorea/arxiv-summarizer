from typing import List

from src.models.paper import Paper
from src.retrieval.arxiv_retriever import ArxivSource


SOURCES = {
    "arxiv": ArxivSource(),
}

def fetch_papers(topic: str, max_results: int = 5, source: str = "arxiv") -> List[Paper]:
    if source not in SOURCES:
        raise ValueError(f"Unknown source '{source}'")

    return SOURCES[source].fetch_papers(topic, max_results)