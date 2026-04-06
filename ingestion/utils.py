import uuid


def generate_chunk_id():
    return str(uuid.uuid4())


def flatten_text(content):
    return " ".join(content).strip()
