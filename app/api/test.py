from fastapi import (
    APIRouter,
    Query,
    Path,
    Form
)
from config import settings
from pydantic import (BaseModel, Field)
from typing import (Annotated, Literal)

router = APIRouter(
    tags=["Test"],
    prefix=settings.url.test,
)


@router.get("")
def index():
    return {"message": "Hello, World!"}

class FormulaTeam(BaseModel):
    name: str
    country: str

class FormulaRacer(BaseModel):
    name: str
    country: str
    team: FormulaTeam
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

@router.get('/items/{item_id}/')
async def read_items(
    *,
    item_id: Annotated[int, Path(title="The ID of the item to get", gt=0, le=1000)],
    q: Annotated[str | None, Query(alias='item-query')] = None,
    size: Annotated[float, Query(gt=0, lt=10.5)],
): 
    results = {'item_id': item_id}
    if q: 
        results.update({"q": q})
    return results

class FilterParams(BaseModel):
    model_config = {'extra': 'forbid'}

    limit: int = Field(100, gt=0, le=100)
    offset: int = Field(0, ge=0)
    order_by: Literal['created_at', 'update_at'] = 'created_at'
    tags: list[str] = []

@router.get('/products/')
async def read_products(filter_query: Annotated[FilterParams, Query()]):
    return filter_query

@router.post("/login/")
async def login(username: Annotated[str, Form()], password: Annotated[str, Form()]):
    return {"username": username}