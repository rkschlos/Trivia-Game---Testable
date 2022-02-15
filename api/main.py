from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from mongo.routers import (
    categories as mongo_categories,
    clues as mongo_clues,
    games as mongo_games,
    custom_games as mongo_custom_games,
)
from postgres.routers import (
    categories as psql_categories,
    clues as psql_clues,
    games as psql_games,
    custom_games as psql_custom_games,
)

app = FastAPI()


origins = [
    "http://localhost:3000",
    os.environ.get("CORS_HOST", None),
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB endpoints
app.include_router(mongo_categories.router)
app.include_router(mongo_clues.router)
app.include_router(mongo_games.router)
app.include_router(mongo_custom_games.router)


# PostgreSQL endpoints
app.include_router(psql_categories.router)
app.include_router(psql_clues.router)
app.include_router(psql_games.router)
app.include_router(psql_custom_games.router)
