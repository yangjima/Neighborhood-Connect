from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

_client: AsyncIOMotorClient = None
_database = None

async def get_database():
    """Get MongoDB database instance"""
    global _client, _database

    if _database is None:
        _client = AsyncIOMotorClient(settings.MONGODB_URL)
        _database = _client[settings.MONGODB_DB]

    return _database

async def close_database_connection():
    """Close MongoDB connection"""
    global _client, _database

    if _client is not None:
        _client.close()
        _client = None
        _database = None
