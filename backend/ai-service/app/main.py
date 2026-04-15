from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import os
import uvicorn

app = FastAPI(title="AI Service", version="1.0.0")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据模型
class RentalInput(BaseModel):
    title: str
    type: str
    area: float
    location: str
    facilities: List[str]
    images: List[str] = []

class GenerateDescriptionRequest(BaseModel):
    rental: Optional[RentalInput] = None
    item_title: Optional[str] = None
    item_condition: Optional[str] = None

class ContentModerationRequest(BaseModel):
    content: str

class RecommendationRequest(BaseModel):
    user_id: str
    category: str  # rental, trade
    limit: int = 5

# LangGraph 工作流定义
from typing import TypedDict

class AIGraphState(TypedDict):
    input_data: dict
    generated_content: str
    is_safe: bool
    feedback: str

def analyze_content(state: AIGraphState) -> AIGraphState:
    """分析输入内容"""
    input_data = state["input_data"]

    # 检测违规内容
    sensitive_words = ["赌博", "色情", "诈骗", "违法"]
    content_to_check = str(input_data).lower()

    for word in sensitive_words:
        if word in content_to_check:
            state["is_safe"] = False
            state["feedback"] = f"检测到敏感词: {word}"
            return state

    state["is_safe"] = True
    state["feedback"] = "内容审核通过"
    return state

def generate_content(state: AIGraphState) -> AIGraphState:
    """生成描述内容"""
    input_data = state["input_data"]

    # 简单模板生成（生产环境应使用LLM）
    if "rental" in input_data:
        rental = input_data["rental"]
        description = f"""
🏠 {rental.get('title', '优质房源')}

📍 位置：{rental.get('location', '核心地段')}

📐 面积：{rental.get('area', 0)}平方米

🏷️ 类型：{rental.get('type', '整租')}

✨ 亮点：
"""
        for facility in input_data.get("facilities", []):
            description += f"- {facility}\n"

        description += f"""
📝 这是一套精心维护的房源，位置优越，交通便利，周边配套齐全。适合家庭居住或办公使用。

欢迎来电咨询！
"""
        state["generated_content"] = description
    elif "item" in input_data:
        item = input_data["item"]
        description = f"""
🛋️ {item.get('title', '二手好物')}

💰 价格：¥{item.get('price', 0)}

📦 成色：{item.get('condition', '九成新')}

📍 位置：{item.get('location', '本地自提')}

💬 描述：{item.get('description', '品质优良，价格实惠')}

有需要的朋友可以联系我！
"""
        state["generated_content"] = description
    else:
        state["generated_content"] = "内容生成完成"

    return state

# 创建工作流
workflow = StateGraph(state_schema=AIGraphState)
workflow.add_node("analyze", analyze_content)
workflow.add_node("generate", generate_content)
workflow.set_entry_point("analyze")
workflow.add_edge("analyze", "generate")
workflow.add_edge("generate", END)

graph = workflow.compile()

@app.get("/")
def read_root():
    return {"service": "AI Service", "status": "running", "model": "LangGraph"}

@app.post("/api/ai/generate-description")
async def generate_description(request: GenerateDescriptionRequest):
    """使用AI生成房源或商品描述"""
    try:
        input_data = {}
        if request.rental:
            input_data["rental"] = request.rental.dict()
        if request.item_title:
            input_data["item"] = {
                "title": request.item_title,
                "condition": request.item_condition
            }

        result = await graph.ainvoke({
            "input_data": input_data,
            "generated_content": "",
            "is_safe": True,
            "feedback": ""
        })

        if not result["is_safe"]:
            return {
                "success": False,
                "message": result["feedback"],
                "content": None
            }

        return {
            "success": True,
            "message": "生成成功",
            "content": result["generated_content"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai/moderate")
async def moderate_content(request: ContentModerationRequest):
    """内容审核"""
    sensitive_words = ["赌博", "色情", "诈骗", "违法", "毒品"]
    content = request.content.lower()

    found = []
    for word in sensitive_words:
        if word in content:
            found.append(word)

    if found:
        return {
            "is_safe": False,
            "flagged_words": found,
            "message": f"检测到敏感词: {', '.join(found)}"
        }

    return {
        "is_safe": True,
        "flagged_words": [],
        "message": "内容审核通过"
    }

@app.post("/api/ai/recommend")
async def recommend(request: RecommendationRequest):
    """智能推荐（简化版）"""
    # 生产环境应结合用户历史行为和机器学习模型
    recommendations = []

    if request.category == "rental":
        recommendations = [
            {"id": "rental_1", "score": 0.95, "reason": "热门房源"},
            {"id": "rental_2", "score": 0.88, "reason": "性价比高"},
            {"id": "rental_3", "score": 0.82, "reason": "新上架"}
        ]
    elif request.category == "trade":
        recommendations = [
            {"id": "item_1", "score": 0.92, "reason": "热门商品"},
            {"id": "item_2", "score": 0.85, "reason": "成色好"}
        ]

    return {
        "user_id": request.user_id,
        "category": request.category,
        "recommendations": recommendations[:request.limit]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)
