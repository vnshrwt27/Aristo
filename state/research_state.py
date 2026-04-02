from typing import Annotated, Any, Dict, List, Optional
from typing_extensions import TypedDict


def _append_unique(left: list, right: list) -> list:
    result = list(left)
    for item in right:
        if isinstance(item, dict):
            if item not in result:
                result.append(item)
        elif item not in result:
            result.append(item)
    return result


class ResearchState(TypedDict, total=False):
    query: str
    sub_queries: List[str]
    current_query: str
    queries_in_batch: List[str]

    documents: Annotated[List[Dict[str, Any]], _append_unique]
    extracted_facts: Annotated[List[str], _append_unique]
    summaries: Annotated[List[str], _append_unique]
    sources: Annotated[List[str], _append_unique]

    final_answer: Optional[str]
    iterations: int
    max_iterations: int
    batch_size: int
    gaps: List[str]
    done: bool
    errors: Annotated[List[Dict[str, str]], _append_unique]
