from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class RetrieveRequest(BaseModel):
    query: str = Field(min_length=3, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=20)

    @field_validator("query")
    @classmethod
    def query_must_not_be_blank(cls, value: str):
        if not value.strip():
            raise ValueError("query must not be blank")
        return value.strip()


class RetrievalHit(BaseModel):
    document_id: str
    score: float
    title: str
    excerpt: str


class RetrieveResponse(BaseModel):
    query: str
    hits: list[RetrievalHit]
    latency_ms: float
    backend: str = "public-demo-bm25"


class FuseRequest(BaseModel):
    rankings: list[list[str]] = Field(min_length=1, max_length=32)
    weights: list[float] | None = None
    limits: list[int] | None = None
    rrf_k: float = Field(default=3.0, ge=0.0, le=1000.0)
    top_k: int = Field(default=5, ge=1, le=150)

    @field_validator("rankings")
    @classmethod
    def rankings_must_not_be_empty(cls, value: list[list[str]]):
        if any(not ranking for ranking in value):
            raise ValueError("each ranking must contain at least one document")
        return value


class FuseResponse(BaseModel):
    documents: list[str]
