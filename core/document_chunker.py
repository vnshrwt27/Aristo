"""
Converts documents into chunks and uploads them to Qdrant database 
TODO: Add Postgres database as well later on 
"""

from typing import List, Dict, Optional, Any
from pathlib import Path
from dataclasses import dataclass, asdict

from document_loader import DocumentLoader
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
    
    def chunk_document(self,
                       content: str,
                       source: str,
                       doc_id: Optional[str]
                       ) -> List[DocumentChunk]:
        """
        Chunk a documnet into smaller chunks
        """
        pass

with open("output.md","r") as f:
    output=f.read()
headers_to_split_on = [
    ("#", "Header 1"),
    ("##", "Header 2"),
    ("###", "Header 3"),
]

splitter=MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)

documents=splitter.split_text(output)
for i in range(0,5):
    print(documents[i],"\n")