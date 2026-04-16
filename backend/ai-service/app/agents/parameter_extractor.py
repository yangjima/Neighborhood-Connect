# backend/ai-service/app/agents/parameter_extractor.py
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from app.models.state import ConversationState
from app.models.schemas import RentalParams, TradeParams
from app.config import settings
import json

llm = ChatOpenAI(
    model=settings.OPENAI_MODEL,
    temperature=settings.OPENAI_TEMPERATURE,
    api_key=settings.OPENAI_API_KEY
)

rental_schema = {
    "name": "extract_rental_params",
    "description": "从自然语言中提取租房参数",
    "parameters": {
        "type": "object",
        "properties": {
            "type": {"type": "string", "enum": ["whole", "shared", "single"], "description": "整租/合租/单间"},
            "location": {"type": "string", "description": "位置名称"},
            "min_price": {"type": "number", "description": "最低价格"},
            "max_price": {"type": "number", "description": "最高价格"},
            "min_area": {"type": "number", "description": "最小面积"},
            "max_area": {"type": "number", "description": "最大面积"},
            "facilities": {"type": "array", "items": {"type": "string"}, "description": "设施列表"}
        }
    }
}

trade_schema = {
    "name": "extract_trade_params",
    "description": "从自然语言中提取交易参数",
    "parameters": {
        "type": "object",
        "properties": {
            "category": {"type": "string", "enum": ["furniture", "appliance", "electronics"], "description": "商品类别"},
            "condition": {"type": "string", "enum": ["like_new", "good", "acceptable"], "description": "成色"},
            "location": {"type": "string", "description": "位置"},
            "min_price": {"type": "number", "description": "最低价格"},
            "max_price": {"type": "number", "description": "最高价格"}
        }
    }
}

async def parameter_extractor_agent(state: ConversationState) -> ConversationState:
    """Extract structured parameters from natural language query"""

    intent = state["intent"]

    if intent == "rental":
        schema = rental_schema
        system_msg = """你是参数提取专家。从用户查询中提取租房参数。

价格推断规则:
- "3000左右" → min_price: 2700, max_price: 3300 (±10%)
- "3000以下" → min_price: 0, max_price: 3000
- "3000-5000" → min_price: 3000, max_price: 5000

户型识别:
- "两室一厅"、"2室1厅" → 在description中匹配,不作为独立参数

只提取明确提到的参数,不要猜测。"""
    else:
        schema = trade_schema
        system_msg = """你是参数提取专家。从用户查询中提取交易参数。

类别映射:
- 沙发、床、桌子 → furniture
- 冰箱、空调、洗衣机 → appliance
- 电视、电脑、手机 → electronics

成色识别:
- 九成新、全新 → like_new
- 八成新、七成新 → good
- 六成新以下 → acceptable

只提取明确提到的参数。"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_msg),
        ("user", "{query}")
    ])

    chain = prompt | llm.bind(functions=[schema], function_call={"name": schema["name"]})

    try:
        response = await chain.ainvoke({"query": state["user_query"]})

        function_call = response.additional_kwargs.get("function_call", {})
        arguments = json.loads(function_call.get("arguments", "{}"))

        # Remove None values
        params = {k: v for k, v in arguments.items() if v is not None}

        state["extracted_params"] = params

    except Exception as e:
        state["error"] = f"Parameter extraction failed: {str(e)}"
        state["extracted_params"] = {}

    return state
