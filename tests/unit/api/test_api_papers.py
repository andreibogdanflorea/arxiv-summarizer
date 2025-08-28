from fastapi.testclient import TestClient
from unittest.mock import patch
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
from src.main import app  # noqa: E402


client = TestClient(app)


@patch("src.api.routes.fetch_papers")
@patch("src.api.routes.PaperService.get_papers_and_store")
def test_get_papers_success(mock_get_papers_and_store, mock_fetch_papers):
    mock_papers = [
        {
            "title": "Test Paper",
            "abstract": "Test abstract",
            "url": "http://arxiv.org/abs/1234.5678",
            "authors": ["Alice", "Bob"],
            "published_date": "2023-01-01",
        }
    ]
    mock_fetch_papers.return_value = mock_papers
    mock_get_papers_and_store.return_value = mock_papers
    response = client.get(
        "/api/papers", params={"topic": "AI", "max_results": 1, "source": "arxiv"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["title"] == "Test Paper"


def test_get_papers_empty_topic():
    response = client.get(
        "/api/papers", params={"topic": "", "max_results": 1, "source": "arxiv"}
    )
    assert response.status_code == 422


def test_get_papers_whitespace_topic():
    response = client.get(
        "/api/papers", params={"topic": "   ", "max_results": 1, "source": "arxiv"}
    )
    assert response.status_code == 400
    assert "Topic cannot be empty" in response.text


def test_get_papers_topic_too_long():
    long_topic = "A" * 201
    response = client.get(
        "/api/papers", params={"topic": long_topic, "max_results": 1, "source": "arxiv"}
    )
    assert response.status_code == 422


def test_get_papers_topic_invalid_chars():
    response = client.get(
        "/api/papers", params={"topic": "AI!@#", "max_results": 1, "source": "arxiv"}
    )
    assert response.status_code == 400
    assert "Topic contains invalid characters" in response.text


def test_get_papers_invalid_source():
    response = client.get(
        "/api/papers", params={"topic": "AI", "max_results": 1, "source": "bad source!"}
    )
    assert response.status_code == 400
    assert "Source contains invalid characters" in response.text


def test_get_papers_max_results_too_low():
    response = client.get(
        "/api/papers", params={"topic": "AI", "max_results": 0, "source": "arxiv"}
    )
    assert response.status_code == 422


def test_get_papers_max_results_too_high():
    response = client.get(
        "/api/papers", params={"topic": "AI", "max_results": 11, "source": "arxiv"}
    )
    assert response.status_code == 422


@patch("src.api.routes.fetch_papers", side_effect=ValueError("bad value"))
def test_get_papers_value_error(mock_fetch_papers):
    response = client.get(
        "/api/papers", params={"topic": "AI", "max_results": 1, "source": "arxiv"}
    )
    assert response.status_code == 400
    assert "bad value" in response.text


@patch("src.api.routes.fetch_papers", side_effect=Exception("unexpected error"))
def test_get_papers_generic_exception(mock_fetch_papers):
    response = client.get(
        "/api/papers", params={"topic": "AI", "max_results": 1, "source": "arxiv"}
    )
    assert response.status_code == 500
    assert "unexpected error" in response.text
