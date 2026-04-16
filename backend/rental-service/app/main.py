from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uvicorn
from app.database import get_database, close_database

app = FastAPI(title="Rental Service", version="1.0.0")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 内存数据存储（用于测试）
rentals_db = [
    {
        "id": "rental_1",
        "title": "精装两室一厅 南北通透",
        "type": "whole",
        "price": 3500,
        "area": 85.0,
        "location": {"community": "阳光小区", "address": "朝阳区望京街道", "coordinates": [116.4, 39.9]},
        "facilities": ["空调", "冰箱", "洗衣机", "热水器", "床", "沙发", "网络"],
        "images": ["https://picsum.photos/seed/house1/600/450", "https://picsum.photos/seed/house1b/600/450"],
        "description": "房屋精装修，家具家电齐全，拎包入住。小区环境优美，配套齐全，交通便利。",
        "contact": "13800138001",
        "publisher_id": "user_1",
        "status": "available",
        "created_at": datetime.now().isoformat()
    },
    {
        "id": "rental_2",
        "title": "温馨单间出租 朝南采光好",
        "type": "single",
        "price": 1800,
        "area": 20.0,
        "location": {"community": "幸福家园", "address": "海淀区中关村", "coordinates": [116.3, 39.98]},
        "facilities": ["空调", "床", "衣柜", "网络"],
        "images": ["https://picsum.photos/seed/room1/600/450"],
        "description": "单间出租，面积20平，朝南，阳光充足。适合单身人士或学生。",
        "contact": "13800138002",
        "publisher_id": "user_2",
        "status": "available",
        "created_at": datetime.now().isoformat()
    },
    {
        "id": "rental_3",
        "title": "主卧带独卫 限女生",
        "type": "shared",
        "price": 2200,
        "area": 30.0,
        "location": {"community": "绿城花园", "address": "丰台区马家堡", "coordinates": [116.35, 39.85]},
        "facilities": ["空调", "床", "独卫", "热水器"],
        "images": ["https://picsum.photos/seed/room2/600/450"],
        "description": "合租主卧，有独立卫生间，限女生入住。室友均为年轻白领，好相处。",
        "contact": "13800138003",
        "publisher_id": "user_3",
        "status": "available",
        "created_at": datetime.now().isoformat()
    },
    {
        "id": "rental_4",
        "title": "整租一居室 地铁旁",
        "type": "whole",
        "price": 4200,
        "area": 55.0,
        "location": {"community": "地铁家园", "address": "东城区东直门", "coordinates": [116.43, 39.94]},
        "facilities": ["空调", "冰箱", "洗衣机", "床", "电视"],
        "images": ["https://picsum.photos/seed/apt1/600/450"],
        "description": "紧邻地铁站，出行方便。房屋新装修，设施新。",
        "contact": "13800138004",
        "publisher_id": "user_4",
        "status": "available",
        "created_at": datetime.now().isoformat()
    },
    {
        "id": "rental_5",
        "title": "次卧招租 近商场",
        "type": "shared",
        "price": 1600,
        "area": 18.0,
        "location": {"community": "购物广场", "address": "西城区西单", "coordinates": [116.37, 39.91]},
        "facilities": ["空调", "床", "衣柜"],
        "images": ["https://picsum.photos/seed/room3/600/450"],
        "description": "次卧招租，附近有大型商场，生活便利。",
        "contact": "13800138005",
        "publisher_id": "user_5",
        "status": "available",
        "created_at": datetime.now().isoformat()
    },
    {
        "id": "rental_6",
        "title": "豪华三室 精装修",
        "type": "whole",
        "price": 6800,
        "area": 120.0,
        "location": {"community": "金隅嘉华", "address": "朝阳区国贸", "coordinates": [116.45, 39.91]},
        "facilities": ["空调", "冰箱", "洗衣机", "热水器", "床", "沙发", "电视", "网络", "暖气"],
        "images": ["https://picsum.photos/seed/villa1/600/450"],
        "description": "高档小区，豪华装修，品牌家具家电。管家式物业服务。",
        "contact": "13800138006",
        "publisher_id": "user_6",
        "status": "available",
        "created_at": datetime.now().isoformat()
    }
]

favorites_db = []

appointments_db = []

# 数据模型
class Location(BaseModel):
    community: str
    address: str
    coordinates: Optional[List[float]] = None

class RentalCreate(BaseModel):
    title: str
    type: str
    price: float
    area: float
    location: Location
    facilities: List[str]
    images: List[str]
    description: str
    contact: str

class FavoriteRequest(BaseModel):
    rental_id: str

class AppointmentRequest(BaseModel):
    rental_id: str
    name: str
    phone: str
    visit_time: str
    message: Optional[str] = None

@app.get("/")
def read_root():
    return {"service": "Rental Service", "status": "running", "mode": "demo"}

@app.on_event("shutdown")
async def shutdown_event():
    await close_database()

@app.get("/api/rental/list")
async def get_rentals(
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=100),
    type: Optional[str] = None,
    location: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None
):
    """Get rental listings from MongoDB"""
    db = await get_database()
    collection = db.rentals

    # Build query filter
    query_filter = {"status": "available"}

    if type:
        query_filter["type"] = type
    if location:
        query_filter["location.community"] = {"$regex": location, "$options": "i"}
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

@app.get("/api/rental/{rental_id}")
def get_rental(rental_id: str):
    """获取房源详情"""
    rental = next((r for r in rentals_db if r["id"] == rental_id), None)
    if not rental:
        raise HTTPException(status_code=404, detail="房源不存在")
    return rental

@app.post("/api/rental/publish")
def publish_rental(rental: RentalCreate):
    """发布房源"""
    rental_dict = rental.dict()
    rental_dict["id"] = f"rental_{len(rentals_db) + 1}"
    rental_dict["publisher_id"] = "user_1"
    rental_dict["status"] = "available"
    rental_dict["created_at"] = datetime.now().isoformat()
    rentals_db.append(rental_dict)
    return {"message": "发布成功", "id": rental_dict["id"]}

@app.get("/api/rental/search")
def search_rentals(q: str = Query(..., min_length=1)):
    """搜索房源"""
    results = [
        r for r in rentals_db
        if q.lower() in r["title"].lower()
        or q.lower() in r["description"].lower()
        or q.lower() in r["location"]["community"].lower()
    ]
    return {"data": results, "total": len(results)}

@app.post("/api/rental/favorite")
def favorite_rental(request: FavoriteRequest):
    """收藏房源"""
    favorite = {"rental_id": request.rental_id, "user_id": "user_1", "created_at": datetime.now().isoformat()}
    favorites_db.append(favorite)
    return {"message": "收藏成功"}

@app.post("/api/rental/appointment")
def create_appointment(request: AppointmentRequest):
    """预约看房"""
    appointment = {
        "rental_id": request.rental_id,
        "name": request.name,
        "phone": request.phone,
        "visit_time": request.visit_time,
        "message": request.message,
        "status": "pending",
        "created_at": datetime.now().isoformat()
    }
    appointments_db.append(appointment)
    return {"message": "预约成功", "id": f"apt_{len(appointments_db)}"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
