from icecream import ic
from datetime import datetime
from models import Intrests, Deposits
from crud import motor_bulk_write, motor_aggregate
from pymongo import UpdateOne
import datetime as dt
from helpers.general import fy_dict


async def get_fd_num(remark):
    fd_num = remark.split(":")[0]
    fd_num = fd_num.split()[0]

    if fd_num.isdigit() == False:
        fd_num = remark.split()[-1][1:-1]

    return fd_num


async def get_current_financial_year():
    today = dt.date.today()
    ic(today)

    if today.month < 4:  # Financial year starts from April
        year_frm, year_to =  str(today.year - 1), str(today.year)
    else:
        year_frm, year_to = str(today.year), str(today.year + 1)
    
    ic(year_frm, year_to)

    fy_strt = "01-04-" + year_frm
    fy_end = "31-03-" + year_to
    ic(fy_strt, fy_end)
    return fy_strt, fy_end


async def chk_stmnt_date(FY_year, df):

    if FY_year == "CURRENT_FY":
        fy_strt, fy_end = await get_current_financial_year()
    else:
        fy_strt, fy_end = fy_dict[FY_year]["start_date"], fy_dict[FY_year]["end_date"]

    st_frm, st_to = df.iloc[10, 7].replace("/", "-"), df.iloc[10, 9].replace("/", "-")
    ic(st_frm, st_to)

    if fy_strt == st_frm and fy_end == st_to:
        return True
    else:
        return False


async def upload_deposit_int(df, user_db):

    filtered_rows = df[df['Remarks'].str.contains('int|renewal', case=False, na=False)]
    ic(filtered_rows)

    if not filtered_rows.empty:

        operations = []
        for _, row in filtered_rows.iterrows():
            fd_number = await get_fd_num(row["Remarks"])

            intrest = Intrests(
                date = datetime.strptime(row['Date'].split()[0], "%d-%m-%Y"),
                fd_number = fd_number,
                intrest = row["Deposits"],
                user = user_db["_id"]
            )
            ic(intrest)

            operation = UpdateOne({"date": intrest.date, "fd_number": fd_number}, {"$set": intrest.model_dump()}, upsert=True)
            operations.append(operation)

        result = await motor_bulk_write(collection="intrests", query=operations)

        return result.upserted_count, result.modified_count
    
    else:
        return 0, 0


async def insert_fd(df, user_db):

    filtered_rows = df[df['Remarks'].str.contains('Dr. Tran for funding A/c', case=False, na=False)]
    ic(filtered_rows)

    if not filtered_rows.empty:

        operations = []
        for _, row in filtered_rows.iterrows():

            fd_number = row["Remarks"].split()[-1]

            deposit = Deposits(
                fd_number = fd_number,
                created_date = datetime.strptime(row['Date'].split()[0], "%d-%m-%Y"),
                amount = row["Withdrawals"],
                user = user_db["_id"]
            )
            ic(deposit)

            operation = UpdateOne({"created_date": deposit.created_date, "fd_number": fd_number}, {"$set": deposit.model_dump()}, upsert=True)
            operations.append(operation)

        result =  await motor_bulk_write(collection="deposits", query=operations)

        return result.upserted_count, result.modified_count

    else:
        return 0, 0


async def cancel_fd(df, user_db):

    filtered_rows = df[df['Remarks'].str.contains('repayment credit', case=False, na=False)]
    ic(filtered_rows)

    if not filtered_rows.empty:
        
        operations = []
        for _, row in filtered_rows.iterrows():

            fd_number = await get_fd_num(row["Remarks"])

            operation = UpdateOne({"fd_number": fd_number, "user": user_db["_id"]}, {"$set": {"status": "CANCELLED", "cancelled_date": datetime.strptime(row['Date'].split()[0], "%d-%m-%Y")}}, upsert=True)
            operations.append(operation)
        ic(operations)
        
        result = await motor_bulk_write(collection="deposits", query=operations)

        return result.modified_count
    
    else:
        return 0


async def get_available_statement_dates(user_name):

    pipeline = [
        {
            "$group": {
                "_id": None,
                "from": { "$min": "$date" },
                "to": { "$max": "$date" }
            }
        },
        {
            "$project": {
                "_id": 0,
            }
        },
    ]
    int_data = await motor_aggregate(collection="intrests", query=pipeline)
    int_data = await int_data.to_list(None)
    ic(int_data)

    pipeline = [
        {
            "$group": {
                "_id": None,
                "from": { "$min": "$created_date" },
                "to": { "$max": "$created_date" }
            }
        },
        {
            "$project": {
                "_id": 0,
            }
        },
    ]
    depo_data = await motor_aggregate(collection="deposits", query=pipeline)
    depo_data = await depo_data.to_list(None)
    ic(depo_data)

    if int_data != [] or depo_data != []:

        stmnt_dates = list(int_data[0].values()) + list(depo_data[0].values())
        ic(stmnt_dates)
        
        data = {
            "from": min(stmnt_dates),
            "to": max(stmnt_dates)
        }
    
    else:

        data = {
            "from": datetime(2021, 1, 1),
            "to": datetime(2021, 1, 1)
        }

    return data