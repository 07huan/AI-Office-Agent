from fastapi import FastAPI, Depends, HTTPException
from pwdlib import PasswordHash
from app.llm import generate_final_answer
from app.schemas import ChatRequest, UserRegister
from app import models
from app.database import engine, get_db
from app.agent.graph import app as agent_app
from app.auth import create_access_token, get_current_user_id
from fastapi.security import OAuth2PasswordRequestForm
from app.tools.task_log_tools import save_task_log
from fastapi.middleware.cors import CORSMiddleware

from urllib.parse import urlencode
import os
import requests


# =========================
# 初始化数据库
# =========================

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# =========================
# CORS
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


password_hash = PasswordHash.recommended()


# =========================
# 首页
# =========================

@app.get("/")
def home():
    return {
        "message": "AI Office Agent is running"
    }


# =========================
# AI 对话
# =========================

@app.post("/chat")
def chat(
    request: ChatRequest,
    user_id: int = Depends(get_current_user_id)
):
    result = agent_app.invoke({
        "message": request.message,
        "route": "",
        "result": [],
        "todo_title": "",
        "user_id": user_id
    })

    answer = generate_final_answer(
        request.message,
        result["result"],
        request.conversation_id
    )

    route = result["route"]

    tool_name_map = {
        "query_customer": "query_customers",
        "add_todo": "add_todo",
        "query_todo": "query_todos",
        "knowledge_base": "query_knowledge_base",
        "unknown": "none"
    }

    tool_name = tool_name_map.get(
        route,
        "none"
    )

    save_task_log(
        user_id=user_id,
        user_message=request.message,
        route=route,
        tool_name=tool_name,
        tool_result=result["result"],
        final_answer=answer
    )

    return {
        "message": answer
    }


# =========================
# 用户注册
# =========================

@app.post("/register")
def register(
    request: UserRegister,
    db=Depends(get_db)
):
    existing_user = db.query(models.User).filter(
        models.User.username == request.username
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="用户名已经存在"
        )

    existing_email = db.query(models.User).filter(
        models.User.email == request.email
    ).first()

    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="邮箱已经存在"
        )

    hashed_password = password_hash.hash(
        request.password
    )

    user = models.User(
        username=request.username,
        email=request.email,
        password=hashed_password
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "message": "注册成功",
        "user_id": user.id
    }


# =========================
# 用户登录
# =========================

