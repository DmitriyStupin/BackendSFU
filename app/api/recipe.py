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
from models import Recipe, Cuisine, Allergen, Ingredient, RecipeIngredient, recipe_allergens

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

class RecipeIngredientCreate(BaseModel):
    ingredient_id: int
    quantity: int
    measurement: int  # enum как int


class RecipeCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str
    cooking_time: int
    difficulty: int

    cuisine_id: int
    allergen_ids: list[int] = []
    ingredients: list[RecipeIngredientCreate] = []
    
    
@router.post("", response_model=RecipeRead, status_code=201)
async def create_recipe(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    data: RecipeCreate,
):
    recipe = Recipe(
        title=data.title,
        description=data.description,
        cooking_time=data.cooking_time,
        difficulty=data.difficulty,
        cuisine_id=data.cuisine_id,
    )

    session.add(recipe)
    await session.flush()  

    if data.allergen_ids:
        await session.execute(
            recipe_allergens.insert().values(
                [
                    {"recipe_id": recipe.id, "allergen_id": a_id}
                    for a_id in data.allergen_ids
                ]
            )
        )

    for item in data.ingredients:
        recipe_ingredient = RecipeIngredient(
            recipe_id=recipe.id,
            ingredient_id=item.ingredient_id,
            quantity=item.quantity,
            measurement=item.measurement,
        )
        session.add(recipe_ingredient)

    await session.commit()

    return recipe
  
@router.get("/{id}")
async def get_recipe(
    id: int,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
):
    recipe = await session.get(Recipe, id)

    allergens = await session.execute(
        recipe_allergens.select().where(recipe_allergens.c.recipe_id == id)
    )

    ingredients = await session.execute(
        select(RecipeIngredient).where(RecipeIngredient.recipe_id == id)
    )

    return {
        **recipe.__dict__,
        "allergens": allergens.mappings().all(),
        "ingredients": ingredients.scalars().all(),
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


@router.put("/{id}", response_model=RecipeRead)
async def update(
  session: Annotated[
    AsyncSession,
    Depends(db_helper.session_getter),
  ],
  id: int,
  recipe_update: RecipeUpdate,
):
  recipe = await session.get(Recipe, id)
  if recipe_update.title is not None:
    recipe.title = recipe_update.title
  if recipe_update.description is not None:
    recipe.description = recipe_update.description
  if recipe_update.cooking_time is not None:
    recipe.cooking_time = recipe_update.cooking_time
  if recipe_update.difficulty is not None:
    recipe.difficulty = recipe_update.difficulty
  await session.commit()
  return recipe


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def destroy(
  session: Annotated[
    AsyncSession,
    Depends(db_helper.session_getter),
  ],
  id: int,
): 
  recipe = await session.get(Recipe, id)
  if not recipe:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND, detail=f"Recipe with id {id} not found"
    )
  
  await session.delete(recipe)
  await session.commit()
  
