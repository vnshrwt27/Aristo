"""Handles uploading chunks to vector database"""

from typing import List, Optional
import uuid
import asyncio
from datetime import datetime

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    CollectionStatus
)
from document_chunker import DocumentChunker,DocumentChunk
from embedding import model


class QdrantUploader:
    """Handles uploading chunks to qdrant database"""

    def __init__(self,
                 client: AsyncQdrantClient,
                 collection_name: str,
                 ):
        self.client=client
        self.collection_name=collection_name
    
    @classmethod
    async def create(cls, client: AsyncQdrantClient, collection_name: str, vector_size: int):
        """Async factory method to create uploader with collection setup"""
        uploader = cls(client, collection_name)
        await uploader.create_collection_if_not_exist()
        return uploader
    
    async def create_collection_if_not_exist(self):
        """Creates collection if it does not exist"""
        collections=await self.client.get_collections()
        if self.collection_name not in collections.collections:
            try:
                print(f"Creating collection:{self.collection_name}")
                await self.client.create_collection(self.collection_name,
                                                    vectors_config=VectorParams(size=768,
                                                                                distance=Distance.COSINE))
            except Exception as e:
                print(f"Error creating collection: {e}")

    async def upload_chunks(self,
                            chunks: List[DocumentChunk],
                            ):
        points=[]
        for chunk_idx,chunk in enumerate(chunks):
            embedded_chunk=model.encode(chunk.content)
            points.append(
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=embedded_chunk,
                    payload= {"Chunk Index":chunk_idx,
                              "metadata":chunk.metadata,
                              })
            )
        res= await self.client.upsert(collection_name= self.collection_name,
                                      points=points)
        return res

