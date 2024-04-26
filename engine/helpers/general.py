

fy_dict = {
    "FY_2021_2022": {
        "start_date": "01-04-2021",
        "end_date": "31-03-2022"
    },
    "FY_2022_2023": {
        "start_date": "01-04-2022",
        "end_date": "31-03-2023"
    },
    "FY_2023_2024": {
        "start_date": "01-04-2023",
        "end_date": "31-03-2024"
    },
    "FY_2024_2025": {
        "start_date": "01-04-2024",
        "end_date": "31-03-2025"
    },
    "FY_2025_2026": {
        "start_date": "01-04-2025",
        "end_date": "31-03-2026"
    },
}


async def convert_datetime_to_str(data):

    for item in data:
        item["date"] = item["date"].strftime("%d %m %Y")