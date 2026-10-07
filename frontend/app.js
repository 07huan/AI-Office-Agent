const API_BASE_URL = "http://127.0.0.1:8082";


// =========================
// 登录
// =========================

const loginForm = document.getElementById("loginForm");

if (loginForm) {

    loginForm.addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();

            const username =
                document.getElementById("username").value;

            const password =
                document.getElementById("password").value;

            const errorMessage =
                document.getElementById("errorMessage");

            errorMessage.textContent = "";

            try {

                const formData =
                    new URLSearchParams();

                formData.append(
                    "username",
                    username
                );

                formData.append(
                    "password",
                    password
                );


                const response =
                    await fetch(
                        `${API_BASE_URL}/login`,
                        {
                            method: "POST",

                            headers: {
                                "Content-Type":
                                    "application/x-www-form-urlencoded"
                            },

                            body: formData
                        }
                    );


                const data =
                    await response.json();


                if (!response.ok) {

                    errorMessage.textContent =
                        data.detail || "登录失败";

                    return;
                }


                localStorage.setItem(
                    "access_token",
                    data.access_token
                );


                window.location.href =
                    "index.html";

            } catch (error) {

                errorMessage.textContent =
                    "无法连接服务器";

                console.error(error);
            }

        }
    );
}


// =========================
// 注册
// =========================

const registerForm =
    document.getElementById("registerForm");

if (registerForm) {

    registerForm.addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();


            const username =
                document.getElementById("username").value;

            const email =
                document.getElementById("email").value;

            const password =
                document.getElementById("password").value;

            const errorMessage =
                document.getElementById("errorMessage");

            errorMessage.textContent = "";


            try {

                const response =
                    await fetch(
                        `${API_BASE_URL}/register`,
                        {
                            method: "POST",

                            headers: {
                                "Content-Type":
                                    "application/json"
                            },

                            body: JSON.stringify({
                                username: username,
                                email: email,
                                password: password
                            })
                        }
                    );


                const data =
                    await response.json();


                if (!response.ok) {

                    errorMessage.textContent =
                        data.detail || "注册失败";

                    return;
                }


                alert("注册成功，请登录");

                window.location.href =
                    "login.html";


            } catch (error) {

                errorMessage.textContent =
                    "无法连接服务器";

                console.error(error);
            }

        }
    );
}


// =========================
// 登录状态检查
// =========================

if (
    window.location.pathname.endsWith(
        "index.html"
    )
) {

    const token =
        localStorage.getItem(
            "access_token"
        );


    if (!token) {

        window.location.href =
            "login.html";
    }
}


// =========================
// JWT请求
// =========================

async function authFetch(
    url,
    options = {}
) {

    const token =
        localStorage.getItem(
            "access_token"
        );


    if (!token) {

        window.location.href =
            "login.html";

        return null;
    }


    options.headers = {
        ...(options.headers || {}),

        "Authorization":
            `Bearer ${token}`
    };


    const response =
        await fetch(url, options);


    if (response.status === 401) {

        localStorage.removeItem(
            "access_token"
        );

        localStorage.removeItem(
            "conversation_id"
        );

        alert(
            "登录已过期，请重新登录"
        );

        window.location.href =
            "login.html";

        return null;
    }


    return response;
}


// =========================
// 页面切换
// =========================

function switchPage(
    pageName,
    menuElement
) {

    document
        .querySelectorAll(".page")
        .forEach(page => {

            page.classList.remove(
                "active-page"
            );

        });


    document
        .querySelectorAll(".menu-item")
        .forEach(item => {

            item.classList.remove(
                "active"
            );

        });


    const pageMap = {

        chat:
            "chatPage",

        customers:
            "customersPage",

        todos:
            "todosPage",

        knowledge:
            "knowledgePage",

        logs:
            "logsPage"

    };


    const page =
        document.getElementById(
            pageMap[pageName]
        );


    if (page) {

        page.classList.add(
            "active-page"
        );
    }


    if (menuElement) {

        menuElement.classList.add(
            "active"
        );
    }


    if (pageName === "customers") {

        loadCustomers();

    } else if (pageName === "todos") {

        loadTodos();

    } else if (pageName === "logs") {

        loadTaskLogs();
    }
}


// =========================
// AI聊天
// =========================

async function sendMessage() {

    const input =
        document.getElementById(
            "messageInput"
        );

    const sendButton =
        document.getElementById(
            "sendButton"
        );


    if (!input) return;


    const message =
        input.value.trim();


    if (!message) return;


    addMessage(
        message,
        "user"
    );


    input.value = "";


    sendButton.disabled = true;

    sendButton.textContent =
        "处理中...";


    try {

        const response =
            await authFetch(
                `${API_BASE_URL}/chat`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        message: message,

                        conversation_id:
                            getConversationId()
                    })
                }
            );


        if (!response) return;


        const data =
            await response.json();


        if (!response.ok) {

            addMessage(
                data.detail ||
                "请求失败",
                "ai"
            );

            return;
        }


        addMessage(
            data.message,
            "ai"
        );


    } catch (error) {

        addMessage(
            "无法连接服务器，请检查 FastAPI 是否已经启动。",
            "ai"
        );

        console.error(error);


    } finally {

        sendButton.disabled = false;

        sendButton.textContent =
            "发送";
    }
}


