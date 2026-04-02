from state.research_state import ResearchState


def retrieve(state: ResearchState) -> ResearchState:
    sub_queries = state.get("sub_queries", [])
    batch_size = state.get("batch_size", 3)

    if not sub_queries:
        return {"current_query": "", "done": True}

    batch = sub_queries[:batch_size]
    remaining = sub_queries[batch_size:]

    from retrieval.retrieval_tools import search_internal_docs, search_web

    all_documents = []
    errors = []

    for query in batch:
        try:
            internal_results = search_internal_docs.invoke(query)
            web_results = search_web.invoke(query)

            for content in internal_results.split("\n\n"):
                if content.strip():
                    all_documents.append({
                        "content": content.strip(),
                        "source": "internal",
                        "query": query,
                    })

            for content in web_results.split("\n\n"):
                if content.strip():
                    all_documents.append({
                        "content": content.strip(),
                        "source": "web",
                        "query": query,
                    })
        except Exception as e:
            errors.append({"query": query, "error": str(e)})

    return {
        "current_query": batch[-1] if batch else "",
        "queries_in_batch": batch,
        "sub_queries": remaining,
        "documents": all_documents,
        "errors": errors,
    }
