from state.research_state import ResearchState
from services.llm import LLMService


SYSTEM_PROMPT = """You are a research analyst identifying knowledge gaps. Given the original research query and the findings collected so far, determine what important aspects are still missing.

Rules:
- Compare the findings against what would be needed to fully answer the query
- Identify 2-3 specific gaps in the current knowledge
- If findings seem comprehensive, return an empty gaps array
- Return ONLY a JSON object: {"gaps": ["gap1", "gap2"]}"""


def generate_queries(state: ResearchState) -> ResearchState:
    query = state.get("query", "")
    facts = state.get("extracted_facts", [])
    iterations = state.get("iterations", 0)

    llm = LLMService()

    findings_context = "\n".join(f"- {f}" for f in facts[:20])

    try:
        result = llm.invoke_json(
            SYSTEM_PROMPT,
            f"Original query: {query}\n\nCurrent findings ({len(facts)} total):\n{findings_context}\n\nWhat important aspects are still missing?",
        )
        gaps = result.get("gaps", [])
    except Exception:
        gaps = []

    if not gaps:
        return {
            "sub_queries": [],
            "iterations": iterations + 1,
            "gaps": [],
            "done": True,
        }

    new_queries = [f"{query} {gap}" for gap in gaps[:3]]

    return {
        "sub_queries": new_queries,
        "iterations": iterations + 1,
        "gaps": gaps,
        "batch_size": state.get("batch_size", 3),
    }
