import os
from dotenv import load_dotenv
import asyncio

load_dotenv()

from qdrant_client import AsyncQdrantClient

client=AsyncQdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
    prefer_grpc=False
)
