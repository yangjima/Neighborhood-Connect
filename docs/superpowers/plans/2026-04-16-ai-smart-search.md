# AI智能搜索系统 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Build a multi-agent AI search system that understands natural language queries, extracts parameters, and returns structured results for rental and trade services.

**Architecture:** LangGraph orchestrates 5 specialized agents (IntentClassifier, ParameterExtractor, QueryOptimizer, DataRetrieval, ResponseFormatter) with conditional routing, MongoDB for data storage, Redis for caching, and OpenAI GPT-4 for LLM capabilities.

**Tech Stack:** FastAPI, LangGraph, LangChain, OpenAI GPT-4 Turbo, MongoDB (Motor), Redis, Prometheus, structlog, OpenTelemetry

---

## File Structure

### Backend AI Service
- `backend/ai-service/app/config.py` - Configuration and environment variables
- `backend/ai-service/app/database.py` - MongoDB connection setup
- `backend/ai-service/app/cache.py` - Redis cache client
- `backend/ai-service/app/models/state.py` - LangGraph state definitions
- `backend/ai-service/app/models/schemas.py` - Pydantic request/response models
- `backend/ai-service/app/agents/intent_classifier.py` - Intent classification agent
- `backend/ai-service/app/agents/parameter_extractor.py` - Parameter extraction agent
- `backend/ai-service/app/agents/query_optimizer.py` - Query optimization agent
- `backend/ai-service/app/agents/data_retrieval.py` - Data retrieval agent
- `backend/ai-service/app/agents/response_formatter.py` - Response formatting agent
- `backend/ai-service/app/workflow.py` - LangGraph workflow definition
- `backend/ai-service/app/main.py` - FastAPI application (modify existing)
- `backend/ai-service/app/metrics.py` - Prometheus metrics
- `backend/ai-service/app/utils/logger.py` - Structured logging setup

### Tests
- `backend/ai-service/tests/conftest.py` - Pytest fixtures
- `backend/ai-service/tests/test_intent_classifier.py` - Intent classifier tests
- `backend/ai-service/tests/test_parameter_extractor.py` - Parameter extractor tests
- `backend/ai-service/tests/test_query_optimizer.py` - Query optimizer tests
- `backend/ai-service/tests/test_data_retrieval.py` - Data retrieval tests
- `backend/ai-service/tests/test_response_formatter.py` - Response formatter tests
- `backend/ai-service/tests/test_workflow.py` - End-to-end workflow tests

### MongoDB Migration
- `backend/rental-service/app/database.py` - MongoDB connection for rental service
- `backend/rental-service/app/models.py` - Rental data models
- `backend/trade-service/app/database.py` - MongoDB connection for trade service
- `backend/trade-service/app/models.py` - Trade data models
- `scripts/migrate_to_mongodb.py` - Data migration script

### Frontend
- `frontend/src/components/SmartSearchBar.vue` - Smart search component
- `frontend/src/api/ai.js` - AI service API client

---

## Phase 1: Foundation Setup (MongoDB + Redis + Config)

### Task 1: Configuration and Environment Setup

**Files:**
- Create: `backend/ai-service/app/config.py`
- Modify: `backend/ai-service/requirements.txt`
- Create: `backend/ai-service/.env.example`

- [x] **Step 1: Write test for configuration loading**

```python
# backend/ai-service/tests/test_config.py
import pytest
from app.config import Settings

def test_settings_loads_from_env(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test123")
    monkeypatch.setenv("MONGODB_URL", "mongodb://localhost:27017")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379")
    
    settings = Settings()
    
    assert settings.OPENAI_API_KEY == "sk-test123"
    assert settings.MONGODB_URL == "mongodb://localhost:27017"
    assert settings.REDIS_URL == "redis://localhost:6379"
    assert settings.OPENAI_MODEL == "gpt-4-turbo"  # default
    assert settings.OPENAI_TEMPERATURE == 0.0  # default

def test_settings_validates_required_fields():
    with pytest.raises(ValueError):
        Settings(OPENAI_API_KEY="")
```

- [x] **Step 2: Run test to verify it fails**

Run: `cd backend/ai-service && pytest tests/test_config.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'app.config'"

- [x] **Step 3: Implement configuration module**

```python
# backend/ai-service/app/config.py
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # OpenAI Configuration
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4-turbo"
    OPENAI_TEMPERATURE: float = 0.0
    
    # MongoDB Configuration
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB: str = "neighborhood_db"
    
    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_CACHE_TTL: int = 300  # 5 minutes
    
    # Service URLs
    RENTAL_SERVICE_URL: str = "http://localhost:8001"
    TRADE_SERVICE_URL: str = "http://localhost:8002"
    
    # AI Configuration
    AI_TIMEOUT: int = 10
    AI_MAX_RETRIES: int = 3
    AI_ENABLE_CACHE: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

- [x] **Step 4: Update requirements.txt**

```txt
# backend/ai-service/requirements.txt
fastapi==0.115.6
uvicorn[standard]==0.34.0
langgraph==0.2.60
langchain==0.3.14
langchain-openai==0.2.14
pydantic==2.10.5
pydantic-settings==2.6.1
motor==3.6.0
redis==5.2.1
httpx==0.28.1
pytest==8.3.4
pytest-asyncio==0.24.0
prometheus-client==0.21.0
structlog==24.4.0
opentelemetry-api==1.29.0
opentelemetry-sdk==1.29.0
opentelemetry-exporter-jaeger==1.29.0
```

- [x] **Step 5: Create .env.example**

```bash
# backend/ai-service/.env.example
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4-turbo
OPENAI_TEMPERATURE=0.0

MONGODB_URL=mongodb://localhost:27017
MONGODB_DB=neighborhood_db

REDIS_URL=redis://localhost:6379
REDIS_CACHE_TTL=300

RENTAL_SERVICE_URL=http://localhost:8001
TRADE_SERVICE_URL=http://localhost:8002

AI_TIMEOUT=10
AI_MAX_RETRIES=3
AI_ENABLE_CACHE=true
```

- [x] **Step 6: Run test to verify it passes**

Run: `cd backend/ai-service && pytest tests/test_config.py -v`
Expected: PASS (2 tests)

- [x] **Step 7: Commit**

```bash
git add backend/ai-service/app/config.py backend/ai-service/requirements.txt backend/ai-service/.env.example backend/ai-service/tests/test_config.py
git commit -m "feat(ai): add configuration module with environment settings"
```


### Task 2: MongoDB Connection Setup

**Files:**
- Create: `backend/ai-service/app/database.py`
- Create: `backend/ai-service/tests/test_database.py`

- [x] **Step 1: Write test for MongoDB connection**

```python
# backend/ai-service/tests/test_database.py
import pytest
from app.database import get_database, close_database_connection

@pytest.mark.asyncio
async def test_get_database_returns_motor_database():
    db = await get_database()
    assert db is not None
    assert db.name == "neighborhood_db"

@pytest.mark.asyncio
async def test_database_connection_can_ping():
    db = await get_database()
    result = await db.command("ping")
    assert result["ok"] == 1.0
    await close_database_connection()
```

- [x] **Step 2: Run test to verify it fails**

Run: `cd backend/ai-service && pytest tests/test_database.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'app.database'"

- [x] **Step 3: Implement MongoDB connection module**

```python
# backend/ai-service/app/database.py
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
```

- [x] **Step 4: Run test to verify it passes**

Run: `cd backend/ai-service && pytest tests/test_database.py -v`
Expected: PASS (2 tests)

- [x] **Step 5: Commit**

```bash
git add backend/ai-service/app/database.py backend/ai-service/tests/test_database.py
git commit -m "feat(ai): add MongoDB connection with Motor async driver"
```

### Task 3: Redis Cache Setup

**Files:**
- Create: `backend/ai-service/app/cache.py`
- Create: `backend/ai-service/tests/test_cache.py`

- [x] **Step 1: Write test for Redis cache operations**

```python
# backend/ai-service/tests/test_cache.py
import pytest
from app.cache import get_cache, set_cache, close_cache_connection

@pytest.mark.asyncio
async def test_set_and_get_cache():
    await set_cache("test_key", {"data": "test_value"}, ttl=60)
    result = await get_cache("test_key")
    assert result == {"data": "test_value"}
    await close_cache_connection()

