from .utils import generate_chunk_id


def collect_sections(doc_tree):

    sections = []
    current_section = None

    for node in doc_tree.get("children", []):

        node_type = node.get("type")
        text = node.get("text")

        if node_type == "section_header":
            current_section = {
                "title": text,
                "content": [],
                "nodes": []
            }
            sections.append(current_section)
            continue

        if current_section is None:
            continue

        if node_type in {"text", "list_item", "caption"} and text:
            current_section["content"].append(text)
            current_section["nodes"].append(node)

    return sections


def chunk_sections(sections, document_title, chunk_size=150):

    chunks = []

    for section in sections:

        words = " ".join(section["content"]).split()

        for i in range(0, len(words), chunk_size):

            text = " ".join(words[i:i + chunk_size])

            chunks.append({
                "id": generate_chunk_id(),
                "text": text,
                "metadata": {
                    "document_title": document_title,
                    "section": section["title"],
                    "node_ids": [n["id"] for n in section["nodes"]]
                }
            })

    return chunks