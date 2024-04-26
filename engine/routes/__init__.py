from fastapi import APIRouter

from . import users, statements, intrests, deposits


router = APIRouter()


router.include_router(users.router)
router.include_router(statements.router)
router.include_router(intrests.router)
router.include_router(deposits.router)


