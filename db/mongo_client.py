from motor.motor_asyncio import AsyncIOMotorClient

MONGO_DETAILS = "mongodb+srv://pingmedia:kmBSuNAGq1aclhFU@ypd-cluster.6dddffx.mongodb.net/?retryWrites=true&w=majority&appName=YPD-Cluster"

client = None
database = None
sessions_collection = None

async def connect_to_mongo():
    global client, database, sessions_collection
    client = AsyncIOMotorClient(MONGO_DETAILS)
    database = client["cvp_lite_db"]
    sessions_collection = database.get_collection("sessions")

async def close_mongo_connection():
    global client
    if client:
        client.close()