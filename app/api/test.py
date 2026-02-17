from fastapi import (
    APIRouter,
    Query
)
from config import settings
from pydantic import BaseModel
from typing import Annotated

router = APIRouter(
    tags=["Test"],
    prefix=settings.url.test,
)


@router.get("")
def index():
    return {"message": "Hello, World!"}

class FormulaRacer(BaseModel):
    name: str
    country: str
    team: str
    number: int
    isWorldChampion: bool = False

@router.post('/racers/')
async def create_item(formulaRacer: FormulaRacer):
    return format

@router.get('/items/')
async def read_items(q: Annotated[str | None, Query(min_length=5, max_length=50)] = None):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results