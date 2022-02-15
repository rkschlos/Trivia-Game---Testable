from bson.objectid import ObjectId
from fastapi import APIRouter, Depends, Response, status
from typing import Union
from ..models.games import GameOut
from ..models.common import ErrorMessage
from ..db import GameQueries


router = APIRouter()


@router.get(
    "/api/mongo/games/{game_id}",
    response_model=Union[GameOut, ErrorMessage],
    responses={
        200: {"model": GameOut},
        404: {"model": ErrorMessage},
    },
)
def get_game(game_id: str, response: Response, query=Depends(GameQueries)):
    game_id = ObjectId(game_id)
    game = query.get_game(game_id)
    if game is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Game not found"}
    game["id"] = str(game["_id"])
    return game
