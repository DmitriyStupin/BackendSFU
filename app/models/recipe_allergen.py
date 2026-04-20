from sqlalchemy import Table, Column, ForeignKey
from .base import Base


recipe_allergens = Table(
    "recipe_allergens",
    Base.metadata,
    Column("recipe_id", ForeignKey("recipes.id"), primary_key=True),
    Column("allergen_id", ForeignKey("allergens.id"), primary_key=True),
)