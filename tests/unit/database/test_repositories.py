import pytest
from unittest.mock import MagicMock
from src.database.repositories import (
    get_paper_by_url,
    create_paper,
    get_summary,
    create_summary,
)


class FakePaper:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class FakeSummary:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


@pytest.fixture
def fake_db():
    db = MagicMock()
    db.query().filter().first.return_value = None
    return db


def test_get_paper_by_url_found():
    db = MagicMock()
    fake_paper = FakePaper(url="http://arxiv.org/abs/1234.5678")
    db.query().filter().first.return_value = fake_paper
    result = get_paper_by_url(db, "http://arxiv.org/abs/1234.5678")
    assert result == fake_paper


def test_get_paper_by_url_not_found():
    db = MagicMock()
    db.query().filter().first.return_value = None
    result = get_paper_by_url(db, "notfound")
    assert result is None


def test_create_paper():
    db = MagicMock()
    paper_data = {
        "title": "Test",
        "abstract": "A",
        "url": "u",
        "authors": "A,B",
        "published_date": "2023",
    }
    db.add.return_value = None
    db.commit.return_value = None
    db.refresh.return_value = None
    create_paper(db, paper_data)
    db.add.assert_called()
    db.commit.assert_called()


def test_get_summary_found():
    db = MagicMock()
    fake_summary = FakeSummary(summary="s")
    db.query().filter().first.return_value = fake_summary
    result = get_summary(db, 1, "general", "gemini_summarizer")
    assert result == fake_summary


def test_get_summary_not_found():
    db = MagicMock()
    db.query().filter().first.return_value = None
    result = get_summary(db, 1, "general", "gemini_summarizer")
    assert result is None


def test_create_summary():
    db = MagicMock()
    summary_data = {
        "paper_id": 1,
        "knowledge_level": "general",
        "summarizer": "gemini_summarizer",
        "summary": "s",
    }
    db.add.return_value = None
    db.commit.return_value = None
    db.refresh.return_value = None
    create_summary(db, summary_data)
    db.add.assert_called()
    db.commit.assert_called()
