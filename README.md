# 邻里通 Neighborhood-Connect

> 邻里通 - 连接社区，服务生活

一个混合模式的社区生活服务平台，连接物业、服务商和居民，提供租房、交易、家政、兼职等一站式社区服务。

## 技术栈

### 前端
- **Vue 3** + Vite - 现代前端框架
- **Vue Router** - 路由管理
- **Pinia** - 状态管理
- **Element Plus** - UI组件库
- **Axios** - HTTP客户端

### 后端
- **用户服务**: Java Spring Boot 3.2 + Spring Security + JWT (8081)
- **租房服务**: Python FastAPI + MongoDB (8001)
- **交易服务**: Python FastAPI + MongoDB (8002)
- **AI服务**: Python FastAPI + LangGraph + OpenAI (8003)
- **支付服务**: Java Spring Boot + MySQL (8082)
- **上传服务**: Python FastAPI (8004)

### 数据存储
- **MySQL 8.0** - 主数据库（用户、订单）
- **MongoDB 6.0** - 文档存储（房源、商品详情）
- **Redis 7.0** - 缓存、会话
- **Elasticsearch 8.x** - 搜索引擎（规划中）

### 基础设施
- **Docker** + Docker Compose
- **Nginx** - API网关、反向代理

---

## 功能模块

### ✅ 已完成

| 模块 | 描述 | 备注 |
|------|------|------|
| 用户认证 | 登录、注册（短信验证码）、JWT认证、用户资料管理 | Redis存储短信验证码；Spring Security + JWT |
| 租房浏览 | 列表浏览、分页、条件筛选（类型/价格/位置）、详情页、发布页 | 后端 list 端点已连接 MongoDB |
| 租房收藏 | 房源收藏、收藏列表 | 内存存储（in-memory） |
| 预约看房 | 预约表单、预约管理 | 内存存储（in-memory） |
| 二手交易 | 列表浏览、分页、分类筛选、条件搜索、商品详情、发布商品、订单管理 | list 端点连接 MongoDB；其余端点内存存储 |
| AI服务架构 | 5-Agent LangGraph 工作流、Prometheus 监控、结构化日志 | 包含 intent_classifier、parameter_extractor、query_optimizer、data_retrieval、response_formatter |
| AI端点 | `/smart-search`、`/generate-description`、`/moderate`、`/recommend` | smart-search 使用 LangGraph；其余为模板/规则实现 |
| 前端智能搜索组件 | SmartSearchBar.vue 组件（自然语言查询界面） | 组件已实现，**尚未集成到 RentalList 页面** |
| 图片上传 | 单图/多图上传（最多9张）、图片删除、文件验证（5MB） | aiofiles 异步文件操作 |
| 用户界面 | 所有页面组件（Login、Profile、MyItems、MyOrders、Rental/Trade List/Detail/Publish） | 完整的前端路由和页面结构 |

### 🚧 进行中 / 部分实现

| 模块 | 描述 | 待完成 |
|------|------|--------|
| MongoDB 存储迁移 | 租房/交易服务的部分端点（publish/detail/search/favorites/appointments/order）仍使用内存存储 | 将所有端点迁移到 MongoDB |
| Redis 缓存 | AI service 的 `cache.py` 已实现，但各 Agent 中尚未全部集成使用 | 在 `data_retrieval.py` 等 Agent 中启用 Redis 缓存 |
| SmartSearchBar 集成 | SmartSearchBar.vue 组件已存在，但 RentalList.vue 仍使用传统 el-input + el-select 搜索 | 将 SmartSearchBar 组件接入 RentalList 和 TradeList |
| Home.vue 数据 | 首页使用硬编码模拟数据 | 改为从 rental/trade API 获取最新数据 |
| Elasticsearch 集成 | 文档规划了 ES 用于全文搜索，但尚未集成 | 接入 Elasticsearch 实现高性能搜索 |
| 支付集成 | 支付服务已创建支付记录，但微信/支付宝 SDK 未实际接入 | 集成微信支付 V3 API 和支付宝支付接口 |
| 结构化日志 | AI service 根模块配置了 structlog，但各 Agent 节点尚未统一使用 | 在所有 Agent 中统一使用 `get_logger()` |
| 分布式追踪 | 文档规划了 OpenTelemetry + Jaeger，但尚未实现 | 添加 OpenTelemetry instrumentation |

### ❌ 未开始

| 模块 | 描述 |
|------|------|
| 家政服务 | 前端路由占位 `/service`，无后端实现 |
| 兼职招聘 | 前端路由占位 `/job`，无后端实现 |
| 消息通知 | 站内消息、订单状态通知等（SMS/邮件/推送） |
| 用户行为追踪 | AI 推荐系统所需的用户历史行为数据收集 |

---

## 项目结构

