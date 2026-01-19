from pydantic import BaseModel, field_validator
from typing import Optional

class ArticleItem(BaseModel):
    title: str
    url: str
    date: str
    lead: Optional[str] = None
    content: Optional[str] = None
    
    # New production fields
    author: Optional[str] = None
    keywords: Optional[str] = None
    section: Optional[str] = None
    date_modified: Optional[str] = None
    image_url: Optional[str] = None
    id: Optional[str] = None
    read_time: Optional[int] = None # in minutes

    @field_validator('title')
    def clean_title(cls, v):
        if not v:
            raise ValueError("Tytuł jest pusty!")
        v = v.strip()
        if not v:
            raise ValueError("Tytuł jest pusty!")
        return v

    @field_validator('url')
    def validate_url(cls, v):
        if not v.startswith('http'):
            raise ValueError("Niepoprawny URL")
        return v