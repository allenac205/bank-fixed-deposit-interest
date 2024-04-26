from fastapi import APIRouter, Body
from typing import Literal

from crud import motor_find_all, motor_find_one, motor_update_one


router = APIRouter()


@router.get("/")
async def get_deposits(user_name: Literal["allen", "gladys"], status: Literal["ACTIVE", "CANCELLED"] = None):

    user_db = await motor_find_one(collection="users", query={"user_name": user_name})

    if status != None:
        query = ({"status": status, "user": user_db["_id"]}, {"_id": 0, "user": 0})
    else:
        query = ({"user": user_db["_id"]}, {"_id": 0, "user": 0})

    result = await motor_find_all(collection="deposits", query=query)
    result = await result.to_list(None)

    # await convert_datetime_to_str(result)

    return result


@router.get("/deposit-incomplete")
async def deposit_incomplete(user_name: Literal["allen", "gladys"]):

    user_db = await motor_find_one(collection="users", query={"user_name": user_name})

    result = await motor_find_all(
        collection="deposits", 
        query=(
            {
                "user": user_db["_id"], 
                "$or": [
                    {"duration": 0}, 
                    {"initial_intrest_rate": 0},
                    {"current_intrest_rate": 0}
                ]
            },
            {
                "_id": 0,
                "user": 0
            }
        )
    )
    result = await result.to_list(None)

    return result


@router.patch("/")
async def deposit_patch(user_name: Literal["allen", "gladys"], fd_number:str, depo_path: dict = Body(...)):

    user_db = await motor_find_one(collection="users", query={"user_name": user_name})
    
    if await motor_find_one(collection="deposits", query={"fd_number":fd_number, "user": user_db["_id"]}):

        result = await motor_update_one(
            collection="deposits", 
            query=(
                {"fd_number":fd_number, "user": user_db["_id"]}, 
                {"$set": {"initial_intrest_rate": depo_path.initial_intrest_rate, "current_intrest_rate": depo_path.current_intrest_rate, "duration": depo_path.duration}}
            )
        )
        
        return {"patch_result": result.modified_count}
    else:
        return "FD number not found"