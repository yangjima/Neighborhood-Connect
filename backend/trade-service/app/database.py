from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional

_client: Optional[AsyncIOMotorClient] = None
_database = None

MONGODB_URL = "mongodb://localhost:27017"
DATABASE_NAME = "neighborhood_db"

async def get_database():
    """Get MongoDB database instance"""
    global _client, _database
    if _database is None:
        _client = AsyncIOMotorClient(MONGODB_URL)
        _database = _client[DATABASE_NAME]
    return _database

async def close_database():
    """Close MongoDB connection"""
    global _client
    if _client:
        _client.close()
