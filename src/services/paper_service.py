from src.database.connection import SessionLocal
from src.database.repositories import (
    get_paper_by_url,
    create_paper,
    get_summary,
    create_summary,
)
from src.models.paper import Paper, PaperSummary

from src.models.knowledge_level import KnowledgeLevel
from src.processing.summarizer import summarize_paper
from typing import List
from src.config import logger

from sqlalchemy.orm import Session


def get_db():
    db = SessionLocal()
    try:
        logger.debug("Creating new database session.")
        yield db
    finally:
        logger.debug("Closing database session.")
        db.close()


class PaperService:
    @staticmethod
    def get_or_create_paper(db: Session, paper: Paper):
        logger.info(f"Looking up paper in DB: {paper.title}")
        db_paper = get_paper_by_url(db, paper.url)
        if not db_paper:
            logger.info(f"Paper not found, creating new entry: {paper.title}")
            db_paper = create_paper(
                db,
                {
                    "title": paper.title,
                    "abstract": paper.abstract,
                    "url": paper.url,
                    "authors": ",".join(paper.authors),
                    "published_date": paper.published_date,
                },
            )
        return db_paper

    @staticmethod
    def get_papers_and_store(db: Session, papers: List[Paper]):
        stored_papers = []
        for paper in papers:
            db_paper = PaperService.get_or_create_paper(db, paper)
            stored_paper = Paper.model_validate(db_paper)
            stored_paper.authors = db_paper.authors.split(",")
            stored_papers.append(stored_paper)
        logger.info(f"Stored {len(stored_papers)} papers in DB.")
        return stored_papers

    @staticmethod
    def get_or_create_summary(
        db: Session, db_paper, paper: Paper, knowledge_level: KnowledgeLevel
    ):
        logger.info(
            f"Checking for cached summary for paper_id={db_paper.id}, level={knowledge_level.value}"
        )

        cached = get_summary(
            db, db_paper.id, knowledge_level.value, "gemini_summarizer"
        )
        if cached:
            logger.info("Returning cached summary.")
            summary = PaperSummary(
                title=db_paper.title,
                authors=db_paper.authors.split(","),
                published_date=db_paper.published_date,
                url=db_paper.url,
                summary=cached.summary,
            )
            return summary

        logger.info("No cached summary found, generating new summary.")
        summary_obj = summarize_paper(paper, knowledge_level)
        create_summary(
            db,
            {
                "paper_id": db_paper.id,
                "knowledge_level": knowledge_level.value,
                "summarizer": "gemini_summarizer",
                "summary": summary_obj.summary,
            },
        )
        logger.info("Summary stored in DB.")
        return summary_obj
