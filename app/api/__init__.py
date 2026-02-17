from fastapi import APIRouter

from config import settings

from .test import router as test_router
from .posts import router as posts_router
from .recipe import router as recipe_router

router = APIRouter(
    prefix=settings.url.prefix,
)
router.include_router(test_router)
router.include_router(posts_router)
router.include_router(recipe_router)
