from typing import List
import re

from fastapi import APIRouter, Query, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from src.models.paper import Paper, PaperSummary
from src.retrieval.factory import fetch_papers

from src.models.knowledge_level import KnowledgeLevel
from src.config import settings, logger
from fastapi import Depends
from sqlalchemy.orm import Session
from src.services.paper_service import get_db, PaperService


limiter = Limiter(key_func=get_remote_address)
router = APIRouter()


def validate_topic(topic: str) -> str:
    """Validate and sanitize the topic parameter."""
    if not topic or not topic.strip():
        logger.warning("Validation failed: Topic cannot be empty")
        raise HTTPException(status_code=400, detail="Topic cannot be empty")
    topic = topic.strip()
    if len(topic) > 200:
        logger.warning("Validation failed: Topic too long")
        raise HTTPException(
            status_code=400, detail="Topic must be 200 characters or less"
        )
    if not re.match(r"^[a-zA-Z0-9\s\-_.,:;()]+$", topic):
        logger.warning("Validation failed: Topic contains invalid characters")
        raise HTTPException(
            status_code=400,
            detail="Topic contains invalid characters. Use letters, numbers, spaces, and basic punctuation.",
        )
    return topic


def validate_source(source: str) -> str:
    """Validate and sanitize the source parameter."""
    if not source or not source.strip():
        logger.warning("Validation failed: Source cannot be empty")
        raise HTTPException(status_code=400, detail="Source cannot be empty")
    source = source.strip().lower()
    if not re.match(r"^[a-zA-Z0-9_]+$", source):
        logger.warning("Validation failed: Source contains invalid characters")
        raise HTTPException(
            status_code=400,
            detail="Source contains invalid characters. Only letters, numbers, and underscores are allowed",
        )
    return source


@router.get("/papers", response_model=List[Paper])
@limiter.limit(f"{settings.RATE_LIMIT_REQUESTS_PER_MINUTE}/minute")
@limiter.limit(f"{settings.RATE_LIMIT_REQUESTS_PER_HOUR}/hour")
def get_papers(
    request: Request,
    topic: str = Query(
        ...,
        description="The research topic to search for.",
        min_length=1,
        max_length=200,
    ),
    max_results: int = Query(
        5, description="Maximum number of papers to retrieve", ge=1, le=10
    ),
    source: str = Query(
        "arxiv",
        description="Source of research papers (e.g. 'arxiv')",
        min_length=1,
        max_length=50,
    ),
    db: Session = Depends(get_db),
):
    """
    Retrieve recent research papers from the specified source.
    Store them in the database if not already present.
    """
    topic = validate_topic(topic)
    source = validate_source(source)

    try:
        logger.info(
            f"Fetching papers for topic='{topic}', max_results={max_results}, source='{source}'"
        )
        papers = fetch_papers(topic, max_results=max_results, source=source)
        result = PaperService.get_papers_and_store(db, papers)
        logger.info(f"Fetched and stored {len(result)} papers.")
        return result
    except ValueError as e:
        logger.error(f"ValueError in get_papers: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f"Unexpected error in get_papers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/summarize", response_model=PaperSummary)
@limiter.limit(f"{settings.RATE_LIMIT_REQUESTS_PER_MINUTE}/minute")
@limiter.limit(f"{settings.RATE_LIMIT_REQUESTS_PER_HOUR}/hour")
def summarize_paper(
    request: Request,
    paper: Paper,
    knowledge_level: KnowledgeLevel = Query(
        KnowledgeLevel.GENERAL,
        description="Knowledge level: general, undergraduate, or researcher/professional",
    ),
    db: Session = Depends(get_db),
) -> PaperSummary:
    """
    Summarize a research paper based on the user's knowledge level.
    Cache the summary in the database.
    """
    try:
        logger.info(
            f"Summarizing paper '{paper.title}' for knowledge_level='{knowledge_level}'"
        )
        db_paper = PaperService.get_or_create_paper(db, paper)
        summary = PaperService.get_or_create_summary(
            db, db_paper, paper, knowledge_level
        )
        logger.info(f"Summary created for paper '{paper.title}'")
        return summary
    except ValueError as e:
        logger.error(f"ValueError in summarize_paper: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f"Unexpected error in summarize_paper: {e}")
        raise HTTPException(status_code=500, detail=str(e))
