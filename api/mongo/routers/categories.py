from fastapi import APIRouter, Depends, Response, status
from typing import Union
from bson.objectid import ObjectId
from ..models.categories import (
    CategoryIn,
    CategoryList,
    CategoryOut,
    CategoryDeleteOperation,
)
from ..models.common import ErrorMessage
from ..db import CategoryQueries, DuplicateTitle

router = APIRouter()


@router.get(
    "/api/mongo/categories",
    response_model=CategoryList,
)
def get_categories(page: int = 0, query=Depends(CategoryQueries)):
    page_count, categories = query.get_all_categories(page)
    for category in categories:
        category["id"] = str(category["_id"])
    return {
        "page_count": page_count,
        "categories": categories,
    }


@router.get(
    "/api/mongo/categories/{category_id}",
    response_model=Union[CategoryOut, ErrorMessage],
    responses={
        200: {"model": CategoryOut},
        404: {"model": ErrorMessage},
    },
)
def get_category(category_id: str, response: Response, query=Depends(CategoryQueries)):
    category_id = ObjectId(category_id)
    category = query.get_category(category_id)
    if category is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Category not found"}
    category["id"] = str(category["_id"])
    return category


@router.post(
    "/api/mongo/categories",
    response_model=Union[CategoryOut, ErrorMessage],
    responses={
        200: {"model": CategoryOut},
        409: {"model": ErrorMessage},
    },
)
def create_category(
    category: CategoryIn,
    response: Response,
    query=Depends(CategoryQueries),
):
    try:
        category = query.insert_category(category.title)
        category["id"] = str(category["_id"])
        return category
    except DuplicateTitle:
        response.status_code = status.HTTP_409_CONFLICT
        return {"message": f"Duplicate category title: {category.title}"}


@router.put(
    "/api/mongo/categories/{category_id}",
    response_model=Union[CategoryOut, ErrorMessage],
    responses={
        200: {"model": CategoryOut},
        404: {"model": ErrorMessage},
        409: {"model": ErrorMessage},
    },
)
def update_category(
    category_id: str,
    category: CategoryIn,
    response: Response,
    query=Depends(CategoryQueries),
):
    try:
        category_id = ObjectId(category_id)
        category = query.update_category(category_id, category.title)
        if category is None:
            response.status_code = status.HTTP_404_NOT_FOUND
            return {"message": "Category not found"}
        category["id"] = str(category["_id"])
        return category
    except DuplicateTitle:
        response.status_code = status.HTTP_409_CONFLICT
        return {"message": f"Duplicate category title: {category.title}"}


@router.delete(
    "/api/mongo/categories/{category_id}",
    response_model=CategoryDeleteOperation,
)
def delete_category(category_id: str, query=Depends(CategoryQueries)):
    try:
        category_id = ObjectId(category_id)
        query.delete_category(category_id)
        return {"result": True}
    except:
        return {"result": False}
