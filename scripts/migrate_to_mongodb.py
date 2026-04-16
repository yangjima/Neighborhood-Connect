import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

MONGODB_URL = "mongodb://localhost:27017"
DATABASE_NAME = "neighborhood_db"

# Sample rental data
RENTAL_DATA = [
    {
        "_id": "rental_1",
        "title": "精装两室一厅 南北通透",
        "type": "whole",
        "price": 3500,
        "area": 85.0,
        "location": {
            "community": "阳光小区",
            "address": "朝阳区望京街道",
            "district": "朝阳区",
            "coordinates": [116.4, 39.9]
        },
        "facilities": ["空调", "冰箱", "洗衣机", "热水器", "床", "沙发", "网络"],
        "images": ["https://picsum.photos/seed/house1/600/450"],
        "description": "房屋精装修，家具家电齐全，拎包入住。",
        "contact": "13800138001",
        "publisher_id": "user_1",
        "status": "available",
        "created_at": datetime.now().isoformat(),
        "view_count": 0,
        "favorite_count": 0
    },
    {
        "_id": "rental_2",
        "title": "温馨单间出租 朝南采光好",
        "type": "single",
        "price": 1800,
        "area": 20.0,
        "location": {
            "community": "幸福家园",
            "address": "海淀区中关村",
            "district": "海淀区",
            "coordinates": [116.3, 39.98]
        },
        "facilities": ["空调", "床", "衣柜", "网络"],
        "images": ["https://picsum.photos/seed/room1/600/450"],
        "description": "单间出租，面积20平，朝南，阳光充足。",
        "contact": "13800138002",
        "publisher_id": "user_2",
        "status": "available",
        "created_at": datetime.now().isoformat(),
        "view_count": 0,
        "favorite_count": 0
    }
]

# Sample trade data
TRADE_DATA = [
    {
        "_id": "item_1",
        "title": "九成新布艺沙发 3+1组合",
        "category": "furniture",
        "price": 1200,
        "condition": "like_new",
        "images": ["https://picsum.photos/seed/sofa1/600/450"],
        "description": "买了半年，使用次数不多。布艺可拆洗，质量很好。",
        "location": "朝阳区望京",
        "seller_id": "user_1",
        "status": "available",
        "created_at": datetime.now().isoformat(),
        "view_count": 0,
        "tags": ["沙发", "家具", "布艺"]
    },
    {
        "_id": "item_2",
        "title": "小米55寸智能电视",
        "category": "appliance",
        "price": 1800,
        "condition": "like_new",
        "images": ["https://picsum.photos/seed/tv1/600/450"],
        "description": "购买1年，画面清晰，系统流畅。",
        "location": "丰台区马家堡",
        "seller_id": "user_3",
        "status": "available",
        "created_at": datetime.now().isoformat(),
        "view_count": 0,
        "tags": ["电视", "家电", "小米"]
    }
]

async def migrate():
    """Migrate sample data to MongoDB"""
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]

    # Create indexes
    print("Creating indexes...")
    await db.rentals.create_index([("location.coordinates", "2dsphere")])
    await db.rentals.create_index([("price", 1)])
    await db.rentals.create_index([("created_at", -1)])
    await db.rentals.create_index([("status", 1)])

    await db.trade_items.create_index([("category", 1)])
    await db.trade_items.create_index([("price", 1)])
    await db.trade_items.create_index([("created_at", -1)])
    await db.trade_items.create_index([("status", 1)])

    # Insert rental data
    print("Migrating rental data...")
    await db.rentals.delete_many({})  # Clear existing
    if RENTAL_DATA:
        await db.rentals.insert_many(RENTAL_DATA)
    print(f"Inserted {len(RENTAL_DATA)} rentals")

    # Insert trade data
    print("Migrating trade data...")
    await db.trade_items.delete_many({})  # Clear existing
    if TRADE_DATA:
        await db.trade_items.insert_many(TRADE_DATA)
    print(f"Inserted {len(TRADE_DATA)} trade items")

    client.close()
    print("Migration completed!")

if __name__ == "__main__":
    asyncio.run(migrate())
