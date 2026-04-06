from sentence_transformers import SentenceTransformer
from .config import EMBEDDING_MODEL

model = SentenceTransformer(EMBEDDING_MODEL)


def embed_chunks(chunks):
    texts = [c["text"] for c in chunks]
    embeddings = model.encode(texts)

    for chunk, emb in zip(chunks, embeddings):
        chunk["embedding"] = emb.tolist()

    return chunks
