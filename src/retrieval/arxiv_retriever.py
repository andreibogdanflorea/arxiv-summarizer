from src.retrieval.base import PaperSource
import arxiv
from typing import List
from src.models.paper import Paper


class ArxivSource(PaperSource):
    def fetch_papers(self, topic: str, max_results: int = 5) -> List[Paper]:
        """
        Fetches recent papers from arXiv matching the topic.
        """
        search = arxiv.Search(
            query=topic,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending,
        )

        papers = []
        for result in search.results():
            paper = Paper(
                title=result.title,
                abstract=result.summary.strip().replace("\n", " "),
                url=result.entry_id,
                authors=[author.name for author in result.authors],
                published_date=result.published.strftime("%Y-%m-%d"),
            )
            papers.append(paper)

        return papers
