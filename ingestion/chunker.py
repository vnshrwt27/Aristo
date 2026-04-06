from .utils import generate_chunk_id
from .config import CHUNK_OVERLAP


def _walk_tree(node, sections, heading_stack=None):
    if heading_stack is None:
        heading_stack = []

    node_type = node.get("type")
    text = node.get("text")

    if node_type == "section_header" and text:
        heading_stack = heading_stack + [text]

    if node_type in {"text", "list_item", "caption"} and text:
        section_key = " / ".join(heading_stack) if heading_stack else "Untitled"
        if not sections or sections[-1]["heading_path"] != section_key:
            sections.append({
                "heading_path": section_key,
                "top_heading": heading_stack[-1] if heading_stack else None,
                "content": [],
                "nodes": [],
            })
        sections[-1]["content"].append(text)
        sections[-1]["nodes"].append(node)

    for child in node.get("children", []):
        _walk_tree(child, sections, heading_stack)


def collect_sections(doc_tree):
    sections = []
    _walk_tree(doc_tree, sections)
    return sections


def chunk_sections(sections, document_title, chunk_size=150, chunk_overlap=None):
    if chunk_overlap is None:
        chunk_overlap = CHUNK_OVERLAP

    stride = max(chunk_size - chunk_overlap, 1)
    chunks = []

    for section in sections:
        words = " ".join(section["content"]).split()
        total = len(words)

        if total == 0:
            continue

        chunk_idx = 0
        for i in range(0, total, stride):
            window = words[i:i + chunk_size]
            text = " ".join(window)

            if len(text.strip()) < 10:
                continue

            node_ids = []
            pages = set()
            word_pos = 0
            for node in section["nodes"]:
                node_words = node.get("text", "").split()
                node_end = len(node_words)
                if i < node_end + word_pos and i + chunk_size > word_pos:
                    node_ids.append(node["id"])
                    page = node.get("page")
                    if page is not None:
                        pages.add(page)
                word_pos += node_end

            meta = {
                "document_title": str(document_title or ""),
                "section": section["heading_path"],
                "chunk_index": chunk_idx,
                "total_chunks": (total + stride - 1) // stride,
            }
            if section["top_heading"]:
                meta["top_heading"] = section["top_heading"]
            if pages:
                meta["pages"] = [str(p) for p in sorted(pages)]
            if node_ids:
                meta["node_ids"] = node_ids[:10]

            chunks.append({
                "id": generate_chunk_id(),
                "text": text,
                "metadata": meta,
            })
            chunk_idx += 1

    return chunks
