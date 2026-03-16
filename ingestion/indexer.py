from pinecone import Pinecone
from .config import VECTOR_INDEX_NAME


pc = Pinecone()

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