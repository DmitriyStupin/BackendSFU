from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Annotated
from pydantic import BaseModel

from models import db_helper, Cuisine

router = APIRouter(
    prefix="/cuisine",
    tags=["Cuisine"],
)


# DTO
class CuisineCreate(BaseModel):
    name: str


class CuisineRead(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


# CREATE
@router.post("", response_model=CuisineRead, status_code=status.HTTP_201_CREATED)
async def create_cuisine(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    data: CuisineCreate,
):
    cuisine = Cuisine(name=data.name)
    session.add(cuisine)
    await session.commit()
    await session.refresh(cuisine)
    return cuisine


# READ ALL
@router.get("", response_model=list[CuisineRead])
async def get_cuisines(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
):
    result = await session.scalars(select(Cuisine))
    return result.all()


# READ ONE
@router.get("/{id}", response_model=CuisineRead)
async def get_cuisine(
    id: int,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
):
    cuisine = await session.get(Cuisine, id)
    if not cuisine:
        raise HTTPException(status_code=404, detail="Cuisine not found")
    return cuisine


# UPDATE
@router.put("/{id}", response_model=CuisineRead)
async def update_cuisine(
    id: int,
    data: CuisineCreate,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
):
    cuisine = await session.get(Cuisine, id)
    if not cuisine:
        raise HTTPException(status_code=404, detail="Cuisine not found")

    cuisine.name = data.name
    await session.commit()
    await session.refresh(cuisine)
    return cuisine


# DELETE
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cuisine(
    id: int,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
):
    cuisine = await session.get(Cuisine, id)
    if not cuisine:
        raise HTTPException(status_code=404, detail="Cuisine not found")

    await session.delete(cuisine)
    await session.commit()