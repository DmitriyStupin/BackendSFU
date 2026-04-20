from fastapi import APIRouter

from config import settings

from .test import router as test_router
from .posts import router as posts_router
from .recipe import router as recipe_router
from .cuisine import router as cuisine_router
from .allergen import router as allergen_router
from .ingredient import router as ingredient_router

router = APIRouter(
    prefix=settings.url.prefix,
)
router.include_router(test_router)
router.include_router(posts_router)
router.include_router(recipe_router)
router.include_router(cuisine_router)
router.include_router(allergen_router)
router.include_router(ingredient_router)