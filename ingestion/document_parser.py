
import json
from pathlib import Path

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption


def build_tree(doc):

    root = {
        "type": "document",
        "title": None,
        "children": [],
        "level": -1
    }

    stack = [root]

    for item, level in doc.iterate_items():

        text = getattr(item, "text", None) or getattr(item, "orig", None)

        node = {
            "id": item.self_ref,
            "type": item.label.value,
            "text": text,
            "page": item.prov[0].page_no if item.prov else None,
            "children": [],
            "level": level
        }

        while stack and stack[-1]["level"] >= level:
            stack.pop()

        stack[-1]["children"].append(node)
        stack.append(node)

    return root


def parse_document(pdf_path: str):

    pipeline_options = PdfPipelineOptions()

    doc_converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )

    conv_res = doc_converter.convert(pdf_path)

    doc = conv_res.document

    tree = build_tree(doc)

    return tree