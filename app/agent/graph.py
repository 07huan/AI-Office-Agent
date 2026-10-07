from typing import TypedDict

from langgraph.graph import (
    StateGraph,
    START,
    END
)

from app.llm import (
    classify_intent,
    generate_customer_report
)

from app.tools.customer_tools import (
    query_customers
)

from app.tools.todo_tools import (
    add_todo,
    query_todos
)

from app.tools.knowledge_tools import (
    query_knowledge_base
)

from app.tools.feishu_tools import (
    send_feishu_message
)


# =========================
# Agent State
# =========================

class AgentState(TypedDict):

    message: str

    route: str

    result: list | dict | str

    todo_title: str

    customer_status: str

    user_id: int

    send_to_feishu: bool


# =========================
# 意图识别节点
# =========================

def intent_node(
        state: AgentState
):

    message = state["message"]

    print(
        "用户消息：",
        message
    )

    intent = classify_intent(
        message
    )

    route = intent.get(
        "route",
        "unknown"
    )

    todo_title = intent.get(
        "todo_title",
        ""
    )

    customer_status = intent.get(
        "customer_status",
        ""
    )

    send_to_feishu = intent.get(
        "send_to_feishu",
        False
    )

    allowed_routes = {
        "query_customer",
        "add_todo",
        "query_todo",
        "knowledge_base",
        "unknown"
    }

    if route not in allowed_routes:

        route = "unknown"

    allowed_customer_status = {
        "",
        "待跟进",
        "跟进中",
        "已成交"
    }

    if (
        customer_status
        not in allowed_customer_status
    ):

        customer_status = ""

    print(
        "识别意图：",
        route
    )

    print(
        "客户状态：",
        customer_status
    )

    print(
        "是否发送飞书：",
        send_to_feishu
    )

    return {
        "route": route,

        "todo_title":
            todo_title,

        "customer_status":
            customer_status,

        "send_to_feishu":
            send_to_feishu
    }


# =========================
# 第一层条件路由
# =========================

def route_node(
        state: AgentState
):

    return state["route"]


# =========================
# 客户查询节点
# =========================

def query_customer_node(
        state: AgentState
):

    print(
        "正在查询客户..."
    )

    customer_status = (
        state.get(
            "customer_status",
            ""
        )
    )

    if customer_status:

        customers = query_customers(
            customer_status
        )

    else:

        customers = query_customers()

    return {
        "result": customers
    }


# =========================
# 判断客户查询后是否发送飞书
# =========================

def after_customer_node(
        state: AgentState
):

    if state.get(
        "send_to_feishu",
        False
    ):

        return "send_feishu"

    return "end"


# =========================
# 飞书节点
# =========================

def send_feishu_node(
        state: AgentState
):

    print(
        "正在生成客户跟进日报..."
    )

    customers = state.get(
        "result",
        []
    )

    report = (
        generate_customer_report(
            customers
        )
    )

    print(
        "正在发送日报到飞书..."
    )

    feishu_result = (
        send_feishu_message(
            report
        )
    )

    print(
        "飞书发送结果：",
        feishu_result
    )

    return {
        "result": {
            "report": report,
            "feishu":
                feishu_result
        }
    }


# =========================
# 创建待办节点
# =========================

def add_todo_node(
        state: AgentState
):

    print(
        "正在创建待办..."
    )

    todo = add_todo(
        state["todo_title"],
        state["user_id"]
    )

    return {
        "result": todo
    }


# =========================
# 查询待办节点
# =========================

def query_todo_node(
        state: AgentState
):

    print(
        "正在查询待办..."
    )

    todos = query_todos(
        state["user_id"],
        "未完成"
    )

    return {
        "result": todos
    }


# =========================
# RAG 知识库节点
# =========================

def knowledge_base_node(
        state: AgentState
):

    print(
        "正在查询知识库..."
    )

    knowledge = (
        query_knowledge_base(
            state["message"]
        )
    )

    return {
        "result": knowledge
    }


# =========================
# 无法识别节点
# =========================

def unknown_node(
        state: AgentState
):

    print(
        "暂时无法识别这个任务"
    )

    return {
        "result": {
            "message":
                "暂时无法处理这个任务"
        }
    }


# =========================
# 创建 LangGraph
# =========================

graph = StateGraph(
    AgentState
)


# =========================
# 添加节点
# =========================

graph.add_node(
    "intent",
    intent_node
)

graph.add_node(
    "query_customer",
    query_customer_node
)

graph.add_node(
    "send_feishu",
    send_feishu_node
)

graph.add_node(
    "add_todo",
    add_todo_node
)

graph.add_node(
    "query_todo",
    query_todo_node
)

graph.add_node(
    "knowledge_base",
    knowledge_base_node
)

graph.add_node(
    "unknown",
    unknown_node
)


# =========================
# START → 意图识别
# =========================

graph.add_edge(
    START,
    "intent"
)


# =========================
# 第一层路由
# =========================

graph.add_conditional_edges(

    "intent",

    route_node,

    {
        "query_customer":
            "query_customer",

        "add_todo":
            "add_todo",

        "query_todo":
            "query_todo",

        "knowledge_base":
            "knowledge_base",

        "unknown":
            "unknown"
    }
)


# =========================
# 客户查询后的第二层路由
# =========================

graph.add_conditional_edges(

    "query_customer",

    after_customer_node,

    {
        "send_feishu":
            "send_feishu",

        "end":
            END
    }
)


# =========================
# 飞书发送完成 → END
# =========================

graph.add_edge(
    "send_feishu",
    END
)


# =========================
# 其他工具执行完成 → END
# =========================

graph.add_edge(
    "add_todo",
    END
)

graph.add_edge(
    "query_todo",
    END
)

graph.add_edge(
    "knowledge_base",
    END
)

graph.add_edge(
    "unknown",
    END
)


# =========================
# 编译 Agent
# =========================

app = graph.compile()