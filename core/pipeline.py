import asyncio 
from pathlib import Path
from typing import List,Optional

from document_loader import DocumentLoader,ParsedDocument
from document_chunker import DocumentChunker,DocumentChunk
from qdrant_uploader import QdrantUploader
from vdb_client import client

class DataPipeline:
    """Pipeline that loads the data ,breaks it into chunks and uploads it to Qdrant Database"""

    def __init__(self,
                 collection_name:str ="document",
                 chunk_size: int=1000,
                 chunk_overlap: int =200 ):
        self.collection_name=collection_name
        self.loader=DocumentLoader()
        self.chunker=DocumentChunker()
        self.uploader= None
    
    async def initialize(self):
        """Initialize async components"""
        print(f"Initializing pipeline with collection :{self.collection_name}")
        self.uploader=await QdrantUploader.create(client,self.collection_name,768)
        print("Pipeline Succesfully Initialized")
    
    async def process_file(self,file_path):
        parsed_doc=self.loader.convert_document(file_path)
        doc_chunks=self.chunker.chunk_document(parsed_doc.parsed_content,
                                               source=parsed_doc.source,
                                               doc_id=parsed_doc.doc_id)
        await self.uploader.upload_chunks(doc_chunks)

if __name__=="__main__":
    async def main():
        pipeline=DataPipeline()
        file_path="/home/itzfranku/Aristo/2501.17887v1.pdf"
        print("Starting Pipeline")
        await pipeline.initialize()
        await pipeline.process_file(file_path=file_path)
        print("Pipeline Finished")
    asyncio.run(main())