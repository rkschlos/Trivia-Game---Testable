from pydantic import BaseModel


class GameOut(BaseModel):
    id: str
    episode_id: int
    aired: str
    canon: bool
    total_amount_won: int
