import os
from typing import Dict, List
from dotenv import load_dotenv
from langchain_pinecone import PineconeVectorStore
from langchain_community.embeddings import HuggingFaceEmbeddings
from flashrank import Ranker, RerankRequest

load_dotenv()

PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "aristo-docs")

_rerank_cache: Dict[str, "Ranker"] = {}


def _get_ranker(model_name: str = "ms-marco-MiniLM-L-12-v2"):
    if model_name not in _rerank_cache:
        _rerank_cache[model_name] = Ranker(model_name=model_name, cache_dir="/tmp/flashrank")
    return _rerank_cache[model_name]


class VectorRetriever:
    def __init__(
        self,
        index_name: str = PINECONE_INDEX_NAME,
        top_k: int = 5,
        fetch_k: int = 20,
        use_rerank: bool = True,
    ):
        self.top_k = top_k
        self.fetch_k = fetch_k
        self.use_rerank = use_rerank
        self.index_name = index_name
        self._vectorstore = None
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    @property
    def vectorstore(self):
        if self._vectorstore is None:
            try:
                self._vectorstore = PineconeVectorStore(
                    index_name=self.index_name,
                    embedding=self.embeddings,
                    text_key="content",
                )
            except Exception:
                self._vectorstore = None
        return self._vectorstore

    def search(self, query: str, filter: dict | None = None) -> List[Dict]:
        if self.vectorstore is None:
            return []

        docs = self.vectorstore.similarity_search(query, k=self.fetch_k, filter=filter)

        if not docs:
            return []

        if self.use_rerank and len(docs) > 1:
            docs = self._rerank(query, docs)

        return [
            {
                "content": d.page_content,
                "metadata": d.metadata,
                "score": d.metadata.get("relevance_score"),
            }
            for d in docs[: self.top_k]
        ]

    def _rerank(self, query: str, docs) -> list:
        passages = [
            {"id": str(i), "text": d.page_content, "meta": d.metadata}
            for i, d in enumerate(docs)
        ]

        rerank_req = RerankRequest(query=query, passages=passages)
        ranker = _get_ranker()
        results = ranker.rerank(rerank_req)

        reranked = []
        for r in results:
            original = docs[int(r["id"])]
            original.metadata["relevance_score"] = r["score"]
            reranked.append(original)

        return reranked
