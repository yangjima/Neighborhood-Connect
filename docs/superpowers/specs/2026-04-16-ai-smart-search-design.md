---
name: AI智能搜索系统设计
description: 基于LangGraph多Agent架构的自然语言查询系统,支持租房和交易服务的智能搜索
type: design
---

# AI智能搜索系统设计规格说明

## 1. 项目概述

### 1.1 目标
为邻里通平台构建智能搜索系统,用户通过自然语言输入查询需求(如"望京3000左右的两室一厅"),AI自动识别意图、提取参数、优化查询并返回结构化结果。

### 1.2 核心价值
- **用户体验提升**: 无需复杂的筛选表单,自然语言即可查询
- **技术展示**: 多Agent架构 + LangGraph编排 + MongoDB + 可观测性
- **可扩展性**: 易于添加新的意图类型和服务

### 1.3 技术栈
- **AI框架**: LangGraph + LangChain
- **LLM**: OpenAI GPT-4 Turbo (Function Calling)
- **数据库**: MongoDB (Motor异步驱动)
- **缓存**: Redis
- **监控**: Prometheus + structlog + OpenTelemetry
- **后端**: FastAPI + Python 3.10+

## 2. 系统架构

### 2.1 整体架构图

```
┌─────────────┐
│   前端      │
│ (Vue 3)     │
└──────┬──────┘
       │ POST /api/ai/smart-search
       ↓
┌─────────────────────────────────────┐
│        AI Service (FastAPI)         │
│  ┌───────────────────────────────┐  │
│  │   LangGraph Workflow          │  │
│  │                               │  │
│  │  ┌─────────────────────────┐  │  │
│  │  │ IntentClassifierAgent   │  │  │
│  │  └───────────┬─────────────┘  │  │
│  │              ↓                │  │
│  │  ┌─────────────────────────┐  │  │
│  │  │ ParameterExtractorAgent │  │  │
│  │  └───────────┬─────────────┘  │  │
│  │              ↓                │  │
│  │  ┌─────────────────────────┐  │  │
│  │  │ QueryOptimizerAgent     │  │  │
│  │  └───────────┬─────────────┘  │  │
│  │              ↓                │  │
│  │  ┌─────────────────────────┐  │  │
│  │  │ DataRetrievalAgent      │  │  │
│  │  └───────────┬─────────────┘  │  │
│  │              ↓                │  │
│  │  ┌─────────────────────────┐  │  │
│  │  │ ResponseFormatterAgent  │  │  │
│  │  └─────────────────────────┘  │  │
│  └───────────────────────────────┘  │
└──────────┬──────────────┬───────────┘
           │              │
           ↓              ↓
    ┌──────────┐   ┌──────────┐
    │ MongoDB  │   │  Redis   │
    └──────────┘   └──────────┘
           ↓
    ┌──────────────────────┐
    │ Rental/Trade Service │
    └──────────────────────┘
```

### 2.2 数据流

1. 用户输入: "望京3000左右的两室一厅"
2. IntentClassifier: 识别为 `rental` 意图
3. ParameterExtractor: 提取 `{location: "望京", price_range: [2700, 3300], type: "whole"}`
4. QueryOptimizer: 扩展位置 `["望京", "朝阳区望京", "望京SOHO"]`
5. DataRetrieval: 调用 rental-service API
6. ResponseFormatter: 格式化为前端JSON
7. 返回结果 + 查询理解说明

## 3. Agent详细设计

### 3.1 IntentClassifierAgent (意图分类Agent)

**职责**: 判断用户查询属于租房(rental)还是交易(trade)

**输入**:
```python
{
    "user_query": "望京3000左右的两室一厅"
}
```

**输出**:
```python
{
    "intent": "rental",  # rental | trade
    "confidence": 0.95   # 0.0-1.0
}
```

**实现细节**:
- 使用OpenAI Function Calling
- 定义intent_schema:
```python
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
```

**决策逻辑**:
- confidence >= 0.7: 继续下一步
- confidence < 0.7: 返回"需要更多信息"提示

### 3.2 ParameterExtractorAgent (参数提取Agent)

**职责**: 从自然语言中提取结构化参数

**Rental参数Schema**:
```python
class RentalParams(BaseModel):
    type: Optional[str] = None  # whole/shared/single
    location: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    min_area: Optional[float] = None
    max_area: Optional[float] = None
    facilities: Optional[List[str]] = None
```

