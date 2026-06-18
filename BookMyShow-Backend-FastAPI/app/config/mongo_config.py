from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_DATABASE_URL=os.getenv("MONGO_DATABASE_URL")
MONGO_DB=os.getenv("MONGO_DB")

client = AsyncIOMotorClient(MONGO_DATABASE_URL)
db = client[MONGO_DB]

def get_mongo_db():
    return db