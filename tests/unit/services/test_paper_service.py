from types import SimpleNamespace
import pytest
from unittest.mock import MagicMock, patch
from src.services.paper_service import PaperService
from src.models.paper import Paper, PaperSummary
from src.models.knowledge_level import KnowledgeLevel


@pytest.fixture
def fake_db():
    return MagicMock()


@pytest.fixture
def fake_paper():
    return Paper(
        title="Test Paper",
        abstract="Test abstract",
        url="http://arxiv.org/abs/1234.5678",
        authors=["Alice", "Bob"],
        published_date="2023-01-01",
    )


fake_db_paper = SimpleNamespace(
    id=1,
    title="Test Paper",
    abstract="Test abstract",
    url="http://arxiv.org/abs/1234.5678",
    authors="Alice,Bob",
    published_date="2023-01-01",
)

fake_cached = SimpleNamespace(
    id=1,
    title="Test Paper",
    abstract="Test abstract",
    url="http://arxiv.org/abs/1234.5678",
    authors="Alice,Bob",
    published_date="2023-01-01",
    summary="Cached summary",
)


def test_get_or_create_paper_creates_new(fake_db, fake_paper):
    with (
        patch("src.services.paper_service.get_paper_by_url", return_value=None),
        patch("src.services.paper_service.create_paper", return_value=fake_db_paper),
    ):
        result = PaperService.get_or_create_paper(fake_db, fake_paper)
        assert result == fake_db_paper


def test_get_or_create_paper_returns_existing(fake_db, fake_paper):
    with patch(
        "src.services.paper_service.get_paper_by_url", return_value=fake_db_paper
    ):
        result = PaperService.get_or_create_paper(fake_db, fake_paper)
        assert result == fake_db_paper


def test_get_papers_and_store(fake_db, fake_paper):
    with patch.object(PaperService, "get_or_create_paper", return_value=fake_db_paper):
        papers = [fake_paper]
        result = PaperService.get_papers_and_store(fake_db, papers)
        assert isinstance(result, list)
        assert result[0].title == fake_paper.title
        assert result[0].authors == ["Alice", "Bob"]


def test_get_or_create_summary_cached(fake_db, fake_paper):
    with patch("src.services.paper_service.get_summary", return_value=fake_cached):
        result = PaperService.get_or_create_summary(
            fake_db, fake_db_paper, fake_paper, KnowledgeLevel.GENERAL
        )
        assert isinstance(result, PaperSummary)
        assert result.summary == "Cached summary"
        assert result.authors == ["Alice", "Bob"]


def test_get_or_create_summary_new(fake_db, fake_paper):
    fake_summary_obj = PaperSummary(
        title=fake_paper.title,
        authors=fake_paper.authors,
        published_date=fake_paper.published_date,
        url=fake_paper.url,
        summary="Generated summary",
    )
    with (
        patch("src.services.paper_service.get_summary", return_value=None),
        patch(
            "src.services.paper_service.summarize_paper", return_value=fake_summary_obj
        ),
        patch("src.services.paper_service.create_summary") as mock_create_summary,
    ):
        result = PaperService.get_or_create_summary(
            fake_db, fake_db_paper, fake_paper, KnowledgeLevel.GENERAL
        )
        assert result == fake_summary_obj
        mock_create_summary.assert_called_once()
