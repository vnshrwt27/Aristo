"""
Converts documents into chunks and uploads them to Qdrant database 
TODO: Add Postgres database as well later on 
"""

from typing import List, Dict, Optional, Any
from pathlib import Path
from dataclasses import dataclass, asdict
import uuid

from langchain.text_splitter import MarkdownHeaderTextSplitter,MarkdownTextSplitter

#from core.vdb_client import client
import asyncio

@dataclass
class ChunkMetadata:
    """Metadata for each chunks"""
    doc_id: str
    chunk_id: str
    source: str
    chunk_index: int
    total_chunks: int
    headers: Dict[str,str] = None
    created_at: float= None
    def to_dict(self):
        """Convert to dictionary for serialization"""
        return {k: v for k, v in asdict(self).items() if v is not None}

@dataclass
class DocumentChunk:
    """A chunk of document with content and metadata"""
    content: str
    metadata: ChunkMetadata
    embedding: List[float]= None

class DocumentChunker:
    """Handles document chunking"""
    def __init__(
            self,
            chunk_size: int =1000,
            chunk_overlap: int =200,
            chunking_strategy: str= 'markdown_headers'):
        """
        Initialize the Chunker with chunk configurations 
        """
        self.chunk_size=chunk_size
        self.chunk_overlap=chunk_overlap
        self.chunking_strategy=chunking_strategy
    def generate_chunk_id(self):
        """Generate Unique chunk ids"""
        return str(uuid.uuid4())
    def chunk_document(self,
                       content: str,
                       source: str,
                       doc_id: Optional[str],
                       ) -> List[DocumentChunk]:
        """
        Chunk a document into smaller chunks
        """
        headers_to_split_on = [
            ("##", "Header"),
                ]

        splitter=MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
        chunks=splitter.split_text(content)
        docs=[]
        for chunk_idx, chunk_content in enumerate(chunks):
            metadata=ChunkMetadata(
                doc_id=doc_id,
                chunk_id=self.generate_chunk_id(), 
                source=source,
                total_chunks=len(chunks),
                chunk_index=chunk_idx,
            )
            docs.append(DocumentChunk(
                                        content=chunk_content.page_content,
                                        metadata=metadata,
                                      ))
        return docs

if __name__=="__main__":
    chunker=DocumentChunker()
    print(chunker)