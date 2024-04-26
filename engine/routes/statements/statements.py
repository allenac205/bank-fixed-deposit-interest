import pandas as pd
from icecream import ic
from datetime import datetime

from fastapi import APIRouter, UploadFile
from typing import Literal

from crud import motor_insert_one, motor_find_one, motor_update_one
from settings import settings

from models import StatementDateRange

from helpers.statements import upload_deposit_int, insert_fd, cancel_fd, chk_stmnt_date


router = APIRouter()


@router.get("/db-statement-dates")
async def db_statement_dates(user_name: Literal["allen", "gladys"]):

    user_db = await motor_find_one(collection="users", query={"user_name": user_name})

    data = await motor_find_one(
        collection=settings.db_tables.STATEMENT_RANGES_TABLE,
        query=({"user": user_db["_id"]}, {"_id": 0, "user": 0, "timestamp": 0})
    )
    ic(data)
    data["start_date"] = data["start_date"].strftime("%d-%m-%Y %H:%M:%S")
    data["end_date"] = data["end_date"].strftime("%d-%m-%Y %H:%M:%S")
    
    return data


@router.post("/intrest")
async def get_total_intrest_from_xls(file: UploadFile):
    
    df = pd.read_excel(file.file)

    statement_name = df.iloc[0,1].strip()

    for index, row in df.iterrows():
        ic(row.values)
        if 'Date' in row.values:
            skip_rows = index
            break
    
    df = pd.read_excel(file.file, skiprows = skip_rows + 1)
    ic(df)
    
    filtered_rows = df[df['Remarks'].str.contains('int|renewal', case=False, na=False)]
    ic(filtered_rows)
    fd_sum = sum(filtered_rows["Deposits"].to_list())

    data = {
        "statement_of": statement_name,
        "total_intrest": fd_sum
    }

    return data


@router.post("/upload")
async def upload_statement(file: UploadFile, FY_year: Literal["CURRENT_FY", "FY_2021_2022", "FY_2022_2023", "FY_2023_2024", "FY_2024_2025", "FY_2025_2026"]):


    df = pd.read_excel(file.file)
    ic(df.head(20))

    statement_name = df.iloc[0, 1].strip()

    user_db = await motor_find_one(collection="users", query={"statement_name": statement_name})

    if await chk_stmnt_date(FY_year, df):

        if user_db:
        
            for index, row in df.iterrows():
                if 'Date' in row.values:
                    skip_rows = index
                    break

            df = pd.read_excel(file.file, skiprows = skip_rows + 1)
            ic(df)

            start_date = datetime.strptime(df.iloc[0]["Date"], '%d-%m-%Y %H:%M:%S')
            end_date = datetime.strptime(df.iloc[-1]["Date"], '%d-%m-%Y %H:%M:%S')
            ic(start_date, end_date)

            cur_st_range = await motor_find_one(collection="statement_ranges", query={"user": user_db["_id"]})
            ic(cur_st_range)

            if cur_st_range:

                updt_doc = {}

                if start_date < cur_st_range["start_date"]:
                    updt_doc = {"start_date": start_date}
                
                if end_date > cur_st_range["end_date"]:
                    updt_doc.update({"end_date": end_date})

                if updt_doc != {}:
                    st_range_rslt = await motor_update_one(
                        collection="statement_ranges",
                        query=({"user": user_db["_id"]}, {"$set": updt_doc})
                    )
                    ic(updt_doc, st_range_rslt)
                else:
                    pass

            else:

                st_range = StatementDateRange(
                    start_date = start_date,
                    end_date = end_date,
                    user = user_db["_id"]
                )
                st_range_rslt = await motor_insert_one(collection=settings.db_tables.STATEMENT_RANGES_TABLE, query=st_range.model_dump())
                ic(st_range_rslt)

            int_upld_upsert, int_upld_mod = await upload_deposit_int(df, user_db)

            fd_insert_upsert, fd_insert_mod = await insert_fd(df, user_db)

            fd_cancel_rslt = await cancel_fd(df, user_db)

            return {
                "statement_of": statement_name,
                "intrest_upserted_count": int_upld_upsert,
                "intrest_modified_count": int_upld_mod,
                "fd_upserted_count": fd_insert_upsert,
                "fd_modified_count": fd_insert_mod,
                "fd_cancel_count": fd_cancel_rslt
            }
        
        else:
            return "statement user not found, check the uploaded statement"
    
    else:
        return "Ops statement date range is not valid, it must start and end in a finacial year"