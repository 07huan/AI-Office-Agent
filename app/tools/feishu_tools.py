import os
import json
import requests

from dotenv import load_dotenv

load_dotenv()


# =========================
# 获取 tenant_access_token
# =========================

def get_tenant_access_token():

    app_id = os.getenv(
        "FEISHU_APP_ID"
    )

    app_secret = os.getenv(
        "FEISHU_APP_SECRET"
    )

    url = (
        "https://open.feishu.cn/"
        "open-apis/auth/v3/"
        "tenant_access_token/internal"
    )

    data = {
        "app_id": app_id,
        "app_secret": app_secret
    }

    response = requests.post(
        url,
        json=data,
        timeout=10
    )

    result = response.json()

    if result.get("code") != 0:

        raise Exception(
            "获取飞书 tenant_access_token 失败："
            f"{result.get('msg')}"
        )

    return result.get(
        "tenant_access_token"
    )


# =========================
# 获取群聊 chat_id
# =========================

def get_chat_id(
        chat_name: str
):

    token = (
        get_tenant_access_token()
    )

    url = (
        "https://open.feishu.cn/"
        "open-apis/im/v1/chats/search"
    )

    headers = {
        "Authorization":
            f"Bearer {token}"
    }

    response = requests.get(
        url,
        headers=headers,
        params={
            "query": chat_name
        },
        timeout=10
    )

    result = response.json()

    if result.get("code") != 0:

        raise Exception(
            "搜索飞书群失败："
            f"{result.get('msg')}"
        )

    items = (
        result
        .get("data", {})
        .get("items", [])
    )

    for chat in items:

        if (
            chat.get("name")
            == chat_name
        ):

            return chat.get(
                "chat_id"
            )

    raise Exception(
        f"没有找到飞书群：{chat_name}"
    )


# =========================
# 发送飞书消息
# =========================

def send_feishu_message(
        text: str,
        chat_name: str =
        "AI Office Agent 测试群"
):

    token = (
        get_tenant_access_token()
    )

    chat_id = get_chat_id(
        chat_name
    )

    url = (
        "https://open.feishu.cn/"
        "open-apis/im/v1/messages"
        "?receive_id_type=chat_id"
    )

    headers = {
        "Authorization":
            f"Bearer {token}",

        "Content-Type":
            "application/json; charset=utf-8"
    }

    data = {
        "receive_id": chat_id,

        "msg_type": "text",

        "content": json.dumps(
            {
                "text": text
            },
            ensure_ascii=False
        )
    }

    response = requests.post(
        url,
        headers=headers,
        json=data,
        timeout=10
    )

    result = response.json()

    if result.get("code") != 0:

        raise Exception(
            "发送飞书消息失败："
            f"{result.get('msg')}"
        )

    return {
        "success": True,
        "message":
            "飞书消息发送成功"
    }