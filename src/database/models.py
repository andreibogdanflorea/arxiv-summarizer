from src.database import Base
from sqlalchemy import Column, Integer, String, TIMESTAMP, text
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey


class Paper(Base):
    __tablename__ = "papers"

    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    abstract = Column(String, nullable=False)
    url = Column(String, nullable=False, unique=True)
    authors = Column(String, nullable=False)  # Comma-separated list
    published_date = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"))
    summaries = relationship("Summary", back_populates="paper")


class Summary(Base):
    __tablename__ = "summaries"

    id = Column(Integer, primary_key=True, nullable=False)
    paper_id = Column(Integer, ForeignKey("papers.id"), nullable=False)
    knowledge_level = Column(String, nullable=False)
    summarizer = Column(String, nullable=False)
    summary = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"))
    paper = relationship("Paper", back_populates="summaries")