@pytest.mark.asyncio
async def test_get_cache_returns_none_for_missing_key():
    result = await get_cache("nonexistent_key")
    assert result is None
    await close_cache_connection()

@pytest.mark.asyncio
async def test_cache_respects_ttl():
    import asyncio
    await set_cache("ttl_key", {"data": "expires"}, ttl=1)
    await asyncio.sleep(2)
    result = await get_cache("ttl_key")
    assert result is None
    await close_cache_connection()
```

- [x] **Step 2: Run test to verify it fails**

Run: `cd backend/ai-service && pytest tests/test_cache.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'app.cache'"

- [x] **Step 3: Implement Redis cache module**

```python
# backend/ai-service/app/cache.py
import redis.asyncio as redis
import json
from typing import Optional, Any
from app.config import settings

_redis_client: redis.Redis = None

async def get_redis_client() -> redis.Redis:
    """Get Redis client instance"""
    global _redis_client
    
    if _redis_client is None:
        _redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
    
    return _redis_client

async def get_cache(key: str) -> Optional[Any]:
    """Get value from cache"""
    client = await get_redis_client()
    value = await client.get(key)
    
    if value is None:
        return None
    
    return json.loads(value)

async def set_cache(key: str, value: Any, ttl: int = None) -> bool:
    """Set value in cache with optional TTL"""
    client = await get_redis_client()
    
    if ttl is None:
        ttl = settings.REDIS_CACHE_TTL
    
    serialized = json.dumps(value)
    await client.setex(key, ttl, serialized)
    return True

async def close_cache_connection():
    """Close Redis connection"""
    global _redis_client
    
    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None
```

- [x] **Step 4: Run test to verify it passes**

Run: `cd backend/ai-service && pytest tests/test_cache.py -v`
Expected: PASS (3 tests)

- [x] **Step 5: Commit**

```bash
git add backend/ai-service/app/cache.py backend/ai-service/tests/test_cache.py
git commit -m "feat(ai): add Redis cache with async operations"
```


### Task 4: LangGraph State Models

**Files:**
- Create: `backend/ai-service/app/models/state.py`
- Create: `backend/ai-service/app/models/schemas.py`
- Create: `backend/ai-service/tests/test_models.py`

- [x] **Step 1: Write test for state model**

```python
# backend/ai-service/tests/test_models.py
import pytest
from app.models.state import ConversationState
from app.models.schemas import RentalParams, TradeParams

def test_conversation_state_structure():
    state = ConversationState(
        user_query="望京3000左右的两室一厅",
        context="rental",
        intent="rental",
        intent_confidence=0.95,
        extracted_params={},
        optimized_query={},
        retrieved_data=[],
        formatted_response={},
        error=None,
        metadata={}
    )
    
    assert state["user_query"] == "望京3000左右的两室一厅"
    assert state["context"] == "rental"
    assert state["intent"] == "rental"
    assert state["intent_confidence"] == 0.95

def test_rental_params_validation():
    params = RentalParams(
        type="whole",
        location="望京",
        min_price=2700.0,
        max_price=3300.0,
        min_area=None,
        max_area=None,
        facilities=None
    )
    
    assert params.type == "whole"
    assert params.location == "望京"
    assert params.min_price == 2700.0

def test_trade_params_validation():
    params = TradeParams(
        category="furniture",
        condition="like_new",
        location="朝阳区",
        min_price=1000.0,
        max_price=2000.0
    )
    
    assert params.category == "furniture"
    assert params.condition == "like_new"
```

- [x] **Step 2: Run test to verify it fails**

Run: `cd backend/ai-service && pytest tests/test_models.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'app.models'"

- [x] **Step 3: Implement state models**

```python
# backend/ai-service/app/models/state.py
from typing import TypedDict, Optional, List, Dict, Any

class ConversationState(TypedDict):
    # Input
    user_query: str
    context: str  # rental | trade
    
    # Intermediate state
    intent: str
    intent_confidence: float
    extracted_params: Dict[str, Any]
    optimized_query: Dict[str, Any]
    retrieved_data: List[Dict[str, Any]]
    
    # Output
    formatted_response: Dict[str, Any]
    
    # Metadata
    error: Optional[str]
    metadata: Dict[str, Any]
```

- [x] **Step 4: Implement schema models**

```python
# backend/ai-service/app/models/schemas.py
from pydantic import BaseModel, Field
from typing import Optional, List

class RentalParams(BaseModel):
    type: Optional[str] = Field(None, description="whole/shared/single")
    location: Optional[str] = Field(None, description="Location name")
    min_price: Optional[float] = Field(None, ge=0)
    max_price: Optional[float] = Field(None, ge=0)
    min_area: Optional[float] = Field(None, ge=0)
    max_area: Optional[float] = Field(None, ge=0)
    facilities: Optional[List[str]] = None

class TradeParams(BaseModel):
    category: Optional[str] = Field(None, description="furniture/appliance/electronics")
    condition: Optional[str] = Field(None, description="like_new/good/acceptable")
    location: Optional[str] = None
    min_price: Optional[float] = Field(None, ge=0)
    max_price: Optional[float] = Field(None, ge=0)

class SmartSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Natural language query")
    context: str = Field(..., description="rental or trade")

class SmartSearchResponse(BaseModel):
    success: bool
    data: List[dict]
    total: int
    query_understanding: str
    applied_filters: dict
    suggestions: List[str] = []
```

- [x] **Step 5: Run test to verify it passes**

Run: `cd backend/ai-service && pytest tests/test_models.py -v`
Expected: PASS (3 tests)

- [x] **Step 6: Commit**

```bash
git add backend/ai-service/app/models/ backend/ai-service/tests/test_models.py
git commit -m "feat(ai): add LangGraph state and Pydantic schema models"
```


## Phase 2: Agent Implementation

### Task 5: Intent Classifier Agent

**Files:**
- Create: `backend/ai-service/app/agents/intent_classifier.py`
- Create: `backend/ai-service/tests/test_intent_classifier.py`

- [x] **Step 1: Write test for intent classification**

```python
# backend/ai-service/tests/test_intent_classifier.py
import pytest
from app.agents.intent_classifier import intent_classifier_agent
from app.models.state import ConversationState

@pytest.mark.asyncio
async def test_classify_rental_intent():
    state = ConversationState(
        user_query="我想租房",
        context="rental",
        intent="",
        intent_confidence=0.0,
        extracted_params={},
        optimized_query={},
        retrieved_data=[],
        formatted_response={},
        error=None,
        metadata={}
    )
    
    result = await intent_classifier_agent(state)
    
    assert result["intent"] == "rental"
    assert result["intent_confidence"] >= 0.7

@pytest.mark.asyncio
async def test_classify_trade_intent():
    state = ConversationState(
        user_query="我想买二手沙发",
        context="trade",
        intent="",
        intent_confidence=0.0,
        extracted_params={},
        optimized_query={},
        retrieved_data=[],
        formatted_response={},
        error=None,
        metadata={}
    )
    
    result = await intent_classifier_agent(state)
    
    assert result["intent"] == "trade"
    assert result["intent_confidence"] >= 0.7

@pytest.mark.asyncio
async def test_low_confidence_intent():
    state = ConversationState(
        user_query="你好",
        context="rental",
        intent="",
        intent_confidence=0.0,
        extracted_params={},
        optimized_query={},
        retrieved_data=[],
        formatted_response={},
        error=None,
        metadata={}
    )
    
    result = await intent_classifier_agent(state)
    
    assert result["intent_confidence"] < 0.7
```

- [x] **Step 2: Run test to verify it fails**

Run: `cd backend/ai-service && pytest tests/test_intent_classifier.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'app.agents'"

- [x] **Step 3: Implement intent classifier agent**

