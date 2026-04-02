from state.research_state import ResearchState
from services.llm import LLMService


SYSTEM_PROMPT = """You are a research planner. Given a research query, break it down into 3-5 focused sub-queries that together will comprehensively cover the topic.

Rules:
- Each sub-query should explore a distinct angle
- Make queries specific and targeted, not broad
- Cover: definition/overview, key details, practical aspects, edge cases
- Return ONLY a JSON object: {"sub_queries": ["query1", "query2", ...]}"""


def decompose(state: ResearchState) -> ResearchState:
    query = state.get("query", "")

    llm = LLMService()

    try:
        result = llm.invoke_json(
            SYSTEM_PROMPT,
            f"Break down this research query into focused sub-queries: {query}",
        )
        sub_queries = result.get("sub_queries", [])
    except Exception:
        sub_queries = [
            f"{query} overview",
            f"{query} key findings",
            f"{query} recent developments",
        ]

    if not sub_queries:
        sub_queries = [f"{query} overview"]

    return {
        "sub_queries": sub_queries[:5],
        "iterations": 1,
        "done": False,
        "batch_size": 3,
    }
