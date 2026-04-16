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
- **用户服务**: Java Spring Boot 3.2 + Spring Security + JWT
- **租房服务**: Python FastAPI + MongoDB
- **交易服务**: Python FastAPI + MongoDB
- **AI服务**: Python FastAPI + LangGraph
- **支付服务**: Java Spring Boot
- **上传服务**: Python FastAPI

### 数据存储
- **MySQL 8.0** - 主数据库（用户、订单）
- **MongoDB 6.0** - 文档存储（房源、商品详情）
- **Redis 7.0** - 缓存、会话
- **Elasticsearch 8.x** - 搜索引擎

### 基础设施
- **Docker** + Docker Compose
- **Nginx** - API网关、反向代理

## 功能模块

### 已完成 ✅

| 模块 | 描述 | 状态 |
|------|------|------|
| 用户认证 | 登录、注册、JWT认证 | ✅ |
| 租房信息 | 发布、浏览、搜索、收藏、预约看房（内存存储） | ✅ |
| 二手交易 | 发布、浏览、搜索、下单、订单管理（内存存储） | ✅ |
| 用户中心 | 个人资料、我的发布、我的订单 | ✅ |
| AI服务 | 内容生成、内容审核、智能推荐（基础版） | ✅ |
| 支付服务 | 微信/支付宝支付集成 | ✅ |
| 图片上传 | 单图/多图上传、删除 | ✅ |

### 进行中 🚧

| 模块 | 描述 | 状态 |
|------|------|------|
| MongoDB集成 | 租房和交易服务迁移到MongoDB | 🚧 |
| AI智能搜索 | 多Agent架构 + LangGraph编排 | 🚧 |
| 前端智能搜索框 | 自然语言查询界面 | 🚧 |
| 监控系统 | Prometheus + 结构化日志 | 🚧 |

### 支付集成说明

支付服务已集成微信支付和支付宝：

**配置步骤：**

1. 微信支付：
   - 申请微信支付商户号
   - 配置API密钥和证书
   - 设置支付回调地址

2. 支付宝：
   - 申请支付宝开放平台应用
   - 配置应用私钥和支付宝公钥
   - 设置回调地址

3. 环境变量配置：
```bash
# 微信支付
WECHAT_MCHID=你的商户号
WECHAT_APPID=你的AppID
WECHAT_API_KEY=你的API密钥

# 支付宝
ALIPAY_APP_ID=你的应用ID
ALIPAY_PRIVATE_KEY=你的应用私钥
ALIPAY_PUBLIC_KEY=支付宝公钥
```

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
│   │   │   └── upload.js         # 上传接口
│   │   ├── components/            # 通用组件
│   │   │   └── Layout.vue        # 全局布局
│   │   ├── router/               # 路由配置
│   │   ├── store/                # Pinia 状态
│   │   ├── utils/                # 工具函数
│   │   │   └── request.js        # Axios 封装
│   │   └── views/                # 页面组件
│   │       ├── Home.vue          # 首页
│   │       ├── rental/           # 租房模块
│   │       │   ├── RentalList.vue
│   │       │   ├── RentalDetail.vue
│   │       │   └── RentalPublish.vue
│   │       ├── trade/            # 交易模块
│   │       │   ├── TradeList.vue
│   │       │   ├── TradeDetail.vue
│   │       │   └── TradePublish.vue
│   │       └── user/             # 用户模块
│   │           ├── Login.vue
│   │           ├── Profile.vue
│   │           ├── MyItems.vue
│   │           └── MyOrders.vue
│   └── package.json
│
├── backend/
│   ├── user-service/              # Java 用户服务 (8081)
│   │   └── src/main/java/com/neighborhood/user/
│   │       ├── controller/        # REST 控制器
│   │       ├── dto/              # 数据传输对象
│   │       ├── entity/            # JPA 实体
│   │       ├── repository/        # 数据访问层
│   │       ├── security/         # JWT 安全
│   │       └── service/          # 业务逻辑
│   │
│   ├── rental-service/            # Python 租房服务 (8001)
│   │   └── app/
│   │       ├── main.py           # FastAPI 应用
│   │       ├── database.py       # MongoDB 连接
│   │       └── models/           # 数据模型
│   │
│   ├── trade-service/             # Python 交易服务 (8002)
│   │   └── app/
│   │       ├── main.py
│   │       ├── database.py
│   │       └── models/
│   │
│   ├── ai-service/                # Python AI 服务 (8003)
│   │   └── app/
│   │       └── main.py          # LangGraph 工作流
│   │
│   ├── payment-service/           # Java 支付服务 (8082)
│   │   └── src/main/java/com/neighborhood/payment/
│   │       ├── controller/        # REST 控制器
│   │       ├── dto/              # 支付DTO
│   │       ├── entity/           # 支付记录
│   │       └── service/          # 微信/支付宝
│   │
│   └── upload-service/            # Python 上传服务 (8004)
│       └── main.py               # 图片上传处理
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
| 支付服务 | 8082 | http://localhost:8082/swagger-ui.html |
| 上传服务 | 8004 | http://localhost:8004/docs |

