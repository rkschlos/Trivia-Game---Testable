from pydantic import BaseModel
from .clues import ClueOut


class CustomGameOut(BaseModel):
    id: str
    created_on: str
    clues: list[ClueOut]
