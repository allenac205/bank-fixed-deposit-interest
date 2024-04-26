from database import MongoDbClient


async def motor_insert_one(collection, query):
    return await MongoDbClient.db[collection].insert_one(query)


async def motor_insert_many(collection, query):
    return await MongoDbClient.db[collection].insert_many(query)


async def motor_bulk_write(collection, query):
    return await MongoDbClient.db[collection].bulk_write(query)


async def motor_find_one(collection, query):

    # use for projection queries
    if (type(query)) == tuple:
        filter_statement, projection = query
        return await MongoDbClient.db[collection].find_one(filter_statement, projection)
    
    return await MongoDbClient.db[collection].find_one(query)


async def motor_find_all(collection, query):

    # use for projection queries
    if (type(query)) == tuple:
        filter_statement, projection = query
        return MongoDbClient.db[collection].find(filter_statement, projection)

    return MongoDbClient.db[collection].find(query)


async def motor_find_pagination(collection, query, page, limit):

    # use for projection queries
    if (type(query)) == tuple:
        filter_statement, projection = query
        return MongoDbClient.db[collection].find(filter_statement, projection).skip((page - 1) * limit).limit(limit)

    return MongoDbClient.db[collection].find(query).skip((page - 1) * limit).limit(limit)


async def motor_count_documents(collection, query):
    return await MongoDbClient.db[collection].count_documents(query)


async def motor_distinct(collection, query):
    if len(query) == 2:
        field_name, filter_operation = query
        return await MongoDbClient.db[collection].distinct(field_name, filter_operation)


async def motor_update_one(collection, query):
    if len(query) == 3:
        filter_operation, update_document,                                                                                                                                                                                                                                                                                                                                                                                                                       = query
        return await MongoDbClient.db[collection].update_one(filter_operation, update_document, upsert=upsert_value)

    elif len(query) == 2:
        filter_operation, update_document = query
        return await MongoDbClient.db[collection].update_one(filter_operation, update_document)


async def motor_update_many(collection, query):
    filter_operation, update_document = query
    return await MongoDbClient.db[collection].update_many(filter_operation, update_document)


async def motor_delete_one(collection, query):
    return await MongoDbClient.db[collection].delete_one(query)


async def motor_delete_many(collection, query):
    return await MongoDbClient.db[collection].delete_many(query)


async def motor_count(collection, query):
    return await MongoDbClient.db[collection].count_documents(query)


async def motor_aggregate(collection, query):
    return MongoDbClient.db[collection].aggregate(query)