// =========================
// 显示聊天消息
// =========================

function addMessage(
    content,
    role
) {

    const messages =
        document.getElementById(
            "messages"
        );

    const welcome =
        document.getElementById(
            "welcome"
        );


    if (!messages) return;


    if (welcome) {

        welcome.style.display =
            "none";
    }


    const messageDiv =
        document.createElement(
            "div"
        );


    messageDiv.className =
        `message ${role}`;


    const contentDiv =
        document.createElement(
            "div"
        );


    contentDiv.className =
        "message-content";


    contentDiv.textContent =
        content;


    messageDiv.appendChild(
        contentDiv
    );


    messages.appendChild(
        messageDiv
    );


    const chatContainer =
        document.getElementById(
            "chatContainer"
        );


    if (chatContainer) {

        chatContainer.scrollTop =
            chatContainer.scrollHeight;
    }
}


// =========================
// 示例问题
// =========================

function useExample(text) {

    const input =
        document.getElementById(
            "messageInput"
        );


    if (!input) return;


    input.value = text;

    input.focus();
}


// =========================
// conversation_id
// =========================

function getConversationId() {

    let conversationId =
        localStorage.getItem(
            "conversation_id"
        );


    if (!conversationId) {

        conversationId =
            "web_" + Date.now();


        localStorage.setItem(
            "conversation_id",
            conversationId
        );
    }


    return conversationId;
}


// =========================
// 客户管理
// =========================

async function loadCustomers() {

    const loading =
        document.getElementById(
            "customersLoading"
        );

    const body =
        document.getElementById(
            "customersBody"
        );


    if (!body) return;


    loading.style.display =
        "block";

    body.innerHTML = "";


    try {

        const response =
            await authFetch(
                `${API_BASE_URL}/customers`
            );


        if (!response) return;


        const customers =
            await response.json();


        loading.style.display =
            "none";


        if (!response.ok) {

            loading.style.display =
                "block";

            loading.textContent =
                "客户数据加载失败";

            return;
        }


        if (customers.length === 0) {

            loading.style.display =
                "block";

            loading.textContent =
                "暂无客户数据";

            return;
        }


        customers.forEach(
            customer => {

                const tr =
                    document.createElement(
                        "tr"
                    );


                tr.innerHTML = `
                    <td>${escapeHtml(customer.id)}</td>

                    <td>
                        ${escapeHtml(customer.name || "-")}
                    </td>

                    <td>
                        ${escapeHtml(customer.company || "-")}
                    </td>

                    <td>
                        ${escapeHtml(customer.phone || "-")}
                    </td>

                    <td>
                        <span class="status">
                            ${escapeHtml(customer.status || "-")}
                        </span>
                    </td>

                    <td>
                        ${formatTime(customer.created_at)}
                    </td>
                `;


                body.appendChild(tr);
            }
        );


    } catch (error) {

        loading.style.display =
            "block";

        loading.textContent =
            "无法加载客户数据";

        console.error(error);
    }
}


// =========================
// 待办事项
// =========================

async function loadTodos() {

    const loading =
        document.getElementById(
            "todosLoading"
        );

    const list =
        document.getElementById(
            "todoList"
        );


    if (!list) return;


    loading.style.display =
        "block";

    loading.textContent =
        "正在加载待办...";

    list.innerHTML = "";


    try {

        const response =
            await authFetch(
                `${API_BASE_URL}/todos`
            );


        if (!response) return;


        const todos =
            await response.json();


        loading.style.display =
            "none";


        if (!response.ok) {

            loading.style.display =
                "block";

            loading.textContent =
                "待办加载失败";

            return;
        }


        if (todos.length === 0) {

            loading.style.display =
                "block";

            loading.textContent =
                "当前没有待办事项";

            return;
        }


        todos.forEach(
            todo => {

                const card =
                    document.createElement(
                        "div"
                    );


                card.className =
                    "todo-card";


                card.innerHTML = `
                    <div>
                        <h3>
                            ${escapeHtml(todo.title)}
                        </h3>

                        <p>
                            创建时间：
                            ${formatTime(todo.created_at)}
                        </p>
                    </div>

                    <span class="status">
                        ${escapeHtml(todo.status)}
                    </span>
                `;


                list.appendChild(card);
            }
        );


    } catch (error) {

        loading.style.display =
            "block";

        loading.textContent =
            "无法加载待办";

        console.error(error);
    }
}


// =========================
// RAG知识库
// =========================

