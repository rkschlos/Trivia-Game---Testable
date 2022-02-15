from fastapi import APIRouter, Depends, Response, status
from typing import Union
from ..models.games import GameOut
from ..models.common import ErrorMessage
from ..db import GameQueries


router = APIRouter()


def row_to_game(row):
    return {
        "id": row[0],
        "episode_id": row[1],
        "aired": row[2],
        "canon": row[3],
        "total_amount_won": row[4],
    }


@router.get(
    "/api/postgres/games/{game_id}",
    response_model=Union[GameOut, ErrorMessage],
    responses={
        200: {"model": GameOut},
        404: {"model": ErrorMessage},
    },
)
def get_game(game_id: int, response: Response, query=Depends(GameQueries)):
    row = query.get_game(game_id)
    if row is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Game not found"}
    return row_to_game(row)
