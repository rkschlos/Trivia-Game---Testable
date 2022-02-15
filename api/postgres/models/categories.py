from pydantic import BaseModel


class CategoryIn(BaseModel):
    title: str


class CategoryOut(BaseModel):
    id: int
    title: str
    canon: bool


class CategoryOutWithClueCount(CategoryOut):
    num_clues: int


class CategoryList(BaseModel):
    page_count: int
    categories: list[CategoryOutWithClueCount]


class CategoryDeleteOperation(BaseModel):
    result: bool
