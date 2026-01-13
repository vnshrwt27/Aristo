"""Enbedding Model for converting data into Vector embeddings"""
from sentence_transformers import SentenceTransformer

model=SentenceTransformer("all-mpnet-base-v2") # Vector Size: 768

sentences = [
    "The weather is lovely today.",
    "It's so sunny outside!",
    "He drove to the stadium.",
]
embeddings = model.encode(sentences)
#print(embeddings.shape)
#print(model)