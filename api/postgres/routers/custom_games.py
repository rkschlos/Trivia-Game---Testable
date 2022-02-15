from typing import Union
from fastapi import APIRouter, Depends, Response, status
from ..db import CustomGameQueries
from ..models.custom_games import CustomGameOut
from ..models.common import ErrorMessage
from .clues import row_to_clue


router = APIRouter()


def rows_to_custom_game(rows):
    first_row = rows[0]
    return {
        "id": first_row[-2],
        "created_on": str(first_row[-1]),
        "clues": [row_to_clue(row) for row in rows],
    }


@router.post(
    "/api/postgres/custom-games",
    response_model=Union[CustomGameOut, ErrorMessage],
    responses={
        200: {"model": CustomGameOut},
        500: {"model": ErrorMessage},
    },
)
def create_custom_game(query=Depends(CustomGameQueries)):
    rows = query.create()
    return rows_to_custom_game(rows)


@router.get(
    "/api/postgres/custom-games/{custom_game_id}",
    response_model=Union[CustomGameOut, ErrorMessage],
    responses={
        200: {"model": CustomGameOut},
        404: {"model": ErrorMessage},
    },
)
def create_custom_game(
    custom_game_id: int,
    response: Response,
    query=Depends(CustomGameQueries),
):
    rows = query.get_custom_game(custom_game_id)
    if len(rows) == 0:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Custom game not found"}
    return rows_to_custom_game(rows)
