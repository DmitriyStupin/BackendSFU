from fastapi_filter.contrib.sqlalchemy import Filter
from models import Recipe, RecipeIngredient
from sqlalchemy import select


class RecipeFilter(Filter):
    name__like: str | None = None
    ingredient_id: list[int] | None = None

    sort: list[str] | None = ["-id"]

    class Constants(Filter.Constants):
        model = Recipe

    def filter(self, query):
        if self.name__like:
            query = query.where(Recipe.title.ilike(f"%{self.name__like}%"))

        if self.ingredient_id:
            query = query.where(
                Recipe.id.in_(
                    select(RecipeIngredient.recipe_id).where(
                        RecipeIngredient.ingredient_id.in_(self.ingredient_id)
                    )
                )
            )

        return query