**Trade参数Schema**:
```python
class TradeParams(BaseModel):
    category: Optional[str] = None  # furniture/appliance
    condition: Optional[str] = None  # like_new/good/acceptable
    location: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
```

**实现细节**:
- 使用OpenAI Function Calling + Pydantic验证
- 支持部分参数提取(用户可能只说"望京的房子")
- 价格智能推断: "3000左右" → `min_price: 2700, max_price: 3300`

### 3.3 QueryOptimizerAgent (查询优化Agent)

**职责**: 优化查询条件,处理同义词和模糊匹配

**优化策略**:

1. **地理位置扩展**:
   - 输入: "望京"
   - 输出: ["望京", "朝阳区望京", "望京SOHO", "望京西园"]

2. **同义词映射**:
   - "沙发" → ["沙发", "布艺沙发", "皮沙发", "转角沙发"]
   - "整租" → ["whole", "整租"]

3. **价格区间智能推断**:
   - "3000左右" → `min: 2700, max: 3300` (±10%)
   - "3000以下" → `min: 0, max: 3000`
   - "3000-5000" → `min: 3000, max: 5000`

4. **户型标准化**:
   - "两室一厅" → 查询条件中添加关键词匹配

**实现细节**:
- 维护同义词词典(JSON配置文件)
- 使用正则表达式解析价格表达
- 可选: 使用embedding向量相似度匹配

### 3.4 DataRetrievalAgent (数据检索Agent)

**职责**: 调用后端服务API获取数据

**实现细节**:
```python
async def retrieve_data(params: dict, intent: str) -> list:
    # 构建查询URL
    if intent == "rental":
        url = "http://rental-service:8001/api/rental/list"
    else:
        url = "http://trade-service:8002/api/trade/list"
    
    # 检查缓存
    cache_key = f"{intent}:{hash(str(params))}"
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # 调用API
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params, timeout=10.0)
        data = response.json()
    
    # 写入缓存(5分钟)
    await redis.setex(cache_key, 300, json.dumps(data))
    
    return data
```

**特性**:
- 使用httpx异步HTTP客户端
- Redis缓存(TTL 5分钟)
- 重试机制(最多3次,指数退避)
- 超时控制(10秒)

### 3.5 ResponseFormatterAgent (响应格式化Agent)

**职责**: 将检索结果格式化为前端需要的JSON

**输出格式**:
```python
{
    "success": true,
    "data": [...],  # 房源/商品列表
    "total": 15,
    "query_understanding": "为您找到望京地区2700-3300元的两室一厅",
    "applied_filters": {
        "location": "望京",
        "min_price": 2700,
        "max_price": 3300,
        "type": "whole"
    },
    "suggestions": []  # 无结果时的推荐建议
}
```

**query_understanding生成逻辑**:
```python
def generate_understanding(params: dict, intent: str) -> str:
    parts = []
    if params.get("location"):
        parts.append(f"{params['location']}地区")
    if params.get("min_price") and params.get("max_price"):
        parts.append(f"{params['min_price']}-{params['max_price']}元")
    if params.get("type"):
        type_map = {"whole": "整租", "shared": "合租", "single": "单间"}
        parts.append(type_map.get(params["type"], ""))
    
    return f"为您找到{''.join(parts)}"
```

## 4. LangGraph工作流编排

### 4.1 状态定义

```python
from typing import TypedDict, Optional, List

class ConversationState(TypedDict):
    # 输入
    user_query: str
    context: str  # rental | trade
    
    # 中间状态
    intent: str
    intent_confidence: float
    extracted_params: dict
    optimized_query: dict
    retrieved_data: List[dict]
    
    # 输出
    formatted_response: dict
    
    # 元数据
    error: Optional[str]
    metadata: dict  # {agent_timings, token_usage, cache_hit}
```

### 4.2 工作流定义