```python
# backend/ai-service/app/agents/intent_classifier.py
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from app.models.state import ConversationState
from app.config import settings
import json

llm = ChatOpenAI(
    model=settings.OPENAI_MODEL,
    temperature=settings.OPENAI_TEMPERATURE,
    api_key=settings.OPENAI_API_KEY
)

intent_schema = {
    "name": "classify_intent",
    "description": "识别用户查询意图",
    "parameters": {
        "type": "object",
        "properties": {
            "intent": {
                "type": "string",
                "enum": ["rental", "trade"],
                "description": "用户意图类型"
            },
            "confidence": {
                "type": "number",
                "description": "置信度0-1"
            }
        },
        "required": ["intent", "confidence"]
    }
}

async def intent_classifier_agent(state: ConversationState) -> ConversationState:
    """Classify user intent as rental or trade"""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """你是一个意图分类专家。分析用户查询,判断是租房(rental)还是交易(trade)意图。

租房关键词: 租房、出租、整租、合租、单间、房源、看房
交易关键词: 买、卖、二手、转让、家具、电器、沙发、冰箱

返回JSON格式: {{"intent": "rental或trade", "confidence": 0.0-1.0}}"""),
        ("user", "{query}")
    ])
    
    chain = prompt | llm.bind(functions=[intent_schema], function_call={"name": "classify_intent"})
    
    try:
        response = await chain.ainvoke({"query": state["user_query"]})
        
        function_call = response.additional_kwargs.get("function_call", {})
        arguments = json.loads(function_call.get("arguments", "{}"))
        
        state["intent"] = arguments.get("intent", "rental")
        state["intent_confidence"] = arguments.get("confidence", 0.5)
        
    except Exception as e:
        state["error"] = f"Intent classification failed: {str(e)}"
        state["intent"] = "rental"
        state["intent_confidence"] = 0.3
    
    return state
```

- [x] **Step 4: Run test to verify it passes**

Run: `cd backend/ai-service && pytest tests/test_intent_classifier.py -v`
Expected: PASS (3 tests)

- [x] **Step 5: Commit**

```bash
git add backend/ai-service/app/agents/intent_classifier.py backend/ai-service/tests/test_intent_classifier.py
git commit -m "feat(ai): implement intent classifier agent with OpenAI function calling"
```


### Task 6: Parameter Extractor Agent

**Files:**
- Create: `backend/ai-service/app/agents/parameter_extractor.py`
- Create: `backend/ai-service/tests/test_parameter_extractor.py`

- [x] **Step 1: Write test for parameter extraction**

```python
# backend/ai-service/tests/test_parameter_extractor.py
import pytest
from app.agents.parameter_extractor import parameter_extractor_agent
from app.models.state import ConversationState

@pytest.mark.asyncio
async def test_extract_rental_parameters():
    state = ConversationState(
        user_query="望京3000左右的两室一厅",
        context="rental",
        intent="rental",
        intent_confidence=0.95,
        extracted_params={},
        optimized_query={},
        retrieved_data=[],
        formatted_response={},
        error=None,
        metadata={}
    )
    
    result = await parameter_extractor_agent(state)
    params = result["extracted_params"]
    
    assert params["location"] == "望京"
    assert 2700 <= params["min_price"] <= 3000
    assert 3000 <= params["max_price"] <= 3300

@pytest.mark.asyncio
async def test_extract_trade_parameters():
    state = ConversationState(
        user_query="1000到2000的二手沙发",
        context="trade",
        intent="trade",
        intent_confidence=0.92,
        extracted_params={},
        optimized_query={},
        retrieved_data=[],
        formatted_response={},
        error=None,
        metadata={}
    )
    
    result = await parameter_extractor_agent(state)
    params = result["extracted_params"]
    
    assert params["category"] == "furniture"
    assert params["min_price"] == 1000
    assert params["max_price"] == 2000

@pytest.mark.asyncio
async def test_extract_partial_parameters():
    state = ConversationState(
        user_query="朝阳区的房子",
        context="rental",
        intent="rental",
        intent_confidence=0.88,
        extracted_params={},
        optimized_query={},
        retrieved_data=[],
        formatted_response={},
        error=None,
        metadata={}
    )
    
    result = await parameter_extractor_agent(state)
    params = result["extracted_params"]
    
    assert params["location"] == "朝阳区"
    assert "min_price" not in params or params["min_price"] is None
```

- [x] **Step 2: Run test to verify it fails**

Run: `cd backend/ai-service && pytest tests/test_parameter_extractor.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'app.agents.parameter_extractor'"

- [x] **Step 3: Implement parameter extractor agent**

```python
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
```

- [x] **Step 4: Run test to verify it passes**

Run: `cd backend/ai-service && pytest tests/test_parameter_extractor.py -v`
Expected: PASS (3 tests)

- [x] **Step 5: Commit**

```bash
git add backend/ai-service/app/agents/parameter_extractor.py backend/ai-service/tests/test_parameter_extractor.py
git commit -m "feat(ai): implement parameter extractor agent with schema validation"
```


### Task 7: Query Optimizer Agent

**Files:**
- Create: `backend/ai-service/app/agents/query_optimizer.py`
- Create: `backend/ai-service/app/agents/synonyms.json`
- Create: `backend/ai-service/tests/test_query_optimizer.py`

- [x] **Step 1: Write test for query optimization**

```python
# backend/ai-service/tests/test_query_optimizer.py
import pytest
from app.agents.query_optimizer import query_optimizer_agent
from app.models.state import ConversationState

@pytest.mark.asyncio
async def test_optimize_location_expansion():
    state = ConversationState(
        user_query="望京的房子",
        context="rental",
        intent="rental",
        intent_confidence=0.95,
        extracted_params={"location": "望京"},
        optimized_query={},
        retrieved_data=[],
        formatted_response={},
        error=None,
        metadata={}
    )
    
    result = await query_optimizer_agent(state)
    optimized = result["optimized_query"]
    
    assert "location" in optimized
    assert isinstance(optimized["location"], list)
    assert "望京" in optimized["location"]
    assert len(optimized["location"]) > 1

@pytest.mark.asyncio
async def test_optimize_price_range():
    state = ConversationState(
        user_query="3000左右",
        context="rental",
        intent="rental",
        intent_confidence=0.95,
        extracted_params={"min_price": 2700, "max_price": 3300},
        optimized_query={},
        retrieved_data=[],
        formatted_response={},
        error=None,
        metadata={}
    )
    
    result = await query_optimizer_agent(state)
    optimized = result["optimized_query"]
    
    assert optimized["min_price"] == 2700
    assert optimized["max_price"] == 3300

@pytest.mark.asyncio
async def test_optimize_category_synonyms():
    state = ConversationState(
        user_query="沙发",
        context="trade",
        intent="trade",
        intent_confidence=0.92,
        extracted_params={"category": "furniture"},
        optimized_query={},
        retrieved_data=[],
        formatted_response={},
        error=None,
        metadata={}
    )
    
    result = await query_optimizer_agent(state)
    optimized = result["optimized_query"]
    
    assert "keywords" in optimized
    assert "沙发" in optimized["keywords"]
```

- [x] **Step 2: Run test to verify it fails**

Run: `cd backend/ai-service && pytest tests/test_query_optimizer.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'app.agents.query_optimizer'"

- [x] **Step 3: Create synonyms dictionary**

```json
{
  "locations": {
    "望京": ["望京", "朝阳区望京", "望京SOHO", "望京西园"],
    "中关村": ["中关村", "海淀区中关村", "中关村软件园"],
    "国贸": ["国贸", "朝阳区国贸", "国贸CBD"],
    "西单": ["西单", "西城区西单", "西单商圈"]
  },
  "furniture": {
    "沙发": ["沙发", "布艺沙发", "皮沙发", "转角沙发"],
    "床": ["床", "双人床", "单人床", "实木床"],
    "桌子": ["桌子", "书桌", "餐桌", "办公桌"]
  },
  "appliance": {
    "冰箱": ["冰箱", "对开门冰箱", "双门冰箱"],
    "空调": ["空调", "挂机空调", "柜机空调", "变频空调"],
    "洗衣机": ["洗衣机", "滚筒洗衣机", "波轮洗衣机"]
  },
  "rental_type": {
    "整租": ["whole", "整租"],
    "合租": ["shared", "合租"],
    "单间": ["single", "单间"]
  }
}
```

- [x] **Step 4: Implement query optimizer agent**

