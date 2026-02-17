from fastapi import ( 
  APIRouter
)
from config import settings

router = APIRouter(
  tags=["Recipe"],
  prefix=settings.url.recipe
)

@router.get("")
def index():
  return {"message": "Hello, World!"}