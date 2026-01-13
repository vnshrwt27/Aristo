import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from core.document_chunker import DocumentChunker
from core.qdrant_uploader import QdrantUploader
from core.vdb_client import client
import uuid
import asyncio
async def main():
    with open("output.md","r") as f:
        text=f.read()
    chunker=DocumentChunker()
    uploader=await QdrantUploader.create(client=client, collection_name="New",vector_size=768)



    res=chunker.chunk_document(content=text,source="output.md",doc_id="test-id-1")
    pnts=await uploader.upload_chunks(res)
    #print(pnts)
    #print(f"Result:{res}")
    print(f"Chunk Len:{len(res)}")
    print(res[0])
asyncio.run(main())