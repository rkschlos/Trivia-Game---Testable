from bson.objectid import ObjectId
from fastapi import APIRouter, Depends, Response, status
from typing import Union
from ..models.clues import ClueOut, ClueList
from ..models.common import ErrorMessage
from ..db import ClueQueries


router = APIRouter()


def fix_clue_ids(clue):
    clue["id"] = str(clue["_id"])
    clue["category"]["id"] = str(clue["category"]["_id"])
    return clue


@router.get(
    "/api/mongo/clues/random-clue",
    response_model=ClueOut,
)
def get_random_clue(query=Depends(ClueQueries)):
    clue = query.get_random_clue()
    return fix_clue_ids(clue)


@router.get(
    "/api/mongo/clues/{clue_id}",
    response_model=Union[ClueOut, ErrorMessage],
    responses={
        200: {"model": ClueOut},
        404: {"model": ErrorMessage},
    },
)
def get_clue(clue_id: str, response: Response, query=Depends(ClueQueries)):
    clue_id = ObjectId(clue_id)
    clue = query.get_clue(clue_id)
    if clue is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Clue not found"}
    return fix_clue_ids(clue)


@router.get(
    "/api/mongo/clues",
    response_model=ClueList,
)
def get_clues(page: int = 0, value: int = 0, query=Depends(ClueQueries)):
    page_count, clues = query.get_all_clues(page, value)
    return {
        "page_count": page_count,
        "clues": [fix_clue_ids(clue) for clue in clues],
    }


@router.delete(
    "/api/mongo/clues/{clue_id}",
    response_model=Union[ClueOut, ErrorMessage],
    responses={
        200: {"model": ClueOut},
        404: {"model": ErrorMessage},
    },
)
def increment_invalid_count(
    clue_id: str,
    response: Response,
    query=Depends(ClueQueries),
):
    clue_id = ObjectId(clue_id)
    clue = query.increment_invalid_count(clue_id)
    if clue is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Clue not found"}
    return fix_clue_ids(clue)
