from fastapi import APIRouter
from crud import motor_insert_one

from models import UserInmodel, UserModel



router = APIRouter()


@router.post("/")
async def create_user(user: UserInmodel):
    try:


        user = UserModel.model_validate(user.model_dump())
        rslt = await motor_insert_one(collection="users", query=user.model_dump())
        return {
            "uid": str(rslt.inserted_id)
        }


    except Exception as err:
        return str(err)