```
neighborhood-connect/
├── frontend/                        # Vue 3 前端项目
│   ├── src/
│   │   ├── api/                   # API 接口模块
│   │   │   ├── auth.js           # 认证接口
│   │   │   ├── rental.js         # 租房接口
│   │   │   ├── trade.js          # 交易接口
│   │   │   ├── payment.js        # 支付接口
│   │   │   ├── upload.js         # 上传接口
│   │   │   └── ai.js            # AI接口
│   │   ├── components/            # 通用组件
│   │   │   ├── Layout.vue        # 全局布局
│   │   │   └── SmartSearchBar.vue # AI智能搜索组件
│   │   ├── router/               # 路由配置
│   │   ├── store/                # Pinia 状态
│   │   ├── utils/                # 工具函数
│   │   │   └── request.js        # Axios 封装
│   │   └── views/                # 页面组件
│   │       ├── Home.vue          # 首页（模拟数据，待接入API）
│   │       ├── rental/           # 租房模块
│   │       ├── trade/            # 交易模块
│   │       └── user/             # 用户模块
│   └── package.json
│
├── backend/
│   ├── user-service/              # Java 用户服务 (8081)
│   │   └── src/main/java/com/neighborhood/user/
│   │       ├── controller/AuthController.java
│   │       ├── dto/              # LoginRequest, RegisterRequest, AuthResponse
│   │       ├── entity/User.java
│   │       ├── repository/UserRepository.java
│   │       ├── security/JwtTokenProvider.java
│   │       ├── service/UserService.java
│   │       └── config/           # SecurityConfig, CorsConfig
│   │
│   ├── rental-service/            # Python 租房服务 (8001)
│   │   └── app/
│   │       ├── main.py           # FastAPI 应用
│   │       ├── database.py       # MongoDB 连接
│   │       └── routers/          # API 路由
│   │
│   ├── trade-service/             # Python 交易服务 (8002)
│   │   └── app/
│   │       ├── main.py           # FastAPI 应用
│   │       ├── database.py       # MongoDB 连接
│   │       └── routers/          # API 路由
│   │
│   ├── ai-service/                # Python AI 服务 (8003)
│   │   └── app/
│   │       ├── main.py           # FastAPI 应用 + Prometheus /metrics
│   │       ├── workflow.py       # LangGraph StateGraph（6节点）
│   │       ├── database.py        # MongoDB 连接
│   │       ├── cache.py          # Redis 缓存
│   │       ├── metrics.py        # Prometheus 指标定义
│   │       ├── agents/           # 5个Agent实现
│   │       │   ├── intent_classifier.py
│   │       │   ├── parameter_extractor.py
│   │       │   ├── query_optimizer.py
│   │       │   ├── data_retrieval.py
│   │       │   └── response_formatter.py
│   │       ├── models/           # Pydantic schemas 和 state
│   │       └── utils/            # logger.py (structlog)
│   │
│   ├── payment-service/           # Java 支付服务 (8082)
│   │   └── src/main/java/com/neighborhood/payment/
│   │       ├── controller/PaymentController.java
│   │       ├── dto/             # CreatePaymentRequest, PaymentResponse
│   │       ├── entity/Payment.java
│   │       ├── repository/PaymentRepository.java
│   │       └── service/PaymentService.java
│   │
│   └── upload-service/            # Python 上传服务 (8004)
│       └── main.py               # 单图/多图上传、删除、验证
│
├── nginx/                         # Nginx 配置
├── docker-compose.yml             # Docker Compose
├── init.sql                      # 数据库初始化
└── README.md
```

## API 端口

| 服务 | 端口 | Swagger文档 |
|------|------|------------|
| 用户服务 | 8081 | http://localhost:8081/swagger-ui.html |
| 租房服务 | 8001 | http://localhost:8001/docs |
| 交易服务 | 8002 | http://localhost:8002/docs |
| AI服务 | 8003 | http://localhost:8003/docs |
| AI监控 | 8003 | http://localhost:8003/metrics (Prometheus) |
| 支付服务 | 8082 | http://localhost:8082/swagger-ui.html |
| 上传服务 | 8004 | http://localhost:8004/docs |

## 快速开始

### 环境要求

- Node.js 18+
- Python 3.10+
- Java 17+
- MySQL 8.0
- MongoDB 6.0
- Redis 7.0
- Docker & Docker Compose (可选)

### 1. 克隆项目

```bash
git clone https://github.com/your-repo/neighborhood-connect.git
cd neighborhood-connect
```

### 2. 启动基础设施（Docker）

```bash
docker-compose up -d
```

这将启动：
- MySQL (3306)
- MongoDB (27017)
- Redis (6379)
- Elasticsearch (9200)

### 3. 初始化数据库

```bash
mysql -h localhost -u root -p < init.sql
```

### 4. 启动后端服务

**用户服务（Java）：**
```bash
cd backend/user-service
mvn spring-boot:run
```

**租房服务（Python）：**
```bash
cd backend/rental-service
pip install -r requirements.txt
python app/main.py
```

**交易服务（Python）：**
```bash
cd backend/trade-service
pip install -r requirements.txt
python app/main.py
```

**AI服务（Python）：**
```bash
cd backend/ai-service
pip install -r requirements.txt
python app/main.py
```

**支付服务（Java）：**
```bash
cd backend/payment-service
mvn spring-boot:run
```

