from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance

import os
from dotenv import load_dotenv

load_dotenv()

qdrant_client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
)
if not qdrant_client.collection_exists("Test"):
    qdrant_client.create_collection(
        collection_name="Test",
        vectors_config=VectorParams(size=100, distance=Distance.COSINE),
    )

print(qdrant_client.get_collections())
