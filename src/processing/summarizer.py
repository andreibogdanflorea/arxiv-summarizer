from typing import List
from enum import Enum

from src.processing.prompts import build_prompt
from src.processing.gemini_summarizer import GeminiSummarizer
from src.models.paper import Paper, PaperSummary
from src.models.knowledge_level import KnowledgeLevel


class Summarizer(str, Enum):
    GEMINI_SUMMARIZER = "gemini_summarizer"


def summarize_paper(
    paper: Paper,
    level: KnowledgeLevel,
    summarizer: Summarizer = Summarizer.GEMINI_SUMMARIZER
) -> PaperSummary:
    if summarizer == Summarizer.GEMINI_SUMMARIZER:
        summarizer = GeminiSummarizer()
    else:
        raise ValueError(f"Unsupported summarizer: {summarizer}")

    prompt = build_prompt(paper.abstract, level)
    summary = summarizer.summarize(prompt)

    return PaperSummary(
        title=paper.title,
        authors=paper.authors,
        published_date=paper.published_date,
        url=paper.url,
        summary=summary,
    )
