from typing import Any, List

from pydantic import BaseModel


class AnnotateRequest(BaseModel):
    text: str


class AnnotateResponse(BaseModel):
    annotated_text: str


class MatchRecord(BaseModel):
    aya_name: str
    verses: List[str]
    errors: Any  # You can refine this type later, e.g. List[str] or Dict[str, Any]
    startInText: int
    endInText: int


class MatchResponse(BaseModel):
    records: List[MatchRecord]
