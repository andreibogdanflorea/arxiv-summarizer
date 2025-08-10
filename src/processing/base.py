from abc import ABC, abstractmethod
from typing import List

from src.models.paper import Paper, PaperSummary
from src.models.knowledge_level import KnowledgeLevel


class AbstractSummarizer(ABC):
    @abstractmethod
    def summarize(self, papers: List[Paper], level: KnowledgeLevel) -> List[PaperSummary]:
        pass