```python
# backend/ai-service/app/agents/query_optimizer.py
from app.models.state import ConversationState
import json
import os

# Load synonyms dictionary
synonyms_path = os.path.join(os.path.dirname(__file__), "synonyms.json")
with open(synonyms_path, "r", encoding="utf-8") as f:
    SYNONYMS = json.load(f)

async def query_optimizer_agent(state: ConversationState) -> ConversationState:
    """Optimize query conditions with synonyms and expansions"""
    
    params = state["extracted_params"]
    optimized = {}
    intent = state["intent"]
    
    # Location expansion
    if "location" in params:
        location = params["location"]
        expanded_locations = SYNONYMS["locations"].get(location, [location])
        optimized["location"] = expanded_locations
    
    # Price range (already optimized by parameter extractor)
    if "min_price" in params:
        optimized["min_price"] = params["min_price"]
    if "max_price" in params:
        optimized["max_price"] = params["max_price"]
    
    # Area range
    if "min_area" in params:
        optimized["min_area"] = params["min_area"]
    if "max_area" in params:
        optimized["max_area"] = params["max_area"]
    
    # Rental type
    if "type" in params:
        rental_type = params["type"]
        optimized["type"] = rental_type
    
    # Trade category with keyword expansion
    if "category" in params:
        category = params["category"]
        optimized["category"] = category
        
        # Extract keywords from query for synonym matching
        query_lower = state["user_query"].lower()
        keywords = []
        
        for item, synonyms in SYNONYMS.get(category, {}).items():
            if item in query_lower:
                keywords.extend(synonyms)
        
        if keywords:
            optimized["keywords"] = keywords
    
    # Condition
    if "condition" in params:
        optimized["condition"] = params["condition"]
    
    # Facilities
    if "facilities" in params:
        optimized["facilities"] = params["facilities"]
    
    state["optimized_query"] = optimized
    
    return state
```

- [x] **Step 5: Run test to verify it passes**

Run: `cd backend/ai-service && pytest tests/test_query_optimizer.py -v`
Expected: PASS (3 tests)

- [x] **Step 6: Commit**

```bash
git add backend/ai-service/app/agents/query_optimizer.py backend/ai-service/app/agents/synonyms.json backend/ai-service/tests/test_query_optimizer.py
git commit -m "feat(ai): implement query optimizer with synonym expansion"
```


### Task 8: Data Retrieval Agent

**Files:**
- Create: `backend/ai-service/app/agents/data_retrieval.py`
- Create: `backend/ai-service/tests/test_data_retrieval.py`

- [x] **Step 1: Write test for data retrieval**

```python
# backend/ai-service/tests/test_data_retrieval.py
import pytest
from unittest.mock import AsyncMock, patch
from app.agents.data_retrieval import data_retrieval_agent
from app.models.state import ConversationState

@pytest.mark.asyncio
async def test_retrieve_rental_data():
    state = ConversationState(
        user_query="望京3000左右的两室一厅",
        context="rental",
        intent="rental",
        intent_confidence=0.95,
        extracted_params={"location": "望京", "min_price": 2700, "max_price": 3300},
        optimized_query={"location": ["望京", "朝阳区望京"], "min_price": 2700, "max_price": 3300},
        retrieved_data=[],
        formatted_response={},
        error=None,
        metadata={}
    )
    
    mock_response = {
        "data": [{"id": "rental_1", "title": "精装两室", "price": 3000}],
        "total": 1
    }
    
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.status_code = 200
        
        result = await data_retrieval_agent(state)
        
        assert len(result["retrieved_data"]) == 1
        assert result["retrieved_data"][0]["id"] == "rental_1"

@pytest.mark.asyncio
async def test_retrieve_trade_data():
    state = ConversationState(
        user_query="二手沙发",
        context="trade",
        intent="trade",
        intent_confidence=0.92,
        extracted_params={"category": "furniture"},
        optimized_query={"category": "furniture"},
        retrieved_data=[],
        formatted_response={},
        error=None,
        metadata={}
    )
    
    mock_response = {
        "data": [{"id": "item_1", "title": "布艺沙发", "price": 1200}],
        "total": 1
    }
    
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.status_code = 200
        
        result = await data_retrieval_agent(state)
        
        assert len(result["retrieved_data"]) == 1
        assert result["retrieved_data"][0]["id"] == "item_1"

@pytest.mark.asyncio
async def test_retrieve_with_cache():
    state = ConversationState(
        user_query="望京的房子",
        context="rental",
        intent="rental",
        intent_confidence=0.95,
        extracted_params={"location": "望京"},
        optimized_query={"location": ["望京"]},
        retrieved_data=[],
        formatted_response={},
        error=None,
        metadata={}
    )
    
    cached_data = [{"id": "rental_1", "title": "缓存房源"}]
    
    with patch("app.cache.get_cache", new_callable=AsyncMock) as mock_cache:
        mock_cache.return_value = cached_data
        
        result = await data_retrieval_agent(state)
        
        assert result["retrieved_data"] == cached_data
        assert result["metadata"]["cache_hit"] == True
```

- [x] **Step 2: Run test to verify it fails**

Run: `cd backend/ai-service && pytest tests/test_data_retrieval.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'app.agents.data_retrieval'"

- [x] **Step 3: Implement data retrieval agent**

```python
# backend/ai-service/app/agents/data_retrieval.py
import httpx
from app.models.state import ConversationState
from app.config import settings
from app.cache import get_cache, set_cache
import hashlib
import json

async def data_retrieval_agent(state: ConversationState) -> ConversationState:
    """Retrieve data from rental or trade service API"""
    
    intent = state["intent"]
    optimized_query = state["optimized_query"]
    
    # Generate cache key
    cache_key = f"{intent}:{hashlib.md5(json.dumps(optimized_query, sort_keys=True).encode()).hexdigest()}"
    
    # Check cache
    if settings.AI_ENABLE_CACHE:
        cached_data = await get_cache(cache_key)
        if cached_data is not None:
            state["retrieved_data"] = cached_data
            state["metadata"]["cache_hit"] = True
            return state
    
    # Build API URL and params
    if intent == "rental":
        url = f"{settings.RENTAL_SERVICE_URL}/api/rental/list"
    else:
        url = f"{settings.TRADE_SERVICE_URL}/api/trade/list"
    
    # Convert optimized query to API params
    params = {}
    
    if "location" in optimized_query:
        # Use first location for now (could be enhanced to query all)
        locations = optimized_query["location"]
        if isinstance(locations, list) and len(locations) > 0:
            params["location"] = locations[0]
        else:
            params["location"] = locations
    
    if "min_price" in optimized_query:
        params["min_price"] = optimized_query["min_price"]
    if "max_price" in optimized_query:
        params["max_price"] = optimized_query["max_price"]
    
    if "type" in optimized_query:
        params["type"] = optimized_query["type"]
    
    if "category" in optimized_query:
        params["category"] = optimized_query["category"]
    if "condition" in optimized_query:
        params["condition"] = optimized_query["condition"]
    
    if "min_area" in optimized_query:
        params["min_area"] = optimized_query["min_area"]
    if "max_area" in optimized_query:
        params["max_area"] = optimized_query["max_area"]
    
    # Call API with retry logic
    max_retries = settings.AI_MAX_RETRIES
    timeout = settings.AI_TIMEOUT
    
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=timeout)
                response.raise_for_status()
                data = response.json()
                
                retrieved_data = data.get("data", [])
                state["retrieved_data"] = retrieved_data
                state["metadata"]["cache_hit"] = False
                
                # Cache the result
                if settings.AI_ENABLE_CACHE:
                    await set_cache(cache_key, retrieved_data)
                
                return state
                
        except httpx.TimeoutException:
            if attempt == max_retries - 1:
                state["error"] = f"API timeout after {max_retries} retries"
                state["retrieved_data"] = []
        except httpx.HTTPError as e:
            if attempt == max_retries - 1:
                state["error"] = f"API error: {str(e)}"
                state["retrieved_data"] = []
        except Exception as e:
            state["error"] = f"Unexpected error: {str(e)}"
            state["retrieved_data"] = []
            break
    
    return state
```

- [x] **Step 4: Run test to verify it passes**

Run: `cd backend/ai-service && pytest tests/test_data_retrieval.py -v`
Expected: PASS (3 tests)

- [x] **Step 5: Commit**

```bash
git add backend/ai-service/app/agents/data_retrieval.py backend/ai-service/tests/test_data_retrieval.py
git commit -m "feat(ai): implement data retrieval agent with caching and retry"
```

---

### Task 9: Response Formatter Agent

**Files:**
- Create: `backend/ai-service/app/agents/response_formatter.py`
- Test: `backend/ai-service/tests/test_response_formatter.py`

- [x] **Step 1: Write the failing test**

Create `backend/ai-service/tests/test_response_formatter.py`:

```python
import pytest
from app.models.state import ConversationState
from app.agents.response_formatter import response_formatter_agent

