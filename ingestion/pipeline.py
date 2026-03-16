from .document_parser import parse_document
from .chunker import collect_sections, chunk_sections
from .embedding import embed_chunks
from .indexer import index_chunks


def ingest(pdf_path):

    print("Parsing document...")
    tree = parse_document(pdf_path)

    print("Collecting sections...")
    sections = collect_sections(tree)

    document_title = tree.get("title")

    print("Chunking...")
    chunks = chunk_sections(sections, document_title)

    print("Embedding...")
    chunks = embed_chunks(chunks)

    print("Indexing...")
    index_chunks(chunks)

    print("Ingestion complete.")