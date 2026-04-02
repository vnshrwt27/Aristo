from state.research_state import ResearchState
from services.llm import LLMService

EVAL_PROMPT = """You are a research quality evaluator. Given the original query and findings so far, decide if more research is needed.

Return ONLY a JSON object with:
- "done": boolean - true if findings are sufficient to answer the query
- "reason": string - brief explanation of your decision

Rules:
- Be generous about what's sufficient - 10+ relevant findings is usually enough
- If findings directly address the query, mark done=true
- If findings are tangential or missing key aspects, mark done=false"""

SYNTH_PROMPT = """You are a research analyst. Write a comprehensive, well-structured report based on the provided research findings.

Rules:
- Answer the user's query directly and thoroughly
- Organize with clear markdown headings and subheadings
- Write in proper prose, not just bullet points
- Cite sources inline using [1], [2], etc. referencing the numbered source list
- If findings conflict, note the discrepancy
- If information is missing, state what could not be determined
- Do not fabricate information not present in the findings
- End with a "Sources" section listing all provided sources numbered"""


def check_gaps(state: ResearchState) -> str:
    done = state.get("done", False)
    iterations = state.get("iterations", 0)
    max_iterations = state.get("max_iterations", 3)
    sub_queries = state.get("sub_queries", [])
    facts = state.get("extracted_facts", [])
    query = state.get("query", "")

    if done or iterations >= max_iterations:
        return "synthesize"

    if sub_queries:
        return "retrieve"

    if not facts:
        return "synthesize"

    llm = LLMService()
    findings_preview = "\n".join(f"- {f}" for f in facts[:15])

    try:
        result = llm.invoke_json(
            EVAL_PROMPT,
            f"Query: {query}\n\nFindings collected ({len(facts)} total):\n{findings_preview}\n\nIs this sufficient to produce a good answer?",
        )
        if result.get("done", False):
            return "synthesize"
    except Exception:
        pass

    return "generate_queries"


def synthesize(state: ResearchState) -> ResearchState:
    context = _build_context(state)
    query = state.get("query", "")
    iterations = state.get("iterations", 0)

    if not context.strip():
        return {
            "final_answer": f"No findings were gathered during research on: {query}",
            "done": True,
        }

    llm = LLMService()
    response = llm.invoke(
        SYNTH_PROMPT,
        f"Write a detailed research report addressing this query:\n\n{query}\n\nUse the following research findings:\n\n{context}",
    )

    header = f"# Research Report\n\n**Query:** {query}\n**Iterations:** {iterations}\n"

    return {
        "final_answer": header + "\n" + response,
        "done": True,
    }


def _build_context(state: ResearchState) -> str:
    query = state.get("query", "")
    facts = state.get("extracted_facts", [])
    summaries = state.get("summaries", [])
    sources = state.get("sources", [])

    lines = [f"Research query: {query}\n"]

    if summaries:
        lines.append("## Research Summary")
        for s in summaries:
            lines.append(f"- {s}")
        lines.append("")

    if facts:
        lines.append(f"## Findings ({len(facts)} total)")
        for i, f in enumerate(facts, 1):
            lines.append(f"{i}. {f}")
        lines.append("")

    if sources:
        unique = list(dict.fromkeys(sources))
        lines.append(f"## Sources ({len(unique)} total)")
        for i, s in enumerate(unique, 1):
            lines.append(f"{i}. {s}")

    return "\n".join(lines)