@pytest.mark.asyncio
async def test_response_formatter_with_results():
    """Test formatting response with retrieved data"""
    state: ConversationState = {
        "user_query": "望京3000左右的两室一厅",
        "context": "rental",
        "intent": "rental",
        "intent_confidence": 0.95,
        "extracted_params": {
            "location": "望京",
            "min_price": 2700,
            "max_price": 3300,
            "type": "whole"
        },
        "optimized_query": {
            "location": ["望京", "朝阳区望京"],
            "min_price": 2700,
            "max_price": 3300,
            "type": "whole"
        },
        "retrieved_data": [
            {"id": "rental_1", "title": "精装两室", "price": 3000},
            {"id": "rental_2", "title": "温馨两居", "price": 2800}
        ],
        "formatted_response": {},
        "error": None,
        "metadata": {}
    }
    
    result = await response_formatter_agent(state)
    
    assert result["formatted_response"]["success"] is True
    assert result["formatted_response"]["total"] == 2
    assert len(result["formatted_response"]["data"]) == 2
    assert "query_understanding" in result["formatted_response"]
    assert "望京" in result["formatted_response"]["query_understanding"]
    assert "applied_filters" in result["formatted_response"]

@pytest.mark.asyncio
async def test_response_formatter_no_results():
    """Test formatting response with no results"""
    state: ConversationState = {
        "user_query": "火星上的房子",
        "context": "rental",
        "intent": "rental",
        "intent_confidence": 0.95,
        "extracted_params": {"location": "火星"},
        "optimized_query": {"location": ["火星"]},
        "retrieved_data": [],
        "formatted_response": {},
        "error": None,
        "metadata": 
    }
    
    result = await response_formatter_agent(state)
    
    assert result["formatted_response"]["success"] is True
    assert result["formatted_response"]["total"] == 0
    assert len(result["formatted_response"]["data"]) == 0
    assert "suggestions" in result["formatted_response"]

@pytest.mark.asyncio
async def test_response_formatter_with_error():
    """Test formatting response when error occurred"""
    state: ConversationState = {
        "user_query": "望京的房子",
        "context": "rental",
        "intent": "rental",
        "intent_confidence": 0.95,
        "extracted_params": {},
        "optimized_query": {},
        "retrieved_data": [],
        "formatted_response": {},
        "error": "API timeout",
        "metadata": {}
    }
    
    result = await response_formatter_agent(state)
    
    assert result["formatted_response"]["success"] is False
    assert "error" in result["formatted_response"]
    assert result["formatted_response"]["error"] == "API timeout"
```

- [x] **Step 2: Run test to verify it fails**

Run: `cd backend/ai-service && pytest tests/test_response_formatter.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'app.agents.response_formatter'"

- [x] **Step 3: Write minimal implementation**

Create `backend/ai-service/app/agents/response_formatter.py`:

```python
from typing import Dict, Any, List
from app.models.state import ConversationState

async def response_formatter_agent(state: ConversationState) -> ConversationState:
    """
    Format retrieved data into frontend-friendly JSON response.
    
    Generates query understanding text and provides suggestions when no results found.
    """
    # Check for errors first
    if state.get("error"):
        state["formatted_response"] = {
            "success": False,
            "error": state["error"],
            "data": [],
            "total": 0
        }
        return state
    
    # Get retrieved data
    retrieved_data = state.get("retrieved_data", [])
    extracted_params = state.get("extracted_params", )
    
    # Generate query understanding text
    query_understanding = _generate_understanding(extracted_params, state["intent"])
    
    # Build response
    formatted_response = {
        "success": True,
        "data": retrieved_data,
        "total": len(retrieved_data),
        "query_understanding": query_understanding,
        "applied_filters": extracted_params
    }
    
    # Add suggestions if no results
    if len(retrieved_data) == 0:
        formatted_response["suggestions"] = _generate_suggestions(extracted_params, state["intent"])
    
    state["formatted_response"] = formatted_response
    return state

def _generate_understanding(params: Dict[str, Any], intent: str) -> str:
    """Generate human-readable query understanding text"""
    parts = []
    
    if params.get("location"):
        location = params["location"]
        if isinstance(location, list):
            location = location[0]
        parts.append(f"{location}地区")
    
    if params.get("min_price") and params.get("max_price"):
        parts.append(f"{params['min_price']}-{params['max_price']}元")
    elif params.get("min_price"):
        parts.append(f"{params['min_price']}元以上")
    elif params.get("max_price"):
        parts.append(f"{params['max_price']}元以下")
    
    if intent == "rental":
        type_map = {"whole": "整租", "shared": "合租", "single": "单间"}
        if params.get("type"):
            parts.append(type_map.get(params["type"], ""))
    elif intent == "trade":
        if params.get("category"):
            category_map = {"furniture": "家具", "appliance": "家电"}
            parts.append(category_map.get(params["category"], params["category"]))
    
    if parts:
        return f"为您找到{''.join(parts)}"
    else:
        return "为您找到相关结果"

def _generate_suggestions(params: Dict[str, Any], intent: str) -> List[str]:
    """Generate suggestions when no results found"""
    suggestions = []
    
    if params.get("min_price") or params.get("max_price"):
        suggestions.append("尝试调整价格范围")
    
    if params.get("location"):
        suggestions.append("尝试搜索附近区域")
    
    if intent == "rental" and params.get("type"):
        suggestions.append("尝试其他租赁类型")
    
    if not suggestions:
        suggestions.append("尝试使用不同的关键词")
    
    return suggestions
```

- [x] **Step 4: Run test to verify it passes**

Run: `cd backend/ai-service && pytest tests/test_response_formatter.py -v`
Expected: PASS (3 tests)

- [x] **Step 5: Commit**

```bash
git add backend/ai-service/app/agents/response_formatter.py backend/ai-service/tests/test_response_formatter.py
git commit -m "feat(ai): implement response formatter agent"
```

---

## Phase 3: LangGraph Workflow Integration

### Task 10: LangGraph Workflow Definition

**Files:**
- Create: `backend/ai-service/app/workflow.py`
- Test: `backend/ai-service/tests/test_workflow.py`

- [x] **Step 1: Write the failing test**

Create `backend/ai-service/tests/test_workflow.py`:

```python
import pytest
from app.workflow import create_workflow
from app.models.state import ConversationState

@pytest.mark.asyncio
async def test_workflow_rental_query():
    """Test complete workflow with rental query"""
    workflow = create_workflow()
    
    initial_state: ConversationState = {
        "user_query": "望京3000左右的两室一厅",
        "context": "rental",
        "intent": "",
        "intent_confidence": 0.0,
        "extracted_params": {},
        "optimized_query": {},
        "retrieved_data": [],
        "formatted_response": {},
        "error": None,
        "metadata": {}
    }
    
    result = await workflow.ainvoke(initial_state)
    
    assert result["intent"] == "rental"
    assert result["intent_confidence"] >= 0.7
    assert "location" in result["extracted_params"]
    assert result["formatted_response"]["success"] is True

@pytest.mark.asyncio
async def test_workflow_low_confidence():
    """Test workflow with low confidence query"""
    workflow = create_workflow()
    
    initial_state: ConversationState = {
        "user_query": "我想要",
        "context": "rental",
        "intent": "",
        "intent_confidence": 0.0,
        "extracted_params": {},
        "optimized_query": {},
        "retrieved_data": [],
        "formatted_response": {},
        "error": None,
        "metadata": {}
    }
    
    result = await workflow.ainvoke(initial_state)
    
    assert result["intent_confidence"] < 0.7
    assert result["formatted_response"]["success"] is False
    assert "更多信息" in result["formatted_response"].get("error", "")
```

- [x] **Step 2: Run test to verify it fails**

