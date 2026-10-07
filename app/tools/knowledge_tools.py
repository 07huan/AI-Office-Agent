from app.rag.vector_store import search_knowledge


def query_knowledge_base(question: str):
    results = search_knowledge(question)

    knowledge = []

    for document in results:
        knowledge.append(document.page_content)

    return knowledge