**上传服务（Python）：**
```bash
cd backend/upload-service
pip install -r requirements.txt
python main.py
```

### 5. 启动前端

```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:5173

## 前端页面

| 页面 | 路径 | 说明 |
|------|------|------|
| 首页 | `/` | Banner、快捷入口、最新房源/商品（**当前为模拟数据**） |
| 租房列表 | `/rental` | 传统搜索+筛选，**待接入 SmartSearchBar** |
| 房源详情 | `/rental/:id` | 图片、基本信息、预约看房 |
| 发布房源 | `/rental/publish` | 完整表单、图片上传 |
| 交易列表 | `/trade` | 分类筛选、条件搜索 |
| 商品详情 | `/trade/:id` | 购买下单、联系卖家 |
| 发布商品 | `/trade/publish` | 完整表单、图片上传 |
| 登录 | `/user/login` | 登录/注册、短信验证码 |
| 个人中心 | `/user/profile` | 个人信息管理 |
| 我的发布 | `/user/my-items` | 管理已发布商品 |
| 我的订单 | `/user/orders` | 订单列表、状态管理 |

## AI 功能（LangGraph + 多Agent架构）

### 智能搜索

用户通过自然语言查询，AI 自动识别意图并提取参数：

```bash
curl -X POST http://localhost:8003/api/ai/smart-search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "望京3000左右的两室一厅",
    "context": "rental"
  }'
```

响应示例：
```json
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
```

### 多Agent架构

```
用户输入 → IntentClassifier → ParameterExtractor → QueryOptimizer → DataRetrieval → ResponseFormatter → 返回前端
                      ↓
              confidence < 0.7?
                      ↓
              HandleLowConfidence
```

- **IntentClassifierAgent** - 识别租房/交易意图 + 置信度
- **ParameterExtractorAgent** - 从自然语言提取结构化参数（OpenAI Function Calling）
- **QueryOptimizerAgent** - 查询条件优化（地名同义词、类别扩展、价格区间修正）
- **DataRetrievalAgent** - 调用 rental/trade service API，Redis 缓存
- **ResponseFormatterAgent** - 格式化查询理解和返回数据

### Prometheus 监控

AI 服务暴露 Prometheus 指标：`GET http://localhost:8003/metrics`

关键指标：
- `ai_requests_total` - 请求总数（按 intent 和 status 标签）
- `ai_request_duration_seconds` - 请求延迟分布
- `ai_active_requests` - 当前活跃请求数
- `ai_cache_hits_total` / `ai_cache_misses_total` - 缓存命中率
- `ai_agent_success_total` / `ai_agent_failure_total` - Agent 执行结果

### 内容生成、内容审核、智能推荐

```bash
# 内容生成
curl -X POST http://localhost:8003/api/ai/generate-description \
  -H "Content-Type: application/json" \
  -d '{"rental": {"title": "精装两室一厅", "type": "整租", "area": 80, "location": "朝阳区", "facilities": ["空调"]}}'

# 内容审核
curl -X POST http://localhost:8003/api/ai/moderate \
  -H "Content-Type: application/json" \
  -d '{"content": "这是一条正常的房源描述"}'

# 智能推荐
curl -X POST http://localhost:8003/api/ai/recommend \
  -H "Content-Type: application/json" \
  -d '{"user_id": "123", "category": "rental", "limit": 5}'
```

## 支付流程

> ⚠️ 当前为沙箱/模拟模式，微信/支付宝 SDK 尚未实际接入

### 1. 创建支付订单

```bash
curl -X POST http://localhost:8082/api/payment/create \
  -H "Content-Type: application/json" \
  -H "X-User-Id: 1" \
  -d '{
    "orderId": "ORD202401150001",
    "amount": 800.00,
    "paymentMethod": "wechat",
    "returnUrl": "http://localhost/order/success"
  }'
```

### 2. 接入真实支付

支付服务结构已完整，需配置以下环境变量后替换沙箱模式：

```bash
# 微信支付
WECHAT_MCHID=商户号
WECHAT_APPID=AppID
WECHAT_API_KEY=API密钥

# 支付宝
ALIPAY_APP_ID=应用ID
ALIPAY_PRIVATE_KEY=应用私钥
ALIPAY_PUBLIC_KEY=支付宝公钥
```

## 部署

### 生产环境建议

- 使用 **Kubernetes** 进行容器编排
- 使用 **云数据库** (RDS、MongoDB Atlas)
- 配置 **CDN** 加速静态资源
- 使用 **Nginx** 配置 HTTPS 和负载均衡
- 配置 **监控告警** (Prometheus + Grafana)

### Docker 部署

```bash
# 构建所有服务镜像
docker-compose build

# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

## 开发规范

### Git 提交规范

```
feat: 新功能
fix: 修复bug
docs: 文档更新
style: 代码格式
refactor: 重构
test: 测试
chore: 构建/工具
```

### API 规范

- 使用 RESTful 风格
- 统一响应格式
- 请求参数验证
- 错误处理规范

## 许可证

MIT License

## 联系方式

- 项目主页: https://github.com/your-repo/neighborhood-connect
- 问题反馈: Issues
