from src.models.paper import Paper, PaperSummary
from src.models.knowledge_level import KnowledgeLevel
from fastapi.testclient import TestClient
from unittest.mock import patch
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
from src.main import app  # noqa: E402

client = TestClient(app)


@patch("src.api.routes.PaperService.get_or_create_paper")
@patch("src.api.routes.PaperService.get_or_create_summary")
def test_summarize_success(mock_get_summary, mock_get_paper):
    paper_data = {
        "title": "Test Paper",
        "abstract": "Test abstract",
        "url": "http://arxiv.org/abs/1234.5678",
        "authors": ["Alice", "Bob"],
        "published_date": "2023-01-01",
    }
    summary_data = paper_data.copy()
    summary_data["summary"] = "Short summary."
    mock_get_paper.return_value = Paper(**paper_data)
    mock_get_summary.return_value = PaperSummary(**summary_data)
    response = client.post(
        "/api/summarize",
        params={"knowledge_level": KnowledgeLevel.GENERAL.value},
        json=paper_data,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Paper"
    assert data["summary"] == "Short summary."


def test_summarize_missing_field():
    # Missing 'title'
    paper_data = {
        "abstract": "Test abstract",
        "url": "http://arxiv.org/abs/1234.5678",
        "authors": ["Alice", "Bob"],
        "published_date": "2023-01-01",
    }
    response = client.post("/api/summarize", json=paper_data)
    assert response.status_code == 422


def test_summarize_invalid_knowledge_level():
    paper_data = {
        "title": "Test Paper",
        "abstract": "Test abstract",
        "url": "http://arxiv.org/abs/1234.5678",
        "authors": ["Alice", "Bob"],
        "published_date": "2023-01-01",
    }
    response = client.post(
        "/api/summarize", params={"knowledge_level": "invalid"}, json=paper_data
    )
    assert response.status_code == 422


@patch("src.api.routes.PaperService.get_or_create_paper")
@patch(
    "src.api.routes.PaperService.get_or_create_summary",
    side_effect=ValueError("bad value"),
)
def test_summarize_value_error(mock_get_summary, mock_get_paper):
    paper_data = {
        "title": "Test Paper",
        "abstract": "Test abstract",
        "url": "http://arxiv.org/abs/1234.5678",
        "authors": ["Alice", "Bob"],
        "published_date": "2023-01-01",
    }
    mock_get_paper.return_value = Paper(**paper_data)
    response = client.post("/api/summarize", json=paper_data)
    assert response.status_code == 400
    assert "bad value" in response.text


@patch("src.api.routes.PaperService.get_or_create_paper")
@patch(
    "src.api.routes.PaperService.get_or_create_summary",
    side_effect=Exception("unexpected error"),
)
def test_summarize_generic_exception(mock_get_summary, mock_get_paper):
    paper_data = {
        "title": "Test Paper",
        "abstract": "Test abstract",
        "url": "http://arxiv.org/abs/1234.5678",
        "authors": ["Alice", "Bob"],
        "published_date": "2023-01-01",
    }
    mock_get_paper.return_value = Paper(**paper_data)
    response = client.post("/api/summarize", json=paper_data)
    assert response.status_code == 500
    assert "unexpected error" in response.text
