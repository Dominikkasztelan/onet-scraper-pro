import scrapy
from pydantic import BaseModel, field_validator
from typing import Optional

class ArticleItem(BaseModel):
    title: str
    url: str
    date: str
    lead: Optional[str] = None

    @field_validator('title')
    def clean_title(cls, v):
        if not v:
            raise ValueError("Tytuł jest pusty!")
        return v.strip()

    @field_validator('url')
    def validate_url(cls, v):
        if not v.startswith('http'):
            raise ValueError("Niepoprawny URL")
        return v