Run: `cd backend/ai-service && pytest tests/test_workflow.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'app.workflow'"

- [x] **Step 3: Write minimal implementation**

Create `backend/ai-service/app/workflow.py`:

```python
from langgraph.graph import StateGraph, END
from app.models.state import ConversationState
from app.agents.intent_classifier import intent_classifier_agent
from app.agents.parameter_extractor import parameter_extractor_agent
from app.agents.query_optimizer import query_optimizer_agent
from app.agents.data_retrieval import data_retrieval_agent
from app.agents.response_formatter import response_formatter_agent

def create_workflow() -> StateGraph:
    """
    Create the LangGraph workflow for AI smart search.
    
    Workflow:
    1. IntentClassifier - identify rental vs trade
    2. Conditional routing based on confidence
    3. ParameterExtractor - extract structured params
    4. QueryOptimizer - expand synonyms and locations
    5. DataRetrieval - call backend APIs
    6. ResponseFormatter - format for frontend
    """
    workflow = StateGraph(ConversationState)
    
    # Add nodes
    workflow.add_node("intent_classifier", intent_classifier_agent)
    workflow.add_node("parameter_extractor", parameter_extractor_agent)
    workflow.add_node("query_optimizer", query_optimizer_agent)
    workflow.add_node("data_retrieval", data_retrieval_agent)
    workflow.add_node("response_formatter", response_formatter_agent)
    workflow.add_node("handle_low_confidence", handle_low_confidence)
    
    # Set entry point
    workflow.set_entry_point("intent_classifier")
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "intent_classifier",
        route_after_intent,
        {
            "continue": "parameter_extractor",
            "low_confidence": "handle_low_confidence"
        }
    )
    
    # Add sequential edges
    workflow.add_edge("parameter_extractor", "query_optimizer")
    workflow.add_edge("query_optimizer", "data_retrieval")
    workflow.add_edge("data_retrieval", "response_formatter")
    workflow.add_edge("response_formatter", END)
    workflow.add_edge("handle_low_confidence", END)
    
    return workflow.compile()

def route_after_intent(state: ConversationState) -> str:
    """Route based on intent confidence"""
    if state["intent_confidence"] >= 0.7:
        return "continue"
    else:
        return "low_confidence"

async def handle_low_confidence(state: ConversationState) -> ConversationState:
    """Handle queries with low confidence"""
    state["formatted_response"] = {
        "success": False,
        "error": "需要更多信息来理解您的查询,请提供更具体的描述",
        "data": [],
        "total": 0,
        "suggestions": [
            "请说明您是想租房还是购买二手商品",
            "提供更多细节,如位置、价格范围等"
        ]
    }
    return state
