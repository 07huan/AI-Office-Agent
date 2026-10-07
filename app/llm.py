import os
import json

from dotenv import load_dotenv
from openai import OpenAI

from app.chat_memory import get_chat_history, add_message

load_dotenv()

deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")

client = OpenAI(
    api_key=deepseek_api_key,
    base_url="https://api.deepseek.com"
)


# =========================
# LLM 意图识别
# =========================

def classify_intent(message: str):

    response = client.chat.completions.create(
        model="deepseek-chat",

        messages=[
            {
                "role": "system",
                "content": """
你是一个 AI 办公助手的意图分类器。

你的任务是根据用户输入，
判断应该执行哪一种办公任务，
并提取任务需要的参数。

只能从下面 5 种 route 中选择：

1. query_customer

用于查询客户、客户列表、
客户跟进状态、客户日报等数据库信息。

例如：

- 查询待跟进客户
- 查询已成交客户
- 查询跟进中的客户
- 有哪些客户正在跟进
- 查询所有客户
- 生成客户跟进日报
- 生成今天的客户跟进日报

customer_status 规则：

如果用户查询“待跟进客户”：
customer_status = "待跟进"

如果用户查询“跟进中客户”：
customer_status = "跟进中"

如果用户查询“已成交客户”：
customer_status = "已成交"

如果用户没有指定状态：
customer_status = ""


2. add_todo

用于创建或添加待办任务。

例如：

- 创建待办，明天联系张三
- 添加待办：整理客户资料
- 帮我记一个待办，下午联系李四


3. query_todo

用于查询用户自己的待办任务。

例如：

- 查询未完成待办
- 我有哪些待办
- 看一下我的待办事项


4. knowledge_base

用于查询公司规定、业务规范、
处理方法、客户跟进规则等知识库内容。

例如：

- 客户连续3次没有回复应该怎么办？
- 客户完成付款后状态怎么改？
- 新客户多久需要第一次跟进？
- 公司对客户跟进有什么规定？


5. unknown

不属于以上任何任务时使用。


除了判断 route，
还需要判断用户是否要求
把结果发送到飞书。

如果用户明确要求：

- 发送到飞书
- 发到飞书
- 发到飞书群
- 同步到飞书
- 把结果发送到飞书

则：

send_to_feishu = true

否则：

send_to_feishu = false


注意：

send_to_feishu 不是 route。

例如：

用户：
查询待跟进客户并发送到飞书

返回：

{
    "route": "query_customer",
    "todo_title": "",
    "customer_status": "待跟进",
    "send_to_feishu": true
}


用户：
帮我生成今天的客户跟进日报，并发送到飞书

返回：

{
    "route": "query_customer",
    "todo_title": "",
    "customer_status": "",
    "send_to_feishu": true
}


固定返回格式：

{
    "route": "分类名称",
    "todo_title": "",
    "customer_status": "",
    "send_to_feishu": false
}


如果 route 是 add_todo：

todo_title 填写具体待办内容。


其他情况下：

todo_title 默认返回空字符串。


不要解释。
不要添加 Markdown。
只返回 JSON。
"""
            },

            {
                "role": "user",
                "content": message
            }
        ],

        response_format={
            "type": "json_object"
        }
    )

    content = (
        response
        .choices[0]
        .message
        .content
    )

    result = json.loads(content)

    return result


# =========================
# 生成客户日报
# =========================

def generate_customer_report(
        customers
):

    response = client.chat.completions.create(
        model="deepseek-chat",

        messages=[
            {
                "role": "system",
                "content": """
你是一个 AI 办公助手。

请根据提供的客户数据，
整理一份简洁的客户跟进日报。

要求：

1. 标题为“客户跟进日报”
2. 统计客户总数
3. 根据客户状态进行简单整理
4. 列出重要客户信息
5. 给出简短的跟进总结
6. 不要编造客户数据中不存在的信息
7. 适合直接发送到飞书群
8. 使用纯文本，不要使用 Markdown 表格
"""
            },

            {
                "role": "user",
                "content": f"""
客户数据：

{json.dumps(
    customers,
    ensure_ascii=False,
    default=str
)}
"""
            }
        ]
    )

    report = (
        response
        .choices[0]
        .message
        .content
    )

    return report


# =========================
# 生成最终自然语言回答
# =========================

def generate_final_answer(
        user_message: str,
        tool_result,
        conversation_id: str
):

    history = get_chat_history(
        conversation_id
    )

    messages = [
        {
            "role": "system",
            "content": """
你是一个 AI 办公助手。

请根据：

1. 用户当前问题
2. 聊天历史
3. 工具执行结果

生成最终回答。

要求：

- 回答简洁
- 回答自然
- 回答准确
- 优先依据工具结果回答
- 不要编造工具结果中不存在的信息
- 如果工具结果已经能够直接回答问题，
  不要额外扩展无关建议
"""
        }
    ]

    messages.extend(history)

    messages.append({
        "role": "user",

        "content": f"""
用户当前问题：
{user_message}

工具执行结果：
{json.dumps(
    tool_result,
    ensure_ascii=False,
    default=str
)}
"""
    })

    response = (
        client
        .chat
        .completions
        .create(
            model="deepseek-chat",
            messages=messages
        )
    )

    answer = (
        response
        .choices[0]
        .message
        .content
    )

    add_message(
        conversation_id,
        "user",
        user_message
    )

    add_message(
        conversation_id,
        "assistant",
        answer
    )

    return answer