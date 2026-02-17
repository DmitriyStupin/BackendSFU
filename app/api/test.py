from fastapi import (
    APIRouter,
    Query,
    Path,
    Form,
    UploadFile,
    HTTPException,
    File
)
from config import settings
from pydantic import (BaseModel, Field)
from typing import (Annotated, Literal)
from fastapi.responses import HTMLResponse, JSONResponse
from pathlib import Path
import uuid


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

class FilterParams(BaseModel):
    model_config = {'extra': 'forbid'}

    limit: int = Field(100, gt=0, le=100)
    offset: int = Field(0, ge=0)
    order_by: Literal['created_at', 'update_at'] = 'created_at'
    tags: list[str] = []

class FormData(BaseModel):
    username: str
    password: str

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

@router.get('/products/')
async def read_products(filter_query: Annotated[FilterParams, Query()]):
    return filter_query

@router.post("/login/")
async def login(data: Annotated[FormData, Form()]):
    return data

@router.get("/champion")
async def read_champion(format: str):
    if format == 'json':
        return {
            "name": 'Max Verstappen',
            "team": 'RedBull'
        }
    elif format == 'html':
        return HTMLResponse(
            """
                <html>
                    <head>
                        <title>F1 World Champion</title>
                    </head>
                    <body>
                        <h1>Max Verstappen</h1>
                        <h2>RedBull</h2>
                    </body>
                </html>
            """
        )

UPLOAD_DIR = Path(__file__).parent.parent / "static/uploads"

@router.post("/upload-file")
async def upload_file(file: UploadFile):
    allowed_types = ['image/png', 'image/jpeg', 'image/webp']
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Only PNG, JPG and WEBP images are allowed")
    
    extension = file.filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4()}.{extension}"
    file_path = UPLOAD_DIR / unique_filename
    
    content = await file.read()
    with open(file_path, 'wb') as buffer:
        buffer.write(content)
        
    url = f"/static/uploads/{unique_filename}"
    return JSONResponse({"url": url})