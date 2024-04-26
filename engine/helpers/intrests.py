

async def total_intrest_only(data):
    
    total_sum = 0

    for item in data:
        total_sum = total_sum + item["intrest"]
    
    return {"total_intrest": total_sum}


async def total_intrest_with_fd(data):

    total_sum = await total_intrest_only(data)

    out = {
        "fd_details": data,
        "total_intrest": total_sum["total_intrest"]
    }

    return out


async def fd_wise_intrest(data):

    processed_data = {}

    for item in data:

        if item["fd_number"] not in processed_data:
            processed_data[item["fd_number"]] = []

        processed_data[item["fd_number"]].append(item)

    return processed_data


async def fd_wise_intrest_with_indv_total(data):
    
    fd_wise_data = await fd_wise_intrest(data)

    out = {}

    for fd in fd_wise_data:

        temp = {
            fd: {
                "details": None,
                "total_intrest": 0
            }
        }

        total_sum = await total_intrest_only(fd_wise_data[fd])

        temp[fd]["details"] = fd_wise_data[fd]
        temp[fd]["total_intrest"] = total_sum["total_intrest"]

        out.update(temp)
    
    return out


async def fd_wise_intrest_with_indv_total_intrest_only(data):
    
    fd_wise_data = await fd_wise_intrest(data)

    for fd in fd_wise_data:

        total_sum = await total_intrest_only(fd_wise_data[fd])

        fd_wise_data[fd] = total_sum
    
    return fd_wise_data