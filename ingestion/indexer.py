import os
from pinecone import Pinecone
from dotenv import load_dotenv

from .config import VECTOR_INDEX_NAME

load_dotenv()

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index(VECTOR_INDEX_NAME)


def index_chunks(chunks):
    vectors = []
    for chunk in chunks:
        meta = dict(chunk["metadata"])
        meta["content"] = chunk["text"]
        vectors.append({
            "id": chunk["id"],
            "values": chunk["embedding"],
            "metadata": meta,
        })
    index.upsert(vectors=vectors)
