from pydantic import BaseModel
from .clues import ClueOut


class CustomGameOut(BaseModel):
    id: int
    created_on: str
    clues: list[ClueOut]
