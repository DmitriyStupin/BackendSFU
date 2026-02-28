from fastapi import ( 
  APIRouter,
  Depends,
  HTTPException,
  status
)
from config import settings
from pydantic import BaseModel, Field
from typing import Optional, Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import db_helper, Recipe

router = APIRouter(
  tags=["Recipe"],
  prefix=settings.url.recipe
)

class RecipeBase(BaseModel):
  title: str = Field(..., min_length=1, max_length=255)
  description: str = Field(..., min_length=1)
  cooking_time: int = Field(..., gt=0)
  difficulty: int = Field(..., ge=1, le=5)
  
class RecipeCreate(RecipeBase):
  pass

class RecipeUpdate(BaseModel):
  title: Optional[str] = Field(None, min_length=1, max_length=255)
  description: Optional[str] = Field(None, min_length=1)
  cooking_time: Optional[int] = Field(None, gt=0)
  difficulty: Optional[int] = Field(None, ge=1, le=5)
  
class RecipeRead(RecipeBase):
  id: int
  
  model_config = {
    'from_attributes': True
  }


@router.get('', response_model=list[RecipeRead])
async def read_recipes(
  session: Annotated[
    AsyncSession,
    Depends(db_helper.session_getter),
  ],
):
  stmt = select(Recipe).order_by(Recipe.id)
  result = await session.scalars(stmt)
  return result.all()


@router.post('', response_model=RecipeRead, status_code=status.HTTP_201_CREATED)
async def store(
  session: Annotated[
    AsyncSession,
    Depends(db_helper.session_getter),
  ],
  recipe_create: RecipeCreate,
):
  recipe = Recipe(title=recipe_create.title, description=recipe_create.description, 
                  cooking_time=recipe_create.cooking_time, difficulty=recipe_create.difficulty)
  session.add(recipe)
  await session.commit()
  return recipe


@router.get("/{id}", response_model=RecipeRead)
async def show(
  session: Annotated[
    AsyncSession,
    Depends(db_helper.session_getter),
  ],
  id: int,
):
  recipe = await session.get(Recipe, id)
  return recipe