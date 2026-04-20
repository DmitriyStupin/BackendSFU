from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, Integer, ForeignKey

from .base import Base
from .recipe_allergens import recipe_allergens


class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    cooking_time: Mapped[int] = mapped_column(Integer)
    difficulty: Mapped[int] = mapped_column(Integer, default=1)

    cuisine_id: Mapped[int] = mapped_column(ForeignKey("cuisines.id"))

    cuisine = relationship("Cuisine", back_populates="recipes")

    allergens = relationship(
        "Allergen",
        secondary=recipe_allergens,
        back_populates="recipes",
    )

    recipe_ingredients = relationship(
        "RecipeIngredient",
        back_populates="recipe",
        cascade="all, delete-orphan",
    )