from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


def load_and_split_documents():
    loader = TextLoader(
        "knowledge/company_rules.txt",
        encoding="utf-8"
    )

    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=100,
        chunk_overlap=20
    )

    chunks = text_splitter.split_documents(documents)

    return chunks