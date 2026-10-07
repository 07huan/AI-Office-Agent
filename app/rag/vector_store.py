import os

from dotenv import load_dotenv
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_chroma import Chroma

from app.rag.document_loader import load_and_split_documents


load_dotenv()

DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")

PERSIST_DIRECTORY = "./chroma_db"
COLLECTION_NAME = "company_knowledge"


# =========================
# 创建 Embedding 模型
# =========================

def get_embeddings():

    return DashScopeEmbeddings(
        model="text-embedding-v4",
        dashscope_api_key=DASHSCOPE_API_KEY
    )


# =========================
# 创建向量库
# 只有第一次需要执行
# =========================

def create_vector_store():

    chunks = load_and_split_documents()

    embeddings = get_embeddings()

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=PERSIST_DIRECTORY
    )

    print("知识库向量化完成")

    return vector_store


# =========================
# 加载已有向量库
# =========================

def load_vector_store():

    embeddings = get_embeddings()

    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=PERSIST_DIRECTORY
    )

    return vector_store


# =========================
# 获取向量库
# =========================

def get_vector_store():

    if not os.path.exists(PERSIST_DIRECTORY):

        print("未发现向量库，正在创建...")

        return create_vector_store()

    print("正在加载已有向量库...")

    return load_vector_store()


# =========================
# RAG 相似度搜索
# =========================

def search_knowledge(query: str):

    vector_store = get_vector_store()

    results = vector_store.similarity_search(
        query,
        k=2
    )

    return results