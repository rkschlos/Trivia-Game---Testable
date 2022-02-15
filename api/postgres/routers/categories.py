from fastapi import APIRouter, Depends, Response, status
from typing import Union
from ..models.categories import (
    CategoryIn,
    CategoryList,
    CategoryOut,
    CategoryDeleteOperation,
)
from ..models.common import ErrorMessage
from ..db import CategoryQueries, DuplicateTitle

router = APIRouter()


def row_to_category(row):
    category = {
        "id": row[0],
        "title": row[1],
        "canon": row[2],
    }
    if len(row) == 4:
        category["num_clues"] = row[3]
    return category


@router.get(
    "/api/postgres/categories",
    response_model=CategoryList,
)
def get_categories(page: int = 0, query=Depends(CategoryQueries)):
    page_count, rows = query.get_all_categories(page)
    return {
        "page_count": page_count,
        "categories": [row_to_category(row) for row in rows],
    }


@router.get(
    "/api/postgres/categories/{category_id}",
    response_model=Union[CategoryOut, ErrorMessage],
    responses={
        200: {"model": CategoryOut},
        404: {"model": ErrorMessage},
    },
)
def get_category(category_id: int, response: Response, query=Depends(CategoryQueries)):
    row = query.get_category(category_id)
    if row is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Category not found"}
    return row_to_category(row)


@router.post(
    "/api/postgres/categories",
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
        row = query.insert_category(category.title)
        return row_to_category(row)
    except DuplicateTitle:
        response.status_code = status.HTTP_409_CONFLICT
        return {"message": f"Duplicate category title: {category.title}"}


@router.put(
    "/api/postgres/categories/{category_id}",
    response_model=Union[CategoryOut, ErrorMessage],
    responses={
        200: {"model": CategoryOut},
        404: {"model": ErrorMessage},
        409: {"model": ErrorMessage},
    },
)
def update_category(
    category_id: int,
    category: CategoryIn,
    response: Response,
    query=Depends(CategoryQueries),
):
    try:
        row = query.update_category(category_id, category.title)
        if row is None:
            response.status_code = status.HTTP_404_NOT_FOUND
            return {"message": "Category not found"}
        return row_to_category(row)
    except DuplicateTitle:
        response.status_code = status.HTTP_409_CONFLICT
        return {"message": f"Duplicate category title: {category.title}"}


@router.delete(
    "/api/postgres/categories/{category_id}",
    response_model=CategoryDeleteOperation,
)
def delete_category(category_id: int, query=Depends(CategoryQueries)):
    try:
        query.delete_category(category_id)
        return {"result": True}
    except:
        return {"result": False}
