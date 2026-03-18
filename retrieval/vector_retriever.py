
from typing import List, Dict
from langchain_community.vectorstores import Pinecone
from langchain_community.embeddings import HuggingFaceEmbeddings
import os 

from dotenv import load_dotenv

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")


class VectorRetriever:
    def __init__(self, index, top_k: int = 5):
        self.index = index
        self.top_k = top_k

        self.embeddings = HuggingFaceEmbeddings(
            model_name="llama-text-embed-v2"
        )

        self.vectorstore = Pinecone(
            api_key= PINECONE_API_KEY,
            index=self.index,
            embedding=self.embeddings
        )

    def retrieve(self, query: str) -> List[Dict]:
        """
        Retrieve relevant chunks from the vector database.
        """

        docs = self.vectorstore.similarity_search(
            query,
            k=self.top_k
        )

        results = []

        for d in docs:
            results.append(
                {
                    "content": d.page_content,
                    "metadata": d.metadata
                }
            )

        return results