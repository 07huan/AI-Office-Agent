# AI Office Agent

一个基于 FastAPI、DeepSeek、LangGraph、RAG 和 MySQL 构建的 AI 办公任务助手。

用户可以通过自然语言与系统交互，Agent 自动识别用户意图，并根据任务调用客户查询、待办管理、知识库检索、飞书消息推送等工具完成办公任务。

## 项目功能

### 用户系统

- 用户注册
- 用户登录
- Argon2 密码哈希
- JWT 身份认证
- 用户数据隔离

### AI Agent

使用 DeepSeek 对用户自然语言进行意图识别和参数提取。

目前支持：

- 客户信息查询
- 按客户状态查询
- 创建待办
- 查询待办
- 企业知识库问答
- 客户跟进日报生成
- 飞书机器人消息推送

### LangGraph 工作流

使用 LangGraph 编排 Agent 工作流程。

基本流程：

```text
用户请求
   ↓
FastAPI
   ↓
DeepSeek 意图识别
   ↓
LangGraph
   ↓
条件路由
   ├── 客户查询 Tool
   ├── 待办 Tool
   ├── RAG Tool
   └── 飞书 Tool
   ↓
DeepSeek 生成最终回答
   ↓
返回前端
```

客户日报推送支持多步骤工作流：

```text
用户
 ↓
意图识别
 ↓
查询客户
 ↓
MySQL
 ↓
DeepSeek 生成客户跟进日报
 ↓
飞书 Tool
 ↓
飞书 OpenAPI
 ↓
飞书群
```

## RAG 企业知识库

项目集成基于 Chroma 的 RAG 知识库。

处理流程：

```text
企业知识文档
 ↓
TextLoader
 ↓
RecursiveCharacterTextSplitter
 ↓
Embedding
 ↓
Chroma
 ↓
相似度检索
 ↓
DeepSeek
 ↓
知识库回答
```

目前使用公司规则文档作为知识库测试数据。

## 飞书机器人

系统接入飞书开放平台 API。

实现：

- tenant_access_token 获取
- 飞书群搜索
- 群聊定位
- 机器人消息发送
- Agent 自动生成客户跟进日报
- 自动推送日报到飞书群

示例：

```text
帮我生成客户跟进日报，并发送到飞书
```

Agent 会自动查询客户数据、生成日报并通过飞书机器人发送。

## 技术栈

### 后端

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- MySQL
- PyMySQL

### AI / Agent

- DeepSeek API
- LangGraph
- LangChain
- Function / Tool Calling 思路
- Prompt Engineering

### RAG

- LangChain
- Chroma
- DashScope Embedding

### 用户认证

- JWT
- Argon2

### 第三方 API

- Feishu OpenAPI

### 前端

- HTML
- CSS
- JavaScript

## 项目目录

```text
office_agent/
│
├── app/
│   ├── agent/
│   │   └── graph.py
│   │
│   ├── rag/
│   │   ├── document_loader.py
│   │   └── vector_store.py
│   │
│   ├── tools/
│   │   ├── customer_tools.py
│   │   ├── todo_tools.py
│   │   ├── knowledge_tools.py
│   │   ├── task_log_tools.py
│   │   └── feishu_tools.py
│   │
│   ├── auth.py
│   ├── chat_memory.py
│   ├── database.py
│   ├── llm.py
│   ├── models.py
│   └── schemas.py
│
├── frontend/
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── app.js
│   └── style.css
│
├── knowledge/
│   └── company_rules.txt
│
├── main.py
├── requirements.txt
├── .gitignore
└── README.md
```

## 环境配置

项目使用 `.env` 保存敏感配置。

请在项目根目录创建：

```text
.env
```

根据自己的环境配置以下变量：

```env
DEEPSEEK_API_KEY=your_deepseek_api_key

DASHSCOPE_API_KEY=your_dashscope_api_key

DATABASE_URL=your_database_url

JWT_SECRET_KEY=your_jwt_secret

FEISHU_APP_ID=your_feishu_app_id
FEISHU_APP_SECRET=your_feishu_app_secret
```

请勿将真实 `.env` 文件上传到 GitHub。

## 安装依赖

```bash
pip install -r requirements.txt
```

## 启动后端

```bash
uvicorn main:app --port 8082
```

启动成功后：

```text
http://127.0.0.1:8082
```

FastAPI API 文档：

```text
http://127.0.0.1:8082/docs
```

## 启动前端

进入：

```bash
cd frontend
```

启动静态服务器：

```bash
python -m http.server 5500
```

浏览器访问：

```text
http://127.0.0.1:5500/login.html
```

## 示例指令

```text
查询待跟进客户

查询已成交客户

帮我创建一个待办，明天联系张三

查询我的未完成待办

客户连续三次没有回复应该怎么办？

帮我生成客户跟进日报，并发送到飞书
```

## 项目特点

项目重点不是单纯调用大模型 API，而是将大模型与实际业务工具结合。

通过：

```text
LLM
+
LangGraph
+
Tools
+
MySQL
+
RAG
+
第三方 API
```

实现一个能够理解任务、选择工具并执行办公任务的 AI Agent。

## 后续优化方向

- 增加更完善的客户跟进记录
- 根据日期生成真正的每日跟进统计
- 增加更多办公工具
- 完善多轮会话持久化
- 优化 Agent 异常处理
- 增加更多第三方办公平台集成