## 快速开始

### 环境要求

- Node.js 18+
- Python 3.10+
- Java 17+
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
./mvnw spring-boot:run
# 或使用 Maven
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
| 首页 | `/` | Banner、快捷入口、最新房源/商品 |
| 租房列表 | `/rental` | 搜索、筛选、分页 |
| 房源详情 | `/rental/:id` | 图片轮播、基本信息、预约看房 |
| 发布房源 | `/rental/publish` | 完整表单、图片上传 |
| 交易列表 | `/trade` | 分类筛选、条件搜索 |
| 商品详情 | `/trade/:id` | 购买下单、联系卖家 |
| 发布商品 | `/trade/publish` | 完整表单、图片上传 |
| 登录 | `/user/login` | 登录/注册、验证码 |
| 个人中心 | `/user/profile` | 个人信息管理 |
| 我的发布 | `/user/my-items` | 管理已发布商品 |
| 我的订单 | `/user/orders` | 订单列表、状态管理 |

## AI 功能（LangGraph + 多Agent架构）

### 智能搜索（核心功能）

用户通过自然语言查询，AI自动识别意图并提取参数：

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

### 多Agent架构设计

系统由5个专门的Agent组成：

1. **IntentClassifierAgent** - 识别用户查询属于租房还是交易
2. **ParameterExtractorAgent** - 从自然语言中提取结构化参数
3. **QueryOptimizerAgent** - 优化查询条件，处理同义词和模糊匹配
4. **DataRetrievalAgent** - 调用租房/交易服务API获取数据
5. **ResponseFormatterAgent** - 将结果格式化为前端需要的JSON

工作流程：
```
用户输入 → IntentClassifier → ParameterExtractor → QueryOptimizer → DataRetrieval → ResponseFormatter → 返回前端
```

### 技术亮点

- **LangGraph状态机编排** - 使用条件边实现动态路由
- **OpenAI Function Calling** - 结构化参数提取
- **MongoDB地理位置查询** - 2dsphere索引支持位置搜索
- **Redis缓存** - 相同查询5分钟内直接返回缓存
- **Prometheus监控** - 完整的可观测性指标
- **降级策略** - LLM失败时回退到关键词匹配
- **分布式追踪** - OpenTelemetry + Jaeger

### 内容生成

```bash
curl -X POST http://localhost:8003/api/ai/generate-description \
  -H "Content-Type: application/json" \
  -d '{
    "rental": {
      "title": "精装两室一厅",
      "type": "整租",
      "area": 80,
      "location": "朝阳区",
      "facilities": ["空调", "冰箱", "洗衣机"]
    }
  }'
```

### 内容审核

```bash
curl -X POST http://localhost:8003/api/ai/moderate \
  -H "Content-Type: application/json" \
  -d '{"content": "这是一条正常的房源描述"}'
```

### 智能推荐

```bash
curl -X POST http://localhost:8003/api/ai/recommend \
  -H "Content-Type: application/json" \
  -d '{"user_id": "123", "category": "rental", "limit": 5}'
```

## 支付流程

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

### 2. 微信支付

获取支付参数后，调起微信支付：
```javascript
WeChatJSBridge.invoke('getBrandWCPayRequest', params)
```

### 3. 支付宝支付

使用返回的表单数据调起支付：
```javascript
const form = response.paymentData.formData
document.querySelector('#pay-form').innerHTML = form
document.querySelector('#pay-form').submit()
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
