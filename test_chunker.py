from core.document_chunker import DocumentChunker
from core.qdrant_uploader import QdrantUploader
from core.vdb_client import client
import uuid
import asyncio
async def main():
    with open("output.md","r") as f:
        text=f.read()
    chunker=DocumentChunker()
    uploader=await QdrantUploader.create(client=client, collection_name="New")



    res=chunker.chunk_document(content=text,source="output.md",doc_id="test-id-1")
    pnts=await uploader.upload_chunks(res)
    #print(pnts)
    #print(f"Result:{res}")
    print(f"Chunk Len:{len(res)}")
    print(f"Chunk content:{res[0].content}")
    print(res[0])
asyncio.run(main())