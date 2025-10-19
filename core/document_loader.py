"""Loads PDF files and converts them into Documents using langchain for chunker"""

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
    def __init__(self,
                 format_options: Optional[Dict]= None,
                 do_picture_description: bool= True,
                 do_table_structure: bool= True,
                 do_ocr: bool= True,
                 generate_picture_images= True):
        """Initialize the Document Loader with cutom pipeline configurations"""
        if format_options is None:
            format_options={InputFormat.PDF: PdfFormatOption(
                pipeline_options=PdfPipelineOptions(
                    do_picture_description=do_picture_description,
                    do_table_structure=do_table_structure,
                    do_ocr=do_ocr,
                    generate_picture_images=generate_picture_images,
                    do_formula_enrichment=True)
            )}
        self.format_options=format_options
        self.converter=DocumentConverter(format_options=format_options)
    
    def generate_doc_id(self,filepath: str) -> str:
        """Generate unique doc_id for each file"""
        unique_string = f"{filepath}_{datetime.now().isoformat()}"
        return hashlib.md5(unique_string.encode()).hexdigest()[:16]
    
    def extract_images(self, result: ConversionResult)-> List[Dict[str,Any]]:
        """Extract image information from the conversion result"""
        images=[]
        try:
            doc=result.document
            for item in doc.pictures:
                images.append(item)

        except Exception as e:
            print(f"Error extracting images from file:{e}")
    
        return images
    
    def extract_tables(self, result:ConversionResult) ->List[Dict[str,Any]]:
        """Extract table information from the conversion result"""
        tables=[]
        try:
            doc=result.document
            for table in doc.tables:
                tables.append(table)
        except Exception as e:
            print(f"Error trying to extract tables:{e}")
        return tables

    
    def convert_document(self,file_path) -> ParsedDocument:
        """Convert files to ParsedDocument"""
        path=Path(file_path)
        result=self.converter.convert(path)
        content=result.document.export_to_markdown()
        
        return ParsedDocument(
            doc_id=self.generate_doc_id(filepath=file_path),
            source=file_path,
            images=self.extract_images(result),
            tables=self.extract_tables(result),
            parsed_content=content
        )
    

if __name__ == "__main__":
    loader=DocumentLoader()
    print("Starting Example Run")
    res=loader.convert_document("/home/itzfranku/Aristo/2501.17887v1.pdf")
    print(res)