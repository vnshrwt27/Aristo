from state.research_state import ResearchState


def aggregate(state: ResearchState) -> ResearchState:
    queries_in_batch = state.get("queries_in_batch", [])
    documents = state.get("documents", [])

    if not documents:
        query_label = ", ".join(queries_in_batch) if queries_in_batch else "unknown"
        return {
            "extracted_facts": [f"[{query_label}] No documents retrieved"],
            "sources": [],
            "summaries": [f"No results for: {query_label}"],
        }

    facts = []
    sources = []

    for doc in documents:
        content = doc.get("content", "")
        source = doc.get("source", "unknown")
        url = doc.get("url", "")

        facts.append(f"[{source}] {content[:200]}...")

        if url:
            sources.append(url)
        elif source == "internal":
            sources.append(f"Internal KB: {doc.get('query', '')}")
        else:
            sources.append(f"Web: {doc.get('query', '')}")

    query_label = ", ".join(queries_in_batch) if queries_in_batch else "unknown"

    return {
        "extracted_facts": facts,
        "sources": sources,
        "summaries": [f"Processed {len(documents)} document(s) for: {query_label}"],
    }
