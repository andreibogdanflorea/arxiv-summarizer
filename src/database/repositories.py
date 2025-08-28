from sqlalchemy.orm import Session
from src.database.models import Paper, Summary

def get_paper_by_url(db: Session, url: str):
	return db.query(Paper).filter(Paper.url == url).first()

def create_paper(db: Session, paper_data: dict):
	db_paper = Paper(**paper_data)
	db.add(db_paper)
	db.commit()
	db.refresh(db_paper)
	return db_paper

def get_summary(db: Session, paper_id: int, knowledge_level: str, summarizer: str):
	return db.query(Summary).filter(
		Summary.paper_id == paper_id,
		Summary.knowledge_level == knowledge_level,
		Summary.summarizer == summarizer
	).first()

def create_summary(db: Session, summary_data: dict):
	db_summary = Summary(**summary_data)
	db.add(db_summary)
	db.commit()
	db.refresh(db_summary)
	return db_summary
