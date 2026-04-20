from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Annotated
from pydantic import BaseModel
from models import Recipe, RecipeIngredient

from models import db_helper, Ingredient

router = APIRouter(
    prefix="/ingredients",
    tags=["Ingredient"],
)


class IngredientCreate(BaseModel):
    name: str


class IngredientRead(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


@router.post("", response_model=IngredientRead, status_code=status.HTTP_201_CREATED)
async def create_ingredient(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    data: IngredientCreate,
):
    ingredient = Ingredient(name=data.name)
    session.add(ingredient)
    await session.commit()
    await session.refresh(ingredient)
    return ingredient


@router.get("", response_model=list[IngredientRead])
async def get_ingredients(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
):
    result = await session.scalars(select(Ingredient))
    return result.all()


@router.get("/{id}", response_model=IngredientRead)
async def get_ingredient(
    id: int,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
):
    ingredient = await session.get(Ingredient, id)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return ingredient


@router.put("/{id}", response_model=IngredientRead)
async def update_ingredient(
    id: int,
    data: IngredientCreate,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
):
    ingredient = await session.get(Ingredient, id)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    ingredient.name = data.name
    await session.commit()
    await session.refresh(ingredient)
    return ingredient


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ingredient(
    id: int,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
):
    ingredient = await session.get(Ingredient, id)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    await session.delete(ingredient)
    await session.commit()
    
@router.get("/{id}/recipes")
async def get_recipes_by_ingredient(
    id: int,
    session: AsyncSession = Depends(db_helper.session_getter),
):
    # 1. находим связи ingredient → recipes
    stmt_links = select(RecipeIngredient).where(
        RecipeIngredient.ingredient_id == id
    )
    links = await session.scalars(stmt_links)
    links = links.all()

    # если нет связей — пустой список
    if not links:
        return []

    # 2. достаём recipe_id
    recipe_ids = [link.recipe_id for link in links]

    # 3. забираем рецепты
    stmt_recipes = select(Recipe).where(Recipe.id.in_(recipe_ids))
    recipes = await session.scalars(stmt_recipes)

    return recipes.all()