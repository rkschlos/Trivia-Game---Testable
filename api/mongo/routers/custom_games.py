from bson.objectid import ObjectId
from typing import Union
from fastapi import APIRouter, Depends, Response, status
from ..db import CustomGameQueries
from ..models.custom_games import CustomGameOut
from ..models.common import ErrorMessage
from .clues import fix_clue_ids

router = APIRouter()


def fix_game_ids(custom_game):
    custom_game["id"] = str(custom_game["_id"])
    custom_game["created_on"] = str(custom_game["created_on"])
    for clue in custom_game["clues"]:
        fix_clue_ids(clue)
    return custom_game


@router.post(
    "/api/mongo/custom-games",
    response_model=Union[CustomGameOut, ErrorMessage],
    responses={
        200: {"model": CustomGameOut},
        500: {"model": ErrorMessage},
    },
)
def create_custom_game(query=Depends(CustomGameQueries)):
    custom_game = query.create()
    return fix_game_ids(custom_game)


@router.get(
    "/api/mongo/custom-games/{custom_game_id}",
    response_model=Union[CustomGameOut, ErrorMessage],
    responses={
        200: {"model": CustomGameOut},
        404: {"model": ErrorMessage},
    },
)
def create_custom_game(
    custom_game_id: str,
    response: Response,
    query=Depends(CustomGameQueries),
):
    custom_game_id = ObjectId(custom_game_id)
    custom_game = query.get_custom_game(custom_game_id)
    if custom_game is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Custom game not found"}

    return fix_game_ids(custom_game)