async function askKnowledge() {

    const input =
        document.getElementById(
            "knowledgeInput"
        );

    const answerBox =
        document.getElementById(
            "knowledgeAnswer"
        );

    const button =
        document.getElementById(
            "knowledgeButton"
        );


    const question =
        input.value.trim();


    if (!question) {

        answerBox.textContent =
            "请输入需要查询的问题。";

        return;
    }


    button.disabled = true;

    button.textContent =
        "查询中...";


    answerBox.textContent =
        "正在检索知识库...";


    try {

        const response =
            await authFetch(
                `${API_BASE_URL}/chat`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        message: question,

                        conversation_id:
                            getConversationId()
                    })
                }
            );


        if (!response) return;


        const data =
            await response.json();


        if (!response.ok) {

            answerBox.textContent =
                data.detail ||
                "知识库查询失败";

            return;
        }


        answerBox.textContent =
            data.message;


    } catch (error) {

        answerBox.textContent =
            "无法连接服务器";

        console.error(error);


    } finally {

        button.disabled = false;

        button.textContent =
            "查询知识库";
    }
}


// =========================
// 任务记录
// =========================

async function loadTaskLogs() {

    const loading =
        document.getElementById(
            "logsLoading"
        );

    const list =
        document.getElementById(
            "taskLogList"
        );


    if (!list) return;


    loading.style.display =
        "block";

    loading.textContent =
        "正在加载任务记录...";

    list.innerHTML = "";


    try {

        const response =
            await authFetch(
                `${API_BASE_URL}/task-logs`
            );


        if (!response) return;


        const logs =
            await response.json();


        loading.style.display =
            "none";


        if (!response.ok) {

            loading.style.display =
                "block";

            loading.textContent =
                "任务记录加载失败";

            return;
        }


        if (logs.length === 0) {

            loading.style.display =
                "block";

            loading.textContent =
                "当前没有任务记录";

            return;
        }


        logs.forEach(
            log => {

                const card =
                    document.createElement(
                        "div"
                    );


                card.className =
                    "log-card";


                card.innerHTML = `
                    <div class="log-header">

                        <div>
                            <strong>
                                ${escapeHtml(log.user_message)}
                            </strong>
                        </div>

                        <div class="log-time">
                            ${formatTime(log.created_at)}
                        </div>

                    </div>


                    <div class="log-row">

                        <span class="log-label">
                            Route：
                        </span>

                        ${escapeHtml(log.route || "-")}

                    </div>


                    <div class="log-row">

                        <span class="log-label">
                            Tool：
                        </span>

                        ${escapeHtml(log.tool_name || "-")}

                    </div>


                    <div class="log-row">

                        <span class="log-label">
                            状态：
                        </span>

                        <span class="status status-success">
                            ${escapeHtml(log.status || "-")}
                        </span>

                    </div>


                    <div class="log-row">

                        <span class="log-label">
                            Tool Result：
                        </span>

                        <div class="log-result">
                            ${escapeHtml(
                                formatToolResult(
                                    log.tool_result
                                )
                            )}
                        </div>

                    </div>


                    <div class="log-row">

                        <span class="log-label">
                            AI 最终回答：
                        </span>

                        <div class="log-result">
                            ${escapeHtml(
                                log.final_answer || "-"
                            )}
                        </div>

                    </div>
                `;


                list.appendChild(card);
            }
        );


    } catch (error) {

        loading.style.display =
            "block";

        loading.textContent =
            "无法加载任务记录";

        console.error(error);
    }
}


// =========================
// 工具结果格式化
// =========================

function formatToolResult(value) {

    if (!value) return "-";


    try {

        const parsed =
            JSON.parse(value);


        return JSON.stringify(
            parsed,
            null,
            2
        );


    } catch (error) {

        return value;
    }
}


// =========================
// 时间格式
// =========================

function formatTime(value) {

    if (!value) return "-";


    const date =
        new Date(value);


    if (
        Number.isNaN(
            date.getTime()
        )
    ) {

        return value;
    }


    return date.toLocaleString();
}


// =========================
// 防止HTML注入
// =========================

function escapeHtml(value) {

    if (
        value === null ||
        value === undefined
    ) {

        return "";
    }


    return String(value)

        .replaceAll(
            "&",
            "&amp;"
        )

        .replaceAll(
            "<",
            "&lt;"
        )

        .replaceAll(
            ">",
            "&gt;"
        )

        .replaceAll(
            '"',
            "&quot;"
        )

        .replaceAll(
            "'",
            "&#039;"
        );
}


// =========================
// 退出登录
// =========================

function logout() {

    localStorage.removeItem(
        "access_token"
    );

    localStorage.removeItem(
        "conversation_id"
    );


    window.location.href =
        "login.html";
}


// =========================
// Enter发送
// =========================

const messageInput =
    document.getElementById(
        "messageInput"
    );


if (messageInput) {

    messageInput.addEventListener(
        "keydown",
        function (event) {

            if (
                event.key === "Enter" &&
                !event.shiftKey
            ) {

                event.preventDefault();

                sendMessage();
            }

        }
    );
}