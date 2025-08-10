from typing import List
import re

from fastapi import APIRouter, Query, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from src.models.paper import Paper, PaperSummary
from src.processing.summarizer import summarize_paper
from src.retrieval.factory import fetch_papers
from src.models.knowledge_level import KnowledgeLevel
from src.config import settings


limiter = Limiter(key_func=get_remote_address)
router = APIRouter()


def validate_topic(topic: str) -> str:
    """Validate and sanitize the topic parameter."""
    if not topic or not topic.strip():
        raise HTTPException(status_code=400, detail="Topic cannot be empty")
    
    topic = topic.strip()
    if len(topic) > 200:
        raise HTTPException(status_code=400, detail="Topic must be 200 characters or less")

    if not re.match(r'^[a-zA-Z0-9\s\-_.,:;()]+$', topic):
        raise HTTPException(
            status_code=400, 
            detail="Topic contains invalid characters. Only letters, numbers, spaces, and basic punctuation are allowed"
        )
    
    return topic


def validate_max_results(max_results: int) -> int:
    """Validate the max_results parameter."""
    if max_results < 1:
        raise HTTPException(status_code=400, detail="max_results must be at least 1")
    
    if max_results > 10:
        raise HTTPException(status_code=400, detail="max_results cannot exceed 50")
    
    return max_results


def validate_source(source: str) -> str:
    """Validate and sanitize the source parameter."""
    if not source or not source.strip():
        raise HTTPException(status_code=400, detail="Source cannot be empty")
    
    source = source.strip().lower()

    if not re.match(r'^[a-zA-Z0-9_]+$', source):
        raise HTTPException(
            status_code=400, 
            detail="Source contains invalid characters. Only letters, numbers, and underscores are allowed"
        )
    
    return source


@router.get("/papers", response_model=List[Paper])
@limiter.limit(f"{settings.RATE_LIMIT_REQUESTS_PER_MINUTE}/minute")
@limiter.limit(f"{settings.RATE_LIMIT_REQUESTS_PER_HOUR}/hour")
def get_papers(
    request: Request,
    topic: str = Query(..., description="The research topic to search for.", min_length=1, max_length=200),
    max_results: int = Query(5, description="Maximum number of papers to retrieve", ge=1, le=10),
    source: str = Query("arxiv", description="Source of research papers (e.g. 'arxiv')", min_length=1, max_length=50)
):
    """
    Retrieve recent research papers from the specified source.
    """
    topic = validate_topic(topic)
    max_results = validate_max_results(max_results)
    source = validate_source(source)
    
    try:
        papers = fetch_papers(topic, max_results=max_results, source=source)
        return papers
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while processing your request")


@router.post("/summarize", response_model=PaperSummary)
@limiter.limit(f"{settings.RATE_LIMIT_REQUESTS_PER_MINUTE}/minute")
@limiter.limit(f"{settings.RATE_LIMIT_REQUESTS_PER_HOUR}/hour")
def summarize_paper_endpoint(
    request: Request,
    paper: Paper,
    knowledge_level: KnowledgeLevel = Query(
        KnowledgeLevel.GENERAL,
        description="Knowledge level: general, undergraduate, or researcher/professional"
    )
) -> PaperSummary:
    """
    Summarize a research paper based on the user's knowledge level.
    """
    try:
        summary = summarize_paper(paper, knowledge_level)
        return summary
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while processing your request")
