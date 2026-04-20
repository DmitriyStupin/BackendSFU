from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String

from .base import Base


class Cuisine(Base):
    __tablename__ = "cuisines"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)

    recipes = relationship("Recipe", back_populates="cuisine")