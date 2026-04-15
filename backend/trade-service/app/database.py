import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from pymongo.database import Database
from dotenv import load_dotenv

load_dotenv()

# MongoDB配置
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://admin:admin123@localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "neighborhood")

# 异步客户端
async_client: AsyncIOMotorClient = None
async_db = None

# 同步客户端
sync_client: MongoClient = None
sync_db: Database = None

def connect_mongodb():
    """同步连接MongoDB"""
    global sync_client, sync_db
    try:
        sync_client = MongoClient(MONGODB_URL)
        sync_db = sync_client[DATABASE_NAME]
        sync_client.admin.command('ping')
        print(f"[OK] MongoDB connected: {DATABASE_NAME}")
        return sync_db
    except Exception as e:
        print(f"[FAIL] MongoDB connection failed: {e}")
        return None

async def init_async_mongodb():
    """异步连接MongoDB"""
    global async_client, async_db
    try:
        async_client = AsyncIOMotorClient(MONGODB_URL)
        async_db = async_client[DATABASE_NAME]
        await async_client.admin.command('ping')
        print(f"[OK] Async MongoDB connected: {DATABASE_NAME}")
        return async_db
    except Exception as e:
        print(f"[FAIL] Async MongoDB connection failed: {e}")
        return None

def close_mongodb():
    """关闭MongoDB连接"""
    global sync_client, async_client
    if sync_client:
        sync_client.close()
    if async_client:
        async_client.close()

def get_collection(name: str):
    """获取集合"""
    if sync_db:
        return sync_db[name]
    return None

# 集合名称
TRADE_ITEMS_COLLECTION = "trade_items"
ORDERS_COLLECTION = "orders"
MESSAGES_COLLECTION = "messages"
