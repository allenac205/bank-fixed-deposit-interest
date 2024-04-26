from icecream import ic
from crud import motor_find_all
from dateutil.relativedelta import relativedelta


async def missing_deposits_int_find(missing_fd_num, future_date, predicted_int):

    missing_depo = await motor_find_all(collection="deposits", query={"fd_number": {"$in": missing_fd_num}})
    missing_depo = await missing_depo.to_list(None)
    ic(missing_depo)

    for item in missing_depo:

        int_percent = item["current_intrest_rate"] / 100
        monthly_int =  (item["amount"] * int_percent) / 12
        thrd_mnth_int = monthly_int * 3

        int_date = item["created_date"] + relativedelta(months=3)

        while int_date <= future_date:

            predicted_int.append(
                {
                    "date": int_date,
                    "fd_number": item["fd_number"],
                    "intrest": thrd_mnth_int
                }
            )

            int_date = int_date + relativedelta(months=3)