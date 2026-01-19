from pydantic import BaseModel, field_validator


class ArticleItem(BaseModel):
    title: str
    url: str
    date: str  # Kept as str to match scraped format, could be datetime in future
    lead: str | None = None
    content: str | None = None

    # New production fields
    author: str | None = None
    keywords: str | None = None
    section: str | None = None
    date_modified: str | None = None
    image_url: str | None = None
    id: str | None = None
    read_time: int | None = None  # in minutes

    @field_validator("title")
    def clean_title(cls, v):
        if not v:
            raise ValueError("Tytuł jest pusty!")
        v = v.strip()
        if not v:
            raise ValueError("Tytuł jest pusty!")
        return v

    @field_validator("url")
    def validate_url(cls, v):
        if not v.startswith("http"):
            raise ValueError("Niepoprawny URL")
        return v
