import json

from docling.datamodel import document 
with open("doc_tree.json") as f:
    tree =json.load(f)

#print(tree)
#print(tree["type"])

def collect_sections(doc_tree):
    sections = []
    current_section = None

    for node in doc_tree.get("children", []):

        node_type = node.get("type")
        text = node.get("text", " ")

        # Start a new section
        if node_type == "section_header":
            current_section = {
                "title": text,
                "content": [],
                "nodes": []
            }
            sections.append(current_section)
            continue

        # Skip anything before the first header
        if current_section is None:
            continue

        # Collect textual content
        if node_type in {"text", "list_item", "caption"} and text:
            current_section["content"].append(text)
            current_section["nodes"].append(node)

    return sections

def chunk_section(sections, document_title ,max_words = 50):
    chunks = []
    
    for section in sections:
        words = " ".join(section["content"]).split()

        for i in range(0, len(words), max_words):
            chunk_words = " ".join(words[i:i+max_words])

            chunks.append({"text" : chunk_words,
                           "metadata" : {
                               "document_title" : document_title,
                               "section" : section["title"],
                               "node_ids" : [n["id"] for n in section["nodes"]]
                           }
                          })
    return chunks


    

def collect_text_nodes(node, results):   #REDUNDANT

    if node["type"] in ["text", "list_item"]:
        results.append(node)

    for child in node["children"]:
        collect_text_nodes(child, results)

nodes = []

sections = collect_sections(tree)
document_title = sections[0]["title"]
chunks = chunk_section(sections,document_title)
print(chunks[0])

#for section in sections:
    #print(section)
    #print("\n"*3)

with open("doc_struct.json" , "w" ,encoding="utf-8") as f:
    json.dump(sections , f , indent= 4)

