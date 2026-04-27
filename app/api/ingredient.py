from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Annotated
from pydantic import BaseModel
from sqlalchemy.orm import selectinload
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
    include: str | None = Query(default=None),
    select_fields: str | None = Query(default=None, alias="select"),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    include_options = {
        item.strip() for item in (include or "").split(",") if item.strip()
    }
    allowed_include = {"cuisine", "ingredients", "allergens"}
    invalid_include = include_options - allowed_include
    if invalid_include:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unsupported include values: {', '.join(sorted(invalid_include))}",
        )

    selected_fields = {
        item.strip() for item in (select_fields or "").split(",") if item.strip()
    }
    allowed_fields = {"id", "name", "difficulty", "description", "cooking_time"}
    if selected_fields:
        invalid_fields = selected_fields - allowed_fields
        if invalid_fields:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Unsupported select values: {', '.join(sorted(invalid_fields))}",
            )
    else:
        selected_fields = allowed_fields

    query = (
        select(Recipe)
        .join(RecipeIngredient, RecipeIngredient.recipe_id == Recipe.id)
        .where(RecipeIngredient.ingredient_id == id)
        .distinct()
    )

    if "cuisine" in include_options:
        query = query.options(selectinload(Recipe.cuisine))
    if "ingredients" in include_options:
        query = query.options(
            selectinload(Recipe.recipe_ingredients).selectinload(RecipeIngredient.ingredient)
        )
    if "allergens" in include_options:
        query = query.options(selectinload(Recipe.allergens))

    recipes = (await session.scalars(query)).all()

    result: list[dict] = []
    for recipe in recipes:
        item: dict = {}

        if "id" in selected_fields:
            item["id"] = recipe.id
        if "name" in selected_fields:
            item["name"] = recipe.title
        if "difficulty" in selected_fields:
            item["difficulty"] = recipe.difficulty
        if "description" in selected_fields:
            item["description"] = recipe.description
        if "cooking_time" in selected_fields:
            item["cooking_time"] = recipe.cooking_time

        if "cuisine" in include_options:
            item["cuisine"] = (
                {"id": recipe.cuisine.id, "name": recipe.cuisine.name}
                if recipe.cuisine
                else None
            )
        if "ingredients" in include_options:
            item["ingredients"] = [
                {
                    "id": ri.id,
                    "ingredient_id": ri.ingredient_id,
                    "ingredient_name": ri.ingredient.name if ri.ingredient else None,
                    "quantity": ri.quantity,
                    "measurement": ri.measurement,
                }
                for ri in recipe.recipe_ingredients
            ]
        if "allergens" in include_options:
            item["allergens"] = [
                {"id": allergen.id, "name": allergen.name} for allergen in recipe.allergens
            ]

        result.append(item)

    return result