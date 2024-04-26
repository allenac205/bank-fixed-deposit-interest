from fastapi import APIRouter

from . import statements


router = APIRouter(
    prefix="/statements",
    tags=["statements"]
)

router.include_router(statements.router)