from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uvicorn
from app.database import get_database, close_database

app = FastAPI(title="Trade Service", version="1.0.0")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 内存数据存储（用于测试）
items_db = [
    {
        "id": "item_1",
        "title": "九成新布艺沙发 3+1组合",
        "category": "furniture",
        "price": 1200,
        "condition": "like_new",
        "images": ["https://picsum.photos/seed/sofa1/600/450", "https://picsum.photos/seed/sofa2/600/450"],
        "description": "买了半年，使用次数不多。布艺可拆洗，质量很好。因搬家低价转让。",
        "location": "朝阳区望京",
        "seller_id": "user_1",
        "status": "available",
        "created_at": datetime.now().isoformat()
    },
    {
        "id": "item_2",
        "title": "宜家汉尼斯书桌",
        "category": "furniture",
        "price": 350,
        "condition": "good",
        "images": ["https://picsum.photos/seed/desk1/600/450"],
        "description": "用了2年，有些轻微划痕，但不影响使用。桌面够大，适合办公学习。",
        "location": "海淀区中关村",
        "seller_id": "user_2",
        "status": "available",
        "created_at": datetime.now().isoformat()
    },
    {
        "id": "item_3",
        "title": "小米55寸智能电视",
        "category": "appliance",
        "price": 1800,
        "condition": "like_new",
        "images": ["https://picsum.photos/seed/tv1/600/450"],
        "description": "购买1年，画面清晰，系统流畅。因换大电视出售。",
        "location": "丰台区马家堡",
        "seller_id": "user_3",
        "status": "available",
        "created_at": datetime.now().isoformat()
    },
    {
        "id": "item_4",
        "title": "实木双人床+床垫",
        "category": "furniture",
        "price": 900,
        "condition": "good",
        "images": ["https://picsum.photos/seed/bed1/600/450"],
        "description": "实木框架，结实耐用。床垫是乳胶的，很舒服。",
        "location": "东城区东直门",
        "seller_id": "user_4",
        "status": "available",
        "created_at": datetime.now().isoformat()
    },
    {
        "id": "item_5",
        "title": "美的变频空调 1.5匹",
        "category": "appliance",
        "price": 1200,
        "condition": "like_new",
        "images": ["https://picsum.photos/seed/ac1/600/450"],
        "description": "去年购买，制冷制热效果都很好。移机出售，含安装费。",
        "location": "西城区西单",
        "seller_id": "user_5",
        "status": "available",
        "created_at": datetime.now().isoformat()
    },
    {
        "id": "item_6",
        "title": "九阳豆浆机 家用全自动",
        "category": "appliance",
        "price": 180,
        "condition": "good",
        "images": ["https://picsum.photos/seed/soymilk/600/450"],
        "description": "功能齐全，清洗方便。做早餐很实用。",
        "location": "朝阳区国贸",
        "seller_id": "user_6",
        "status": "available",
        "created_at": datetime.now().isoformat()
    },
    {
        "id": "item_7",
        "title": "儿童高低床 实木",
        "category": "furniture",
        "price": 1500,
        "condition": "good",
        "images": ["https://picsum.photos/seed/bunkbed/600/450"],
        "description": "二孩家庭必备，上面睡一个下面睡一个。质量很好，孩子大了用不上了。",
        "location": "昌平区回龙观",
        "seller_id": "user_7",
        "status": "available",
        "created_at": datetime.now().isoformat()
    },
    {
        "id": "item_8",
        "title": "西门子冰箱 对开门",
        "category": "appliance",
        "price": 3500,
        "condition": "like_new",
        "images": ["https://picsum.photos/seed/fridge1/600/450"],
        "description": "500多升大容量，变频压缩机。省电静音。",
        "location": "通州区梨园",
        "seller_id": "user_8",
        "status": "available",
        "created_at": datetime.now().isoformat()
    }
]

orders_db = []

# 数据模型
class TradeItemCreate(BaseModel):
    title: str
    category: str
    price: float
    condition: str
    images: List[str]
    description: str
    location: str

class OrderCreate(BaseModel):
    item_id: str

@app.get("/")
def read_root():
    return {"service": "Trade Service", "status": "running", "mode": "demo"}

@app.on_event("shutdown")
async def shutdown_event():
    await close_database()

@app.get("/api/trade/list")
async def get_items(
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=100),
    category: Optional[str] = None,
    condition: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None
):
    """Get trade items from MongoDB"""
    db = await get_database()
    collection = db.trade_items

    # Build query filter
    query_filter = {"status": "available"}

    if category:
        query_filter["category"] = category
    if condition:
        query_filter["condition"] = condition
    if min_price is not None:
        query_filter["price"] = query_filter.get("price", {})
        query_filter["price"]["$gte"] = min_price
    if max_price is not None and max_price < 999999:
        query_filter["price"] = query_filter.get("price", {})
        query_filter["price"]["$lte"] = max_price

    # Get total count
    total = await collection.count_documents(query_filter)

    # Get paginated results
    skip = (page - 1) * page_size
    cursor = collection.find(query_filter).skip(skip).limit(page_size).sort("created_at", -1)
    items = await cursor.to_list(length=page_size)

    # Convert ObjectId to string
    for item in items:
        item["_id"] = str(item["_id"])

    return {
        "data": items,
        "total": total,
        "page": page,
        "page_size": page_size
    }

@app.get("/api/trade/{item_id}")
def get_item(item_id: str):
    """获取商品详情"""
    item = next((i for i in items_db if i["id"] == item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="商品不存在")
    return item

@app.post("/api/trade/publish")
def publish_item(item: TradeItemCreate):
    """发布商品"""
    item_dict = item.dict()
    item_dict["id"] = f"item_{len(items_db) + 1}"
    item_dict["seller_id"] = "user_1"
    item_dict["status"] = "available"
    item_dict["created_at"] = datetime.now().isoformat()
    items_db.append(item_dict)
    return {"message": "发布成功", "id": item_dict["id"]}

@app.get("/api/trade/search")
def search_items(q: str = Query(..., min_length=1)):
    """搜索商品"""
    results = [
        i for i in items_db
        if q.lower() in i["title"].lower()
        or q.lower() in i["description"].lower()
    ]
    return {"data": results, "total": len(results)}

@app.post("/api/trade/order")
def create_order(order: OrderCreate):
    """创建订单"""
    item = next((i for i in items_db if i["id"] == order.item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="商品不存在")

    if item["status"] != "available":
        raise HTTPException(status_code=400, detail="商品已售出或不可用")

    order_dict = {
        "order_id": f"order_{len(orders_db) + 1}",
        "item_id": order.item_id,
        "item_type": "trade",
        "buyer_id": "user_1",
        "seller_id": item["seller_id"],
        "price": item["price"],
        "status": "pending",
        "created_at": datetime.now().isoformat()
    }
    orders_db.append(order_dict)
    item["status"] = "reserved"

    return {"message": "订单创建成功", "order_id": order_dict["order_id"]}

@app.get("/api/trade/order/{order_id}")
def get_order(order_id: str):
    """获取订单详情"""
    order = next((o for o in orders_db if o["order_id"] == order_id), None)
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    return order

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
