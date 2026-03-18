
from langchain.tools import tool
from retrieval.vector_retriever import VectorRetriever
from retrieval.web_retriever import WebRetriever


vector_retriever = VectorRetriever(vectorstore)
web_retriever = WebRetriever(TAVILY_API_KEY)


@tool
def search_internal_docs(query: str) -> str:
    """
    Search internal documents stored in the knowledge base.
    """

    results = vector_retriever.search(query)

    return "\n\n".join([r["content"] for r in results])


@tool
def search_web(query: str) -> str:
    """
    Search the internet for recent information.
    """

    results = web_retriever.search(query)

    return "\n\n".join([r["content"] for r in results])


retrieval_tools = [
    search_internal_docs,
    search_web
]