from fastapi import APIRouter

from . import deposits


router = APIRouter(
    prefix="/deposits",
    tags=["deposits"]
)

router.include_router(deposits.router)