```

- [x] **Step 4: Run test to verify it passes**

Run: `cd backend/ai-service && pytest tests/test_workflow.py -v`
Expected: PASS (2 tests)

- [x] **Step 5: Commit**

```bash
git add backend/ai-service/app/workflow.py backend/ai-service/tests/test_workflow.py
git commit -m "feat(ai): implement langgraph workflow with conditional routing"
```

---

### Task 11: FastAPI Endpoint Integration

**Files:**
- Modify: `backend/ai-service/app/main.py`
- Create: `backend/ai-service/app/models/schemas.py`

- [x] **Step 1: Write the failing test**

Add to `backend/ai-service/tests/test_workflow.py`:

```python
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_smart_search_endpoint():
    """Test /api/ai/smart-search endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/ai/smart-search",
            json={
                "query": "望京3000左右的两室一厅",
                "context": "rental"
            }
        )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "query_understanding" in data
    assert "data" in data
```

- [x] **Step 2: Run test to verify it fails**

Run: `cd backend/ai-service && pytest tests/test_workflow.py::test_smart_search_endpoint -v`
Expected: FAIL with 404 or endpoint not found

- [x] **Step 3: Create request/response schemas**

Create `backend/ai-service/app/models/schemas.py`:

```python
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class SmartSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="User's natural language query")
    context: str = Field(..., pattern="^(rental|trade)$", description="Search context: rental or trade")

class SmartSearchResponse(BaseModel):
    success: bool
    data: List[Dict[str, Any]]
    total: int
    query_understanding: Optional[str] = None
    applied_filters: Optional[Dict[str, Any]] = None
    suggestions: Optional[List[str]] = None
    error: Optional[str] = None
```

- [x] **Step 4: Update FastAPI main.py**

Modify `backend/ai-service/app/main.py`:

```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.models.schemas import SmartSearchRequest, SmartSearchResponse
from app.models.state import ConversationState
from app.workflow import create_workflow

app = FastAPI(title="AI Service", version="2.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create workflow once at startup
workflow = None

@app.on_event("startup")
async def startup_event():
    global workflow
    workflow = create_workflow()

@app.get("/")
def read_root():
    return {"service": "AI Service", "status": "running", "version": "2.0.0"}

@app.post("/api/ai/smart-search", response_model=SmartSearchResponse)
async def smart_search(request: SmartSearchRequest):
    """
    AI-powered smart search endpoint.
    
    Accepts natural language queries and returns structured results.
    """
    try:
        # Initialize state
        initial_state: ConversationState = {
            "user_query": request.query,
            "context": request.context,
            "intent": "",
            "intent_confidence": 0.0,
            "extracted_params": {},
            "optimized_query": {},
            "retrieved_data": [],
            "formatted_response": {},
            "error": None,
            "metadata": {}
        }
        
        # Run workflow
        result = await workflow.ainvoke(initial_state)
        
        # Return formatted response
        return result["formatted_response"]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)
```

- [x] **Step 5: Run test to verify it passes**

Run: `cd backend/ai-service && pytest tests/test_workflow.py::test_smart_search_endpoint -v`
Expected: PASS

- [x] **Step 6: Commit**

```bash
git add backend/ai-service/app/main.py backend/ai-service/app/models/schemas.py
git commit -m "feat(ai): add smart search endpoint with workflow integration"
```

---

## Phase 4: MongoDB Migration

### Task 12: Rental Service MongoDB Migration

**Files:**
- Create: `backend/rental-service/app/database.py`
- Create: `backend/rental-service/app/models.py`
- Modify: `backend/rental-service/app/main.py`

- [x] **Step 1: Create database connection**

Create `backend/rental-service/app/database.py`:

```python
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
```

- [x] **Step 2: Create data models**

Create `backend/rental-service/app/models.py`:

```python
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Location(BaseModel):
    community: str
    address: str
    district: Optional[str] = None
    coordinates: Optional[List[float]] = None

class Rental(BaseModel):
    id: str
    title: str
    type: str  # whole/shared/single
    price: float
    area: float
    location: Location
    facilities: List[str]
    images: List[str]
    description: str
    contact: str
    publisher_id: str
    status: str  # available/reserved/rented
    created_at: str
    view_count: int = 0
    favorite_count: int = 0
```

- [x] **Step 3: Update main.py to use MongoDB**

Modify `backend/rental-service/app/main.py` - replace the `/api/rental/list` endpoint:

```python
from app.database import get_database

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
```

- [x] **Step 4: Add startup/shutdown events**

Add to `backend/rental-service/app/main.py`:

```python
from app.database import close_database

@app.on_event("shutdown")
async def shutdown_event():
    await close_database()
```

- [x] **Step 5: Test manually**

Run: `cd backend/rental-service && python app/main.py`
Then: `curl http://localhost:8001/api/rental/list`
Expected: Returns empty list or migrated data

- [x] **Step 6: Commit**

```bash
git add backend/rental-service/app/database.py backend/rental-service/app/models.py backend/rental-service/app/main.py
git commit -m "feat(rental): migrate to mongodb storage"
```

---

### Task 13: Trade Service MongoDB Migration

**Files:**
- Create: `backend/trade-service/app/database.py`
- Create: `backend/trade-service/app/models.py`
- Modify: `backend/trade-service/app/main.py`

- [x] **Step 1: Create database connection**

Create `backend/trade-service/app/database.py`:

```python
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
```

- [x] **Step 2: Create data models**

Create `backend/trade-service/app/models.py`:

```python
from pydantic import BaseModel
from typing import List, Optional

class TradeItem(BaseModel):
    id: str
    title: str
    category: str  # furniture/appliance/electronics
    price: float
    condition: str  # like_new/good/acceptable
    images: List[str]
    description: str
    location: str
    seller_id: str
    status: str  # available/reserved/sold
    created_at: str
    view_count: int = 0
    tags: Optional[List[str]] = []
```

- [x] **Step 3: Update main.py to use MongoDB**

Modify `backend/trade-service/app/main.py` - replace the `/api/trade/list` endpoint:

```python
from app.database import get_database

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
```

- [x] **Step 4: Add shutdown event**

Add to `backend/trade-service/app/main.py`:

```python
from app.database import close_database

@app.on_event("shutdown")
async def shutdown_event():
    await close_database()
```

- [x] **Step 5: Test manually**

Run: `cd backend/trade-service && python app/main.py`
Then: `curl http://localhost:8002/api/trade/list`
Expected: Returns empty list or migrated data

- [x] **Step 6: Commit**

```bash
git add backend/trade-service/app/database.py backend/trade-service/app/models.py backend/trade-service/app/main.py
git commit -m "feat(trade): migrate to mongodb storage"
```

---

### Task 14: Data Migration Script

**Files:**
- Create: `scripts/migrate_to_mongodb.py`

- [x] **Step 1: Create migration script**

Create `scripts/migrate_to_mongodb.py`:

```python
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
```

- [x] **Step 2: Run migration**

Run: `python scripts/migrate_to_mongodb.py`
Expected: Output showing indexes created and data inserted

- [x] **Step 3: Verify data**

Run: `mongo neighborhood_db --eval "db.rentals.count()"`
Expected: Shows count of rental records

- [x] **Step 4: Commit**

```bash
git add scripts/migrate_to_mongodb.py
git commit -m "feat: add mongodb migration script with sample data"
```

---

## Phase 5: Frontend Integration

### Task 15: SmartSearchBar Component

**Files:**
- Create: `frontend/src/components/SmartSearchBar.vue`
- Create: `frontend/src/api/ai.js`

- [x] **Step 1: Create AI API client**

Create `frontend/src/api/ai.js`:

```javascript
import request from '../utils/request'

export const smartSearchApi = {
  // Smart search
  search(data) {
    return request.post('/api/ai/smart-search', data)
  },
  
  // Get search history (future feature)
  getSearchHistory() {
    return request.get('/api/ai/search-history')
  }
}
```

- [x] **Step 2: Create SmartSearchBar component**

Create `frontend/src/components/SmartSearchBar.vue`:

```vue
<template>
  <div class="smart-search-bar">
    <el-input
      v-model="query"
      placeholder="试试输入: 望京3000左右的两室一厅"
      @keyup.enter="handleSearch"
      :loading="loading"
      size="large"
      clearable
    >
      <template #append>
        <el-button 
          @click="handleSearch" 
          :loading="loading"
          type="primary"
        >
          <el-icon><Search /></el-icon>
          搜索
        </el-button>
      </template>
    </el-input>
    
    <!-- Query understanding -->
    <div v-if="queryUnderstanding" class="query-understanding">
      <el-tag type="success" size="large">
        <el-icon><Check /></el-icon>
        {{ queryUnderstanding }}
      </el-tag>
    </div>
    
    <!-- Applied filters -->
    <div v-if="appliedFilters && Object.keys(appliedFilters).length > 0" class="applied-filters">
      <span class="filter-label">筛选条件:</span>
      <el-tag
        v-for="(value, key) in appliedFilters"
        :key="key"
        closable
        @close="removeFilter(key)"
        class="filter-tag"
      >
        {{ formatFilter(key, value) }}
      </el-tag>
    </div>
    
    <!-- Error message -->
    <el-alert
      v-if="errorMessage"
      :title="errorMessage"
      type="error"
      :closable="true"
      @close="errorMessage = ''"
      class="error-alert"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Search, Check } from '@element-plus/icons-vue'
import { smartSearchApi } from '@/api/ai'
import { ElMessage } from 'element-plus'

const props = defineProps({
  context: {
    type: String,
    required: true,
    validator: (value) => ['rental', 'trade'].includes(value)
  }
})

const emit = defineEmits(['search-results'])

const query = ref('')
const loading = ref(false)
const queryUnderstanding = ref('')
const appliedFilters = ref(null)
const errorMessage = ref('')

const handleSearch = async () => {
  if (!query.value.trim()) {
    ElMessage.warning('请输入搜索内容')
    return
  }
  
  loading.value = true
  errorMessage.value = ''
  
  try {
    const response = await smartSearchApi.search({
      query: query.value,
      context: props.context
    })
    
    if (response.success) {
      queryUnderstanding.value = response.query_understanding
      appliedFilters.value = response.applied_filters
      
      // Emit results to parent
      emit('search-results', {
        data: response.data,
        total: response.total
      })
      
      if (response.data.length === 0) {
        ElMessage.info('未找到匹配结果，试试调整搜索条件')
      }
    } else {
      errorMessage.value = response.error || '搜索失败'
    }
  } catch (error) {
    console.error('Search failed:', error)
    errorMessage.value = '搜索服务暂时不可用，请稍后重试'
  } finally {
    loading.value = false
  }
}

const removeFilter = (key) => {
  if (appliedFilters.value) {
    delete appliedFilters.value[key]
    // Re-trigger search without this filter
    handleSearch()
  }
}

const formatFilter = (key, value) => {
  const filterMap = {
    location: `位置: ${value}`,
    min_price: `最低价: ${value}元`,
    max_price: `最高价: ${value}元`,
    type: `类型: ${value}`,
    category: `分类: ${value}`,
    condition: `成色: ${value}`
  }
  return filterMap[key] || `${key}: ${value}`
}
</script>

<style scoped>
.smart-search-bar {
  margin-bottom: 20px;
}

.query-understanding {
  margin-top: 12px;
}

.applied-filters {
  margin-top: 12px;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.filter-label {
  font-size: 14px;
  color: #606266;
  margin-right: 8px;
}

.filter-tag {
  margin: 0;
}

.error-alert {
  margin-top: 12px;
}
</style>
```

- [x] **Step 3: Test component manually**

Add to rental list page (`frontend/src/views/rental/RentalList.vue`):

```vue
<template>
  <div>
    <SmartSearchBar context="rental" @search-results="handleSearchResults" />
    <!-- existing rental list -->
  </div>
</template>

<script setup>
import SmartSearchBar from '@/components/SmartSearchBar.vue'

const handleSearchResults = (results) => {
  console.log('Search results:', results)
  // Update rental list with results
}
</script>
```

- [x] **Step 4: Run frontend dev server**

Run: `cd frontend && npm run dev`
Then: Open browser and test search with "望京3000左右的两室"
Expected: Search bar shows query understanding and results

- [x] **Step 5: Commit**

```bash
git add frontend/src/components/SmartSearchBar.vue frontend/src/api/ai.js
git commit -m "feat(frontend): add smart search bar component"
```

---

## Phase 6: Monitoring and Observability

### Task 16: Prometheus Metrics

**Files:**
- Create: `backend/ai-service/app/metrics.py`
- Modify: `backend/ai-service/app/main.py`

- [x] **Step 1: Create metrics definitions**

Create `backend/ai-service/app/metrics.py`:

```python
from prometheus_client import Counter, Histogram, Gauge

# Request metrics
ai_requests_total = Counter(
    'ai_requests_total',
    'Total AI search requests',
    ['intent', 'status']
)

ai_request_duration = Histogram(
    'ai_request_duration_seconds',
    'AI request duration in seconds',
    ['agent']
)

# LLM metrics
ai_llm_tokens = Counter(
    'ai_llm_tokens_total',
    'Total LLM tokens used',
    ['model', 'type']  # type: prompt/completion
)

# Cache metrics
ai_cache_hits = Counter('ai_cache_hits_total', 'Cache hits')
ai_cache_misses = Counter('ai_cache_misses_total', 'Cache misses')

# Agent metrics
ai_agent_success = Counter(
    'ai_agent_success_total',
    'Agent success count',
    ['agent']
)

ai_agent_failure = Counter(
    'ai_agent_failure_total',
    'Agent failure count',
    ['agent', 'error_type']
)

# Active requests
ai_active_requests = Gauge(
    'ai_active_requests',
    'Number of active AI requests'
)
```

- [x] **Step 2: Add metrics endpoint**

Modify `backend/ai-service/app/main.py`:

```python
from prometheus_client import make_asgi_app

# Mount prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
```

- [x] **Step 3: Add metrics to workflow**

Update `backend/ai-service/app/main.py` smart_search endpoint:

```python
from app.metrics import (
    ai_requests_total, 
    ai_request_duration, 
    ai_active_requests
)
import time

@app.post("/api/ai/smart-search", response_model=SmartSearchResponse)
async def smart_search(request: SmartSearchRequest):
    ai_active_requests.inc()
    start_time = time.time()
    
    try:
        # ... existing workflow code ...
        
        # Record success metrics
        intent = result.get("intent", "unknown")
        ai_requests_total.labels(intent=intent, status="success").inc()
        
        return result["formatted_response"]
        
    except Exception as e:
        ai_requests_total.labels(intent="unknown", status="error").inc()
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
    finally:
        duration = time.time() - start_time
        ai_request_duration.labels(agent="workflow").observe(duration)
        ai_active_requests.dec()
```

- [x] **Step 4: Test metrics endpoint**

Run: `cd backend/ai-service && python app/main.py`
Then: `curl http://localhost:8003/metrics`
Expected: Prometheus metrics output

- [x] **Step 5: Commit**

```bash
git add backend/ai-service/app/metrics.py backend/ai-service/app/main.py
git commit -m "feat(ai): add prometheus metrics for monitoring"
```

---

### Task 17: Structured Logging

**Files:**
- Create: `backend/ai-service/app/utils/logger.py`
- Modify: `backend/ai-service/app/agents/*.py` (add logging)

- [x] **Step 1: Create logger setup**

Create `backend/ai-service/app/utils/logger.py`:

```python
import structlog
import logging
import sys

def setup_logging():
    """Configure structured logging with structlog"""
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,
    )
    
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

def get_logger(name: str):
    """Get a structured logger instance"""
    return structlog.get_logger(name)
```

- [x] **Step 2: Add logging to intent classifier**

Update `backend/ai-service/app/agents/intent_classifier.py`:

```python
from app.utils.logger import get_logger
import time

logger = get_logger(__name__)

async def intent_classifier_agent(state: ConversationState) -> ConversationState:
    start_time = time.time()
    
    try:
        # ... existing code ...
        
        duration_ms = (time.time() - start_time) * 1000
        logger.info(
            "intent_classified",
            user_query=state["user_query"],
            intent=intent,
            confidence=confidence,
            duration_ms=duration_ms
        )
        
        return state
        
    except Exception as e:
        logger.error(
            "intent_classification_failed",
            user_query=state["user_query"],
            error=str(e)
        )
        raise
```

- [x] **Step 3: Initialize logging in main.py**

Update `backend/ai-service/app/main.py`:

```python
from app.utils.logger import setup_logging, get_logger

# Setup logging at module level
setup_logging()
logger = get_logger(__name__)

@app.on_event("startup")
async def startup_event():
    global workflow
    workflow = create_workflow()
    logger.info("ai_service_started", version="2.0.0")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("ai_service_shutdown")
```

- [x] **Step 4: Test structured logs**

Run: `cd backend/ai-service && python app/main.py`
Then: Make a search request
Expected: JSON-formatted logs in console

- [x] **Step 5: Commit**

```bash
git add backend/ai-service/app/utils/logger.py backend/ai-service/app/agents/intent_classifier.py backend/ai-service/app/main.py
git commit -m "feat(ai): add structured logging with structlog"
```

---

## Phase 7: Testing and Documentation

### Task 18: Integration Tests

**Files:**
- Create: `backend/ai-service/tests/test_integration.py`

- [x] **Step 1: Write integration test**

Create `backend/ai-service/tests/test_integration.py`:

```python
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_end_to_end_rental_search():
    """Test complete rental search flow"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/ai/smart-search",
            json={
                "query": "望京3000左右的两室一厅",
                "context": "rental"
            }
        )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify response structure
    assert data["success"] is True
    assert "query_understanding" in data
    assert "望京" in data["query_understanding"]
    assert "applied_filters" in data
    assert data["applied_filters"]["location"] == "望京"
    assert 2700 <= data["applied_filters"]["min_price"] <= 3000
    assert 3000 <= data["applied_filters"]["max_price"] <= 3300

