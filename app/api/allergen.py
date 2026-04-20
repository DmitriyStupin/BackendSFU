from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Annotated
from pydantic import BaseModel

from models import db_helper, Allergen

router = APIRouter(
    prefix="/allergens",
    tags=["Allergen"],
)


class AllergenCreate(BaseModel):
    name: str


class AllergenRead(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


@router.post("", response_model=AllergenRead, status_code=status.HTTP_201_CREATED)
async def create_allergen(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    data: AllergenCreate,
):
    allergen = Allergen(name=data.name)
    session.add(allergen)
    await session.commit()
    await session.refresh(allergen)
    return allergen


@router.get("", response_model=list[AllergenRead])
async def get_allergens(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
):
    result = await session.scalars(select(Allergen))
    return result.all()


@router.get("/{id}", response_model=AllergenRead)
async def get_allergen(
    id: int,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
):
    allergen = await session.get(Allergen, id)
    if not allergen:
        raise HTTPException(status_code=404, detail="Allergen not found")
    return allergen


@router.put("/{id}", response_model=AllergenRead)
async def update_allergen(
    id: int,
    data: AllergenCreate,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
):
    allergen = await session.get(Allergen, id)
    if not allergen:
        raise HTTPException(status_code=404, detail="Allergen not found")

    allergen.name = data.name
    await session.commit()
    await session.refresh(allergen)
    return allergen


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_allergen(
    id: int,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
):
    allergen = await session.get(Allergen, id)
    if not allergen:
        raise HTTPException(status_code=404, detail="Allergen not found")

    await session.delete(allergen)
    await session.commit()