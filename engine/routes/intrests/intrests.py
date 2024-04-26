from icecream import ic
from typing import Literal
from datetime import datetime
from operator import itemgetter
from dateutil.relativedelta import relativedelta

from fastapi import APIRouter

from crud import motor_find_all, motor_find_one, motor_aggregate
from settings import settings

from helpers.general import convert_datetime_to_str, fy_dict
from helpers.intrests import total_intrest_only, total_intrest_with_fd, fd_wise_intrest, fd_wise_intrest_with_indv_total, fd_wise_intrest_with_indv_total_intrest_only
from helpers.deposits import missing_deposits_int_find

router = APIRouter()


@router.get("/")
async def get_intrest(user_name: Literal["allen", "gladys"], mode: Literal["TOTAL_INTREST_ONLY", "TOTAL_INTREST_WITH_FD", "FD_WISE_INTREST", "FD_WISE_INTREST_WITH_INDV_TOTAL_INTREST", "FD_WISE_INTREST_WITH_INDV_TOTAL_INTREST_ONLY"], FY_year: Literal["FY_2021_2022", "FY_2022_2023", "FY_2023_2024", "FY_2024_2025", "FY_2025_2026"] = None, start_date: str = "", end_date: str = ""):
    try:


        user_db = await motor_find_one(collection=settings.db_tables.USER_TABLE, query={"user_name": user_name})

        ic(FY_year)

        if FY_year != None:

            start_date = fy_dict[FY_year]["start_date"]
            end_date = fy_dict[FY_year]["end_date"]
            ic(start_date, end_date)

        if start_date != "" or end_date != "":
            start_date = datetime.strptime(start_date, "%d-%m-%Y")
            end_date = datetime.strptime(end_date, "%d-%m-%Y")
            filter_document = {
                "date":{
                    "$gte": start_date,
                    "$lte": end_date,
                },
                "user": user_db["_id"]
            }

        else:
            filter_document = {}
        

        pipeline = [
            {
                "$match": filter_document
            },

            {
                "$project": {
                    "_id": 0,
                    "user": 0,
                    "timestamp": 0
                }
            },
            {
                "$sort": {
                    "date": 1
                }
            }
        ]

        data = await motor_aggregate(collection=settings.db_tables.INTREST_TABLE, query=pipeline)
        data = await data.to_list(None)
        ic(data)

        await convert_datetime_to_str(data)

        if mode == "TOTAL_INTREST_ONLY":
            result = await total_intrest_only(data)
            ic(result)

        elif mode == "TOTAL_INTREST_WITH_FD":
            result = await total_intrest_with_fd(data)
            ic(result)
        
        elif mode == "FD_WISE_INTREST":
            result = await fd_wise_intrest(data)
            ic(result)

        elif mode == "FD_WISE_INTREST_WITH_INDV_TOTAL_INTREST":
            result = await fd_wise_intrest_with_indv_total(data)
            ic(result)
        
        elif mode == "FD_WISE_INTREST_WITH_INDV_TOTAL_INTREST_ONLY":
            result = await fd_wise_intrest_with_indv_total_intrest_only(data)
            ic(result)

        return result


    except Exception as e:
        return str(e)


@router.get("/fd-specific")
async def fd_specific_intrest(user_name: Literal["allen", "gladys"], fd_number: str, start_date: str = "", end_date: str = ""):
    try:


        user_db = await motor_find_one(collection=settings.db_tables.USER_TABLE, query={"user_name": user_name})

        if await motor_find_one(collection=settings.db_tables.DEPOSITS_TABLE, query={"fd_number":fd_number, "user": user_db["_id"]}):
        
            if start_date != "" or end_date != "":

                start_date = datetime.strptime(start_date, "%d-%m-%Y")
                end_date = datetime.strptime(end_date, "%d-%m-%Y")

                filter_document = {
                    "date":{
                        "$gte": start_date,
                        "$lte": end_date
                    },
                    "fd_number": fd_number,
                    "user": user_db["_id"]
                }

            else:
                filter_document = {
                    "fd_number": fd_number,
                    "user": user_db["_id"]
                }

            pipeline = [
                {
                    "$match": filter_document
                },
                {
                    "$project": {
                        "_id": 0,
                        "user": 0,
                        "timestamp": 0
                    }
                },
                {
                    "$sort": {
                        "date": 1
                    }
                }
            ]
            data = await motor_aggregate(collection=settings.db_tables.INTREST_TABLE, query=pipeline)
            data = await data.to_list(None)

            ic(data)

            await convert_datetime_to_str(data)

            out = await fd_wise_intrest_with_indv_total(data)

            return out
        
        else:
            return "FD number not found"


    except Exception as e:
        return str(e)


@router.get("/future")
async def future_intrest_find(future_date: str, user_name: Literal["allen", "gladys"]):
    try:


        user_db = await motor_find_one(collection="users", query={"user_name": user_name})

        future_date = datetime.strptime(future_date, "%d-%m-%Y")
        ic(future_date)

        active_fds = await motor_find_all(collection="deposits", query={"user": user_db["_id"], "status": "ACTIVE"})
        active_fds = await active_fds.to_list(None)
        ic(active_fds)

        active_fd_num = [item["fd_number"] for item in active_fds]
        ic(active_fd_num)

        pipeline = [
            {
                "$match": {"fd_number": {"$in":active_fd_num}}
            },
            {
                "$sort": {"date": -1}
            },
            {
                "$group": {
                    "_id": "$fd_number",
                    "latest_record": {"$first": "$$ROOT"}
                }
            },
            {
                "$replaceRoot": {"newRoot": "$latest_record"}
            },
        ]

        # pipeline = [
        #     {"$match": {"fd_number": {"$in": fd_num}}},
        #     {"$facet": {
        #         "beforeGrouping": [
        #             {"$sort": {"date": -1}}
        #         ],
        #         "afterGrouping": [
        #             {"$sort": {"date": -1}},
        #             {"$group": {
        #                 "_id": "$fd_number",
        #                 "latest_record": {"$first": "$$ROOT"}
        #             }},
        #             {"$replaceRoot": {"newRoot": "$latest_record"}}
        #         ]
        #     }}
        # ]

        int_data = await motor_aggregate(collection=user_name, query=pipeline)
        int_data = await int_data.to_list(None)
        ic(int_data)

        int_data_fd_num = [item["fd_number"] for item in int_data]
        ic(int_data_fd_num)

        missing_fd_num = list(set(active_fd_num) ^ set(int_data_fd_num))
        ic(missing_fd_num)

        predicted_int = []
        for item in int_data:

            int_date = item["date"] + relativedelta(months=3)

            while int_date <= future_date:

                predicted_int.append(
                    {
                        "date": int_date,
                        "fd_number": item["fd_number"],
                        "intrest": item["intrest"]
                    }
                )

                int_date = int_date + relativedelta(months=3)
                
        ic(predicted_int)

        if missing_fd_num != []:

            await missing_deposits_int_find(missing_fd_num, future_date, predicted_int)
        
        predicted_int.sort(key=itemgetter('date'))

        await convert_datetime_to_str(predicted_int)

        total_interest = sum(item['intrest'] for item in predicted_int)
        predicted_int.append({"total_interest": total_interest})

        return predicted_int


    except Exception as e:
        return str(e)