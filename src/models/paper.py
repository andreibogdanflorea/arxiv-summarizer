from pydantic import BaseModel, field_validator, ConfigDict
from typing import List, Any


class Paper(BaseModel):
    title: str
    abstract: str
    url: str
    authors: List[str]
    published_date: str

    @field_validator("authors", mode="before")
    @classmethod
    def split_authors(cls, v: Any) -> List[str]:
        if isinstance(v, str):
            return [a.strip() for a in v.split(",") if a.strip()]
        return v

    model_config = ConfigDict(from_attributes=True)


class PaperSummary(BaseModel):
    title: str
    authors: List[str]
    published_date: str
    summary: str
    url: str

    @field_validator("authors", mode="before")
    @classmethod
    def split_authors(cls, v: Any) -> List[str]:
        if isinstance(v, str):
            return [a.strip() for a in v.split(",") if a.strip()]
        return v

    model_config = ConfigDict(from_attributes=True)
