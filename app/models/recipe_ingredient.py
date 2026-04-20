from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, Integer

from .base import Base


class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"

    id: Mapped[int] = mapped_column(primary_key=True)

    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id"))
    ingredient_id: Mapped[int] = mapped_column(ForeignKey("ingredients.id"))

    quantity: Mapped[int] = mapped_column(Integer)
    measurement: Mapped[int] = mapped_column(Integer)  # enum как int

    def __repr__(self):
        return f"RecipeIngredient(id={self.id})"