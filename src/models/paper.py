from pydantic import BaseModel
from typing import List


class Paper(BaseModel):
    title: str
    abstract: str
    url: str
    authors: List[str]
    published_date: str


class PaperSummary(BaseModel):
    title: str
    authors: List[str]
    published_date: str
    summary: str
    url: str