```python
from langgraph.graph import StateGraph, END

workflow = StateGraph(state_schema=ConversationState)

# 添加节点
workflow.add_node("intent_classifier", intent_classifier_agent)
workflow.add_node("parameter_extractor", parameter_extractor_agent)
workflow.add_node("query_optimizer", query_optimizer_agent)
workflow.add_node("data_retrieval", data_retrieval_agent)
workflow.add_node("response_formatter", response_formatter_agent)
workflow.add_node("handle_low_confidence", handle_low_confidence)

# 设置入口
workflow.set_entry_point("intent_classifier")

# 添加条件边
workflow.add_conditional_edges(
    "intent_classifier",
    lambda state: "continue" if state["intent_confidence"] >= 0.7 else "low_confidence",
    {
        "continue": "parameter_extractor",
        "low_confidence": "handle_low_confidence"
    }
)

# 添加普通边
workflow.add_edge("parameter_extractor", "query_optimizer")
workflow.add_edge("query_optimizer", "data_retrieval")
workflow.add_edge("data_retrieval", "response_formatter")
workflow.add_edge("response_formatter", END)
workflow.add_edge("handle_low_confidence", END)

# 编译
graph = workflow.compile()
```

### 4.3 错误处理

每个Agent节点包装错误处理:

```python
async def safe_agent_wrapper(agent_func):
    async def wrapper(state: ConversationState) -> ConversationState:
        try:
            return await agent_func(state)
        except OpenAIError as e:
            # LLM调用失败,降级到规则引擎
            logger.error(f"LLM error: {e}, falling back to rules")
            return await fallback_rules_engine(state)
        except Exception as e:
            # 其他错误,记录并返回错误状态
            logger.error(f"Agent error: {e}")
            state["error"] = str(e)
            return state
    return wrapper
```

## 5. 数据层设计

### 5.1 MongoDB Schema

**Database**: `neighborhood_db`

**Collection: rentals**
```javascript
{
    _id: ObjectId,
    title: String,
    type: String,  // whole/shared/single
    price: Number,
    area: Number,
    location: {
        community: String,
        address: String,
        district: String,  // 朝阳区、海淀区
        coordinates: [Number, Number]  // [经度, 纬度]
    },
    facilities: [String],
    images: [String],
    description: String,
    contact: String,
    publisher_id: String,
    status: String,  // available/reserved/rented
    created_at: Date,
    updated_at: Date,
    view_count: Number,
    favorite_count: Number
}
```

**Collection: trade_items**
```javascript
{
    _id: ObjectId,
    title: String,
    category: String,  // furniture/appliance/electronics
    price: Number,
    condition: String,  // like_new/good/acceptable
    images: [String],
    description: String,
    location: String,
    seller_id: String,
    status: String,  // available/reserved/sold
    created_at: Date,
    updated_at: Date,
    view_count: Number,
    tags: [String]
}
```

**Collection: search_logs (新增)**
```javascript
{
    _id: ObjectId,
    user_id: String,
    query: String,
    intent: String,
    extracted_params: Object,
    result_count: Number,
    clicked_items: [String],
    timestamp: Date,
    session_id: String
}
```

### 5.2 索引设计

```python
# rentals collection
db.rentals.create_index([("location.coordinates", "2dsphere")])  # 地理位置查询
db.rentals.create_index([("title", "text"), ("description", "text")])  # 全文搜索
db.rentals.create_index([("price", 1)])  # 价格排序
db.rentals.create_index([("created_at", -1)])  # 时间排序
db.rentals.create_index([("status", 1)])  # 状态筛选

# trade_items collection
db.trade_items.create_index([("category", 1)])
db.trade_items.create_index([("price", 1)])
db.trade_items.create_index([("title", "text"), ("description", "text")])
db.trade_items.create_index([("created_at", -1)])

# search_logs collection
db.search_logs.create_index([("user_id", 1), ("timestamp", -1)])
db.search_logs.create_index([("timestamp", -1)])
```

### 5.3 数据迁移

```python
# migration.py
async def migrate_memory_to_mongodb():
    """将内存数据迁移到MongoDB"""
    from backend.rental_service.app.main import rentals_db as memory_rentals
    from backend.trade_service.app.main import items_db as memory_items
    
    # 连接MongoDB
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.neighborhood_db
    
    # 迁移租房数据
    for rental in memory_rentals:
        rental["_id"] = rental.pop("id")
        await db.rentals.insert_one(rental)
    
    # 迁移交易数据
    for item in memory_items:
        item["_id"] = item.pop("id")
        await db.trade_items.insert_one(item)
    
    print("Migration completed!")
```

## 6. 前端集成

### 6.1 智能搜索框组件

**文件**: `frontend/src/components/SmartSearchBar.vue`

