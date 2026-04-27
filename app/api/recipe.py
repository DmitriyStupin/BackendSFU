from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from typing import Optional, Annotated

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.sql import Select

from fastapi_filter import FilterDepends
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import apaginate

from models import (
    db_helper,
    Recipe,
    RecipeIngredient,
    recipe_allergens,
)

from filters.recipe import RecipeFilter

router = APIRouter(
    tags=["Recipe"],
    prefix="/recipes",
)

class RecipeBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    cooking_time: int = Field(..., gt=0)
    difficulty: int = Field(..., ge=1, le=5)


class RecipeRead(RecipeBase):
    id: int

    model_config = {
        "from_attributes": True
    }


class RecipeUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    cooking_time: Optional[int] = Field(None, gt=0)
    difficulty: Optional[int] = Field(None, ge=1, le=5)


class RecipeIngredientCreate(BaseModel):
    ingredient_id: int
    quantity: int
    measurement: int


class RecipeCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str
    cooking_time: int
    difficulty: int

    cuisine_id: int
    allergen_ids: list[int] = []
    ingredients: list[RecipeIngredientCreate] = []

@router.post("", response_model=RecipeRead, status_code=status.HTTP_201_CREATED)
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

    # allergens
    if data.allergen_ids:
        await session.execute(
            recipe_allergens.insert().values(
                [
                    {"recipe_id": recipe.id, "allergen_id": a_id}
                    for a_id in data.allergen_ids
                ]
            )
        )

    # ingredients
    for item in data.ingredients:
        session.add(
            RecipeIngredient(
                recipe_id=recipe.id,
                ingredient_id=item.ingredient_id,
                quantity=item.quantity,
                measurement=item.measurement,
            )
        )

    await session.commit()
    return recipe


@router.get("/{id}", response_model=RecipeRead)
async def get_recipe(
    id: int,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
):
    recipe = await session.get(Recipe, id)

    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    return recipe


@router.get("", response_model=Page[RecipeRead])
async def read_recipes(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    recipe_filter: RecipeFilter = FilterDepends(RecipeFilter),
    ingredient_id: str | None = Query(default=None),
):
    stmt: Select = select(Recipe)

    # fastapi-filter
    stmt = recipe_filter.filter(stmt)
    stmt = recipe_filter.sort(stmt)

    # filter by ingredient
    if ingredient_id:
        try:
            ingredient_ids = [
                int(i.strip()) for i in ingredient_id.split(",") if i.strip()
            ]
        except ValueError:
            raise HTTPException(
                status_code=422,
                detail="ingredient_id must be integers separated by comma",
            )

        if ingredient_ids:
            stmt = (
                stmt.join(RecipeIngredient)
                .where(RecipeIngredient.ingredient_id.in_(ingredient_ids))
                .distinct()
            )

    return await apaginate(session, stmt)


@router.put("/{id}", response_model=RecipeRead)
async def update_recipe(
    id: int,
    recipe_update: RecipeUpdate,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
):
    recipe = await session.get(Recipe, id)

    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    for field, value in recipe_update.model_dump(exclude_unset=True).items():
        setattr(recipe, field, value)

    await session.commit()
    return recipe


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe(
    id: int,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
):
    recipe = await session.get(Recipe, id)

    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    await session.delete(recipe)
    await session.commit()