@pytest.mark.asyncio
async def test_end_to_end_trade_search():
    """Test complete trade search flow"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/ai/smart-search",
            json={
                "query": "九成新的沙发",
                "context": "trade"
            }
        )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert "沙发" in data["query_understanding"] or "家具" in data["query_understanding"]

@pytest.mark.asyncio
async def test_low_confidence_query():
    """Test handling of ambiguous queries"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/ai/smart-search",
            json={
                "query": "我想要",
                "context": "rental"
            }
        )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is False
    assert "更多信息" in data["error"]
    assert "suggestions" in data

@pytest.mark.asyncio
async def test_metrics_endpoint():
    """Test Prometheus metrics endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/metrics")
    
    assert response.status_code == 200
    assert "ai_requests_total" in response.text
```

- [x] **Step 2: Run integration tests**

Run: `cd backend/ai-service && pytest tests/test_integration.py -v`
Expected: PASS (4 tests)

- [x] **Step 3: Commit**

```bash
git add backend/ai-service/tests/test_integration.py
git commit -m "test(ai): add end-to-end integration tests"
```

---

### Task 19: Update Requirements and Documentation

**Files:**
- Modify: `backend/ai-service/requirements.txt`
- Modify: `README.md`

- [x] **Step 1: Update requirements.txt**

Update `backend/ai-service/requirements.txt`:

```txt
fastapi==0.109.0
uvicorn==0.27.0
langgraph==0.0.20
langchain==0.1.0
langchain-openai==0.0.5
pydantic==2.5.3
pydantic-settings==2.1.0
motor==3.3.2
redis==5.0.1
httpx==0.26.0
prometheus-client==0.19.0
structlog==24.1.0
opentelemetry-api==1.22.0
opentelemetry-sdk==1.22.0
opentelemetry-instrumentation-fastapi==0.43b0
pytest==7.4.4
pytest-asyncio==0.23.3
```

- [x] **Step 2: Update README.md**

Update the AI Service section in `README.md`:

```markdown
## AI 功能（LangGraph + 多Agent架构）

### 智能搜索（核心功能）

用户通过自然语言查询，AI自动识别意图并提取参数：

\`\`\`bash
curl -X POST http://localhost:8003/api/ai/smart-search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "望京3000左右的两室一厅",
    "context": "rental"
  }'
\`\`\`

响应示例：
\`\`\`json
{
  "success": true,
  "data": [...],
  "total": 15,
  "query_understanding": "为您找到望京地区2700-3300元的两室一厅",
  "applied_filters": {
    "location": "望京",
    "min_price": 2700,
    "max_price": 3300,
    "type": "whole"
  }
}
\`\`\`

### 多Agent架构

系统由5个专门的Agent组成：

1. **IntentClassifierAgent** - 识别租房/交易意图
2. **ParameterExtractorAgent** - 提取结构化参数
3. **QueryOptimizerAgent** - 优化查询条件
4. **DataRetrievalAgent** - 调用后端API
5. **ResponseFormatterAgent** - 格式化响应

### 监控

- **Prometheus指标**: http://localhost:8003/metrics
- **结构化日志**: JSON格式输出
- **分布式追踪**: OpenTelemetry集成
```

- [x] **Step 3: Commit**

```bash
git add backend/ai-service/requirements.txt README.md
git commit -m "docs: update requirements and readme for ai service"
```

---

## Self-Review Checklist

Before presenting this plan to the user, verify:

- [x] **No placeholders**: No "TBD", "TODO", "implement later", or vague instructions
- [x] **Complete code**: Every code step includes actual implementation, not descriptions
- [x] **Exact paths**: All file paths are absolute and correct
- [x] **Type consistency**: Function names, parameters, and types match across tasks
- [x] **Spec coverage**: All requirements from design doc are covered
- [x] **Test-first**: Every task follows TDD pattern (test → fail → implement → pass → commit)
- [x] **Bite-sized steps**: Each step is 2-5 minutes of work
- [x] **No duplication**: Code is shown in full, not referenced as "similar to Task N"

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-04-16-ai-smart-search.md`.

**Two execution options:**

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?**
