"""Loads PDF files and concverts them into Documents using langchain for chunker"""

from typing import List, Dict, Optional, Any
from pathlib import Path
import hashlib
from datetime import datetime
from dataclasses import dataclass , field

from docling.document_converter import DocumentConverter ,PdfFormatOption
from docling.pipeline.base_pipeline import PdfPipelineOptions
from docling.datamodel.base_models import InputFormat
from docling.datamodel.document import ConversionResult

@dataclass
class ParsedDocument: #Figure out how to store the documnet 
    """Structured representation of parsed document"""
    doc_id: int
    source: str
    images: List[Dict]
    tables: List[Dict]
    parsed_content: str =""


class DocumentLoader:
    """
    Smart document loader with configurable pipeline options
    Supports PDFs with picture descriptions and table extraction
    """
    def __init__(self):
        """Initialize the Document Loader with cutom pipeline configurations"""
        self.converter=DocumentConverter()
    
    def generate_doc_id():
        """Generate unique doc_id for each file"""
        pass
    
    def extract_images():
        """Extract image information from the conversion result"""
        pass
    
    def extract_tables():
        """Extract table information from the conversion result"""
        pass
    
    def convert_document(self,file_path) -> ParsedDocument:
        """Convert files to ParsedDocument"""
        path=Path(file_path)
        result=self.converter.convert(path)
        content=result.document.export_to_markdown()
        
        return ParsedDocument(
            doc_id="",
            source="dummy",
            images=[],
            tables=[],
            parsed_content=content
        )
    

if __name__ == "__main__":
    loader=DocumentLoader()
    print("Starting Example Run")
    res=loader.convert_document("/home/itzfranku/Aristo/2501.17887v1.pdf")
    print(res)