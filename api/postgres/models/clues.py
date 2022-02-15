from typing import Union
from pydantic import BaseModel
from .categories import CategoryOut


class ClueOut(BaseModel):
    id: int
    answer: str
    question: str
    value: int
    invalid_count: Union[int, None]
    canon: bool
    category: CategoryOut


class ClueList(BaseModel):
    page_count: int
    clues: list[ClueOut]
