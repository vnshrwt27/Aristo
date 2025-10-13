"""Loads PDF files and concverts them into Documents using langchain for chunker"""

from typing import List, Dict, Optional, Any
from pathlib import Path
from dataclasses import dataclass

@dataclass
class ParsedDocument:   #Figure out how to store the documnet 
    doc_id: int
    source: str
    tables: List[Dict]
    parsed_content: str # Have to figure out what to insert into the loader

from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.pipeline.vlm_pipeline import VlmPipeline
from docling.datamodel.pipeline_options import VlmPipelineOptions, AcceleratorOptions
from docling.datamodel import vlm_model_specs
import torch
import time

file_path = "/home/itzfranku/Aristo/2309.02427v3.pdf"

print("=== Simple Fast Mode ===\n")


print("Loading model...")
start = time.time()

# Use pre-configured SmolDocling - simplest approach
pipeline_options = VlmPipelineOptions(
    vlm_options=vlm_model_specs.SMOLDOCLING_TRANSFORMERS,
    accelerator_options=AcceleratorOptions(device='cuda'),
    do_picture_description=True,
    do_picture_classification=False,
    allow_external_plugins=False,
)

loader = DocumentConverter()

load_time = time.time() - start
print(f"✓ Model loaded: {load_time:.2f}s")
print(f"  GPU Memory: {torch.cuda.memory_allocated(0) / 1024**3:.2f} GB\n")

print("Processing PDF...")
start = time.time()
docs = loader.convert(file_path)
process_time = time.time() - start

print(f"✓ Processed: {process_time:.2f}s")
print(f"✓ Total time: {load_time + process_time:.2f}s\n")

# Export results
markdown = docs.document.export_to_markdown()
print("First 500 characters:")
print(markdown[:500])

# Save to file
with open("output.md", "w") as f:
    f.write(markdown)
print("\n✓ Saved to output.md")