```vue
<template>
  <div class="smart-search-bar">
    <el-input
      v-model="query"
      placeholder="试试输入: 望京3000左右的两室一厅"
      @keyup.enter="handleSearch"
      :loading="loading"
    >
      <template #append>
        <el-button @click="handleSearch" :loading="loading">
          搜索
        </el-button>
      </template>
    </el-input>
    
    <!-- 查询理解提示 -->
    <div v-if="queryUnderstanding" class="query-understanding">
      <el-tag>{{ queryUnderstanding }}</el-tag>
    </div>
    
    <!-- 应用的筛选条件 -->
    <div v-if="appliedFilters" class="applied-filters">
      <el-tag
        v-for="(value, key) in appliedFilters"
        :key="key"
        closable
        @close="removeFilter(key)"
      >
        {{ formatFilter(key, value) }}
      </el-tag>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { smartSearchApi } from '@/api/ai'

const query = ref('')
const loading = ref(false)
const queryUnderstanding = ref('')
const appliedFilters = ref(null)

const handleSearch = async () => {
  if (!query.value.trim()) return
  
  loading.value = true
  try {
    const response = await smartSearchApi.search({
      query: query.value,
      context: 'rental'  // 或 'trade'
    })
    
    if (response.success) {
      queryUnderstanding.value = response.query_understanding
      appliedFilters.value = response.applied_filters
      
      // 触发结果更新事件
      emit('search-results', response.data)
    }
  } catch (error) {
    console.error('Search failed:', error)
  } finally {
    loading.value = false
  }
}
</script>
```

### 6.2 API封装

**文件**: `frontend/src/api/ai.js`

```javascript
import request from '../utils/request'

export const smartSearchApi = {
  // 智能搜索
  search(data) {
    return request.post('/api/ai/smart-search', data)
  },
  
  // 获取搜索历史
  getSearchHistory() {
    return request.get('/api/ai/search-history')
  }
}
```

## 7. 可观测性设计

### 7.1 Prometheus指标

```python
from prometheus_client import Counter, Histogram, Gauge

# 请求计数
ai_requests_total = Counter(
    'ai_requests_total',
    'Total AI requests',
    ['intent', 'status']
)

# 请求耗时
ai_request_duration = Histogram(
    'ai_request_duration_seconds',
    'AI request duration',
    ['agent']
)

# LLM token使用
ai_llm_tokens = Counter(
    'ai_llm_tokens_total',
    'Total LLM tokens used',
    ['model', 'type']  # type: prompt/completion
)

# 缓存命中率
ai_cache_hits = Counter('ai_cache_hits_total', 'Cache hits')
ai_cache_misses = Counter('ai_cache_misses_total', 'Cache misses')

# Agent成功率
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
```

### 7.2 结构化日志

```python
import structlog

logger = structlog.get_logger()

# 使用示例
logger.info(
    "intent_classified",
    trace_id=trace_id,
    user_query=query,
    intent=intent,
    confidence=confidence,
    duration_ms=duration
)
```

### 7.3 分布式追踪

```python
from opentelemetry import trace
from opentelemetry.exporter.jaeger import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# 配置Jaeger
jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)

provider = TracerProvider()
processor = BatchSpanProcessor(jaeger_exporter)
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

tracer = trace.get_tracer(__name__)

# 使用示例
with tracer.start_as_current_span("intent_classification"):
    result = await classify_intent(query)
```

## 8. 部署和运维

### 8.1 环境变量

```bash
# .env
OPENAI_API_KEY=sk-xxx
OPENAI_MODEL=gpt-4-turbo
OPENAI_TEMPERATURE=0.0

MONGODB_URL=mongodb://mongodb:27017
MONGODB_DB=neighborhood_db

REDIS_URL=redis://redis:6379
REDIS_CACHE_TTL=300

AI_TIMEOUT=10
AI_MAX_RETRIES=3
AI_ENABLE_CACHE=true

RENTAL_SERVICE_URL=http://rental-service:8001
TRADE_SERVICE_URL=http://trade-service:8002
```

### 8.2 Docker Compose更新

```yaml
services:
  ai-service:
    build: ./backend/ai-service
    ports:
      - "8003:8003"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - MONGODB_URL=mongodb://mongodb:27017
      - REDIS_URL=redis://redis:6379
    depends_on:
      - mongodb
      - redis
      - rental-service
      - trade-service
  
  mongodb:
    image: mongo:6.0
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
  
  redis:
    image: redis:7.0
    ports:
      - "6379:6379"

volumes:
  mongodb_data:
```

