# Aristo – Autonomous Research Agent

An AI-powered research system built with **LangGraph** that performs iterative multi-round research across internal vector databases (Pinecone) and web search (Tavily).

## How It Works

Instead of single-step retrieval like traditional RAG, Aristo runs a **research loop**:

```
Query → Retrieve → Aggregate → (Generate New Queries → Retrieve)× → Synthesize Answer


## Architecture

```
cli.py ──► graph/research_graph.py ──► nodes/ ──► retrieval/
                                          │
                                ingestion/ (separate pipeline)
```

### Graph Nodes

| Node | Purpose |
|------|---------|
| `decompose` | Break query into sub-queries |
| `retrieve` | Fetch docs from Pinecone + Tavily |
| `aggregate` | Collect and deduplicate findings |
| `generate_queries` | Create new queries from knowledge gaps |
| `synthesize` | Produce final answer |

### State

Research state (`state/research_state.py`) tracks queries, documents, facts, summaries, and iteration count with automatic deduplication via `Annotated` reducers.

### Ingestion Pipeline

Linear pipeline: **PDF → Parse (Docling) → Chunk → Embed → Index (Pinecone)**

## Tech Stack

- **Orchestration**: LangGraph (state machine with checkpointing)
- **Vector DB**: Pinecone
- **Web Search**: Tavily
- **LLM**: Groq
- **PDF Parsing**: Docling
- **Embeddings**: sentence-transformers
