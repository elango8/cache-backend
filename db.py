import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

client = AsyncIOMotorClient(os.getenv("MONGODB_URL"))
db = client[os.getenv("MONGODB_DB_NAME")]

print("✅ MongoDB Atlas connected")

def get_db():
    return db
