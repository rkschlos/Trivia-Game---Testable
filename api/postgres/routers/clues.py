from fastapi import APIRouter, Depends, Response, status
from typing import Union
from ..models.clues import ClueOut, ClueList
from ..models.common import ErrorMessage
from ..db import ClueQueries


router = APIRouter()


def row_to_clue(row):
    return {
        "id": row[0],
        "answer": row[1],
        "question": row[2],
        "value": row[3],
        "invalid_count": row[4],
        "canon": row[5],
        "category": {
            "id": row[6],
            "title": row[7],
            "canon": row[8],
        },
    }


@router.get(
    "/api/postgres/clues/random-clue",
    response_model=ClueOut,
)
def get_random_clue(query=Depends(ClueQueries)):
    row = query.get_random_clue()
    return row_to_clue(row)


@router.get(
    "/api/postgres/clues/{clue_id}",
    response_model=Union[ClueOut, ErrorMessage],
    responses={
        200: {"model": ClueOut},
        404: {"model": ErrorMessage},
    },
)
def get_clue(clue_id: int, response: Response, query=Depends(ClueQueries)):
    row = query.get_clue(clue_id)
    if row is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Clue not found"}
    return row_to_clue(row)


@router.get(
    "/api/postgres/clues",
    response_model=ClueList,
)
def get_clues(page: int = 0, value: int = 0, query=Depends(ClueQueries)):
    page_count, rows = query.get_all_clues(page, value)
    return {"page_count": page_count, "clues": [row_to_clue(row) for row in rows]}


@router.delete(
    "/api/postgres/clues/{clue_id}",
    response_model=Union[ClueOut, ErrorMessage],
    responses={
        200: {"model": ClueOut},
        404: {"model": ErrorMessage},
    },
)
def increment_invalid_count(
    clue_id: int,
    response: Response,
    query=Depends(ClueQueries),
):
    row = query.increment_invalid_count(clue_id)
    if row is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Clue not found"}
    return row_to_clue(row)
