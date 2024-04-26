from motor.motor_asyncio import AsyncIOMotorClient


class MongoDbClient():
    url = "mongodb://localhost:27017"
    client = AsyncIOMotorClient(url)
    db = client.bank


MongoDbClient.db["users"].create_index("user_name", unique=True)