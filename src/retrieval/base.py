from abc import ABC, abstractmethod
from typing import List
from src.models.paper import Paper

class PaperSource(ABC):

    @abstractmethod
    def fetch_papers(self, topic: str, max_results: int = 5) -> List[Paper]:
        pass
