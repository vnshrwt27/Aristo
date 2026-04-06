import logging
from pathlib import Path

from .document_parser import parse_document
from .chunker import collect_sections, chunk_sections
from .embedding import embed_chunks
from .indexer import index_chunks

logger = logging.getLogger(__name__)


def ingest(pdf_path):
    pdf_path = str(pdf_path)

    if not Path(pdf_path).exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    if not pdf_path.lower().endswith(".pdf"):
        raise ValueError(f"Expected PDF file, got: {pdf_path}")

    try:
        print("Parsing document...")
        tree = parse_document(pdf_path)

        print("Collecting sections...")
        sections = collect_sections(tree)
        if not sections:
            logger.warning("No sections found in document tree")

        document_title = tree.get("title")
        print(f"Document: {document_title}")
        print(f"Sections found: {len(sections)}")

        print("Chunking...")
        chunks = chunk_sections(sections, document_title)
        print(f"Chunks created: {len(chunks)}")

        if not chunks:
            raise ValueError("No chunks generated from document")

        print("Embedding...")
        chunks = embed_chunks(chunks)

        print("Indexing...")
        index_chunks(chunks)

        print(f"Ingestion complete: {len(chunks)} chunks indexed")
        return {
            "document_title": document_title,
            "sections": len(sections),
            "chunks": len(chunks),
        }

    except Exception as e:
        logger.error(f"Ingestion failed for {pdf_path}: {e}")
        raise