@app.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db=Depends(get_db)
):
    user = db.query(models.User).filter(
        models.User.username == form_data.username
    ).first()

    if not user:
        raise HTTPException(
            status_code=400,
            detail="用户名不存在"
        )

    if not password_hash.verify(
        form_data.password,
        user.password
    ):
        raise HTTPException(
            status_code=400,
            detail="密码错误"
        )

    access_token = create_access_token(
        user.id
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# =========================
# 客户管理
# =========================

@app.get("/customers")
def get_customers(
    user_id: int = Depends(get_current_user_id),
    db=Depends(get_db)
):
    customers = db.query(
        models.Customer
    ).order_by(
        models.Customer.id.desc()
    ).all()

    result = []

    for customer in customers:
        result.append({
            "id": customer.id,
            "name": customer.name,
            "company": customer.company,
            "status": customer.status,
            "phone": customer.phone,
            "created_at": str(customer.created_at)
        })

    return result


# =========================
# 待办管理
# =========================

@app.get("/todos")
def get_todos(
    user_id: int = Depends(get_current_user_id),
    db=Depends(get_db)
):
    todos = db.query(
        models.Todo
    ).filter(
        models.Todo.user_id == user_id
    ).order_by(
        models.Todo.id.desc()
    ).all()

    result = []

    for todo in todos:
        result.append({
            "id": todo.id,
            "title": todo.title,
            "status": todo.status,
            "created_at": str(todo.created_at)
        })

    return result


# =========================
# 任务日志
# =========================

@app.get("/task-logs")
def get_task_logs(
    user_id: int = Depends(get_current_user_id),
    db=Depends(get_db)
):
    logs = db.query(
        models.TaskLog
    ).filter(
        models.TaskLog.user_id == user_id
    ).order_by(
        models.TaskLog.id.desc()
    ).all()

    result = []

    for log in logs:
        result.append({
            "id": log.id,
            "user_message": log.user_message,
            "route": log.route,
            "tool_name": log.tool_name,
            "tool_result": log.tool_result,
            "final_answer": log.final_answer,
            "status": log.status,
            "created_at": str(log.created_at)
        })

    return result


# ============================================================
# 飞书 OAuth
# ============================================================


# =========================
# 飞书登录
# =========================

@app.get("/feishu/login")
def feishu_login():

    app_id = os.getenv("FEISHU_APP_ID")

    redirect_uri = (
        "http://127.0.0.1:8082/feishu/callback"
    )

    params = {
        "app_id": app_id,
        "redirect_uri": redirect_uri,
        "scope": "im:chat:read"
    }

    auth_url = (
        "https://accounts.feishu.cn/"
        "open-apis/authen/v1/authorize?"
        + urlencode(params)
    )

    return {
        "auth_url": auth_url
    }


# =========================
# 飞书授权回调
# =========================

@app.get("/feishu/callback")
def feishu_callback(code: str):

    app_id = os.getenv("FEISHU_APP_ID")
    app_secret = os.getenv("FEISHU_APP_SECRET")

    print("是否收到 code：", bool(code))
    print(
        "APP_ID 是否读取成功：",
        bool(app_id)
    )
    print(
        "APP_SECRET 是否读取成功：",
        bool(app_secret)
    )

    if not app_id or not app_secret:
        raise HTTPException(
            status_code=500,
            detail="飞书 App ID 或 App Secret 未配置"
        )

    # --------------------------------
    # 第一步：
    # 获取 app_access_token
    # --------------------------------

    app_token_url = (
        "https://open.feishu.cn/"
        "open-apis/auth/v3/"
        "app_access_token/internal"
    )

    app_token_response = requests.post(
        app_token_url,
        json={
            "app_id": app_id,
            "app_secret": app_secret
        },
        timeout=10
    )

    app_token_result = app_token_response.json()

    print(
        "App Token HTTP 状态码：",
        app_token_response.status_code
    )

    print(
        "App Token code：",
        app_token_result.get("code")
    )

    app_access_token = (
        app_token_result.get(
            "app_access_token"
        )
    )

    if not app_access_token:
        return {
            "message": "获取 app_access_token 失败",
            "code": app_token_result.get("code"),
            "msg": app_token_result.get("msg")
        }

    print(
        "是否拿到 app_access_token：",
        True
    )

    # --------------------------------
    # 第二步：
    # code 换 user_access_token
    # --------------------------------

    user_token_url = (
        "https://open.feishu.cn/"
        "open-apis/authen/v1/access_token"
    )

    headers = {
        "Authorization":
            f"Bearer {app_access_token}",
        "Content-Type":
            "application/json; charset=utf-8"
    }

    user_token_data = {
        "grant_type": "authorization_code",
        "code": code
    }

    user_token_response = requests.post(
        user_token_url,
        headers=headers,
        json=user_token_data,
        timeout=10
    )

    user_token_result = (
        user_token_response.json()
    )

    print(
        "User Token HTTP 状态码：",
        user_token_response.status_code
    )

    print(
        "User Token code：",
        user_token_result.get("code")
    )

    # v1 接口返回的数据在 data 里面
    user_data = (
        user_token_result.get("data") or {}
    )

    user_access_token = (
        user_data.get("access_token")
    )

    print(
        "是否拿到 user_access_token：",
        bool(user_access_token)
    )

    if not user_access_token:
        return {
            "message": "获取 user_access_token 失败",
            "code": user_token_result.get("code"),
            "msg": user_token_result.get("msg")
        }

    # --------------------------------
    # 第三步：
    # 使用用户身份查询群聊
    # --------------------------------

    chat_url = (
        "https://open.feishu.cn/"
        "open-apis/im/v1/chats"
    )

    chat_headers = {
        "Authorization":
            f"Bearer {user_access_token}",
        "Content-Type":
            "application/json; charset=utf-8"
    }

    chat_response = requests.get(
        chat_url,
        headers=chat_headers,
        params={
            "page_size": 100
        },
        timeout=10
    )

    chat_result = chat_response.json()

    print(
        "群聊 API HTTP 状态码：",
        chat_response.status_code
    )

    print(
        "群聊 API code：",
        chat_result.get("code")
    )

    chats = (
        chat_result.get("data", {})
        .get("items", [])
    )

    # 只打印群名称和 chat_id
    # 不打印 user_access_token
    print("当前用户可见群聊：")

    safe_chats = []

    for chat in chats:

        chat_info = {
            "name": chat.get("name"),
            "chat_id": chat.get("chat_id")
        }

        safe_chats.append(chat_info)

        print(
            chat_info["name"],
            "->",
            chat_info["chat_id"]
        )

    return {
        "message": "飞书授权成功",
        "chats": safe_chats
    }