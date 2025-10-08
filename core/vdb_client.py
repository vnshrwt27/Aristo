import os
from dotenv import load_dotenv
import asyncio

load_dotenv()

from db.qdrant_vectorstore import AsyncQdrantManager

client=AsyncQdrantManager(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
    prefer_grpc=False
)
async def main():
    collections = await client.get_all_collections()  # Use async await
    for col in collections.collections:
        print(col.name)
        

asyncio.run(main())