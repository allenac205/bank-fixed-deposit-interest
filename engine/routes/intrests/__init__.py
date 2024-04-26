from fastapi import APIRouter

from . import intrests


router = APIRouter(
    prefix="/intrests",
    tags=["intrests"]
)

router.include_router(intrests.router)