from pinecone import Pinecone
from .config import VECTOR_INDEX_NAME
import os 
from dotenv import load_dotenv

load_dotenv()
PINECONE_API_KEY= os.getenv("PINECONE_API_KEY")

pc = Pinecone(api_key=PINECONE_API_KEY)

index = pc.Index(VECTOR_INDEX_NAME)


def index_chunks(chunks):

    vectors = []

    for chunk in chunks:

        vectors.append({
            "id": chunk["id"],
            "values": chunk["embedding"],
            "metadata": chunk["metadata"]
        })

    index.upsert(vectors=vectors)