### 8.3 性能优化

1. **LLM调用优化**
   - 使用缓存减少重复调用
   - 批量处理相似查询
   - 设置合理的timeout

2. **数据库查询优化**
   - 使用索引加速查询
   - 限制返回字段(projection)
   - 分页查询避免大结果集

3. **降级策略**
   - LLM超时 → 回退到关键词匹配
   - MongoDB连接失败 → 回退到内存数据
   - Redis缓存失败 → 直接查询,不影响主流程

## 9. 测试策略

### 9.1 单元测试

```python
# test_intent_classifier.py
import pytest

@pytest.mark.asyncio
async def test_intent_classifier_rental():
    state = {"user_query": "我想租房"}
    result = await intent_classifier_agent(state)
    assert result["intent"] == "rental"
    assert result["intent_confidence"] > 0.7

@pytest.mark.asyncio
async def test_parameter_extractor():
    state = {
        "user_query": "望京3000左右的两室",
        "intent": "rental"
    }
    result = await parameter_extractor_agent(state)
    params = result["extracted_params"]
    assert params["location"] == "望京"
    assert 2700 <= params["min_price"] <= 3000
    assert 3000 <= params["max_price"] <= 3300
```

### 9.2 集成测试

```python
# test_workflow.py
@pytest.mark.asyncio
async def test_full_workflow():
    initial_state = {
        "user_query": "望京3000左右的两室一厅",
        "context": "rental"
    }
    
    result = await graph.ainvoke(initial_state)
    
    assert result["success"] == True
    assert len(result["data"]) > 0
    assert "query_understanding" in result
```

## 10. 实施计划

### Phase 1: 基础架构 (3天)
- [ ] 搭建LangGraph工作流框架
- [ ] 实现5个Agent的基础结构
- [ ] MongoDB集成和数据迁移
- [ ] Redis缓存集成

### Phase 2: Agent实现 (5天)
- [ ] IntentClassifierAgent + OpenAI Function Calling
- [ ] ParameterExtractorAgent + Pydantic验证
- [ ] QueryOptimizerAgent + 同义词词典
- [ ] DataRetrievalAgent + 重试机制
- [ ] ResponseFormatterAgent

### Phase 3: 前端集成 (2天)
- [ ] SmartSearchBar组件
- [ ] API封装
- [ ] 搜索历史功能

### Phase 4: 监控和优化 (2天)
- [ ] Prometheus指标
- [ ] 结构化日志
- [ ] 性能测试和优化

### Phase 5: 测试和文档 (2天)
- [ ] 单元测试
- [ ] 集成测试
- [ ] API文档
- [ ] 部署文档

## 11. 技术亮点总结

1. **多Agent架构** - 职责清晰,易于扩展和维护
2. **LangGraph编排** - 可视化工作流,支持条件路由
3. **OpenAI Function Calling** - 结构化参数提取,准确度高
4. **MongoDB地理位置查询** - 2dsphere索引支持位置搜索
5. **Redis缓存** - 减少LLM调用成本,提升响应速度
6. **Prometheus监控** - 完整的可观测性指标
7. **降级策略** - 高可用设计,LLM失败时回退到规则引擎
8. **分布式追踪** - OpenTelemetry + Jaeger全链路追踪
9. **异步处理** - Motor + httpx异步IO,高并发性能
10. **结构化日志** - structlog便于日志分析和问题排查

## 12. 风险和挑战

### 12.1 技术风险
- **LLM调用成本**: 每次查询调用多次LLM,成本较高
  - 缓解: 使用Redis缓存,相同查询直接返回
- **LLM响应时间**: 可能超过3秒
  - 缓解: 设置合理timeout,提供loading状态
- **参数提取准确度**: 复杂查询可能提取不准确
  - 缓解: 提供"查询理解"反馈,用户可调整

### 12.2 业务风险
- **用户习惯**: 用户可能不习惯自然语言查询
  - 缓解: 提供示例查询,引导用户使用
- **查询多样性**: 用户查询方式千变万化
  - 缓解: 持续收集search_logs,优化prompt

## 13. 后续扩展

1. **多轮对话**: 支持追问和澄清
2. **个性化推荐**: 基于用户历史行为推荐
3. **语音输入**: 集成语音识别
4. **多语言支持**: 支持英文查询
5. **图像搜索**: 上传图片搜索相似房源/商品
