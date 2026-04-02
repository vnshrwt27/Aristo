from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver

from state.research_state import ResearchState

from graph.nodes.decomposer import decompose
from graph.nodes.agent_runner import retrieve
from graph.nodes.aggregator import aggregate
from graph.nodes.synthesizer import check_gaps, synthesize
from graph.nodes.generate_queries import generate_queries


def _state_snapshot(state: dict, node_name: str):
    print(f"\n{'=' * 60}")
    print(f"NODE: {node_name}")
    print(f"{'=' * 60}")
    keys = [
        "query", "sub_queries", "queries_in_batch", "current_query",
        "documents", "extracted_facts", "summaries", "sources",
        "iterations", "batch_size", "gaps", "done", "errors",
    ]
    for k in keys:
        v = state.get(k)
        if v is None:
            continue
        if isinstance(v, list):
            print(f"  {k}: [{len(v)} items]")
            for i, item in enumerate(v[:3]):
                preview = str(item)[:120]
                print(f"    [{i}] {preview}")
            if len(v) > 3:
                print(f"    ... and {len(v) - 3} more")
        else:
            print(f"  {k}: {v}")
    print()


def _wrap_node(node_fn, name):
    def wrapped(state):
        result = node_fn(state)
        _state_snapshot({**state, **result}, name)
        return result
    return wrapped


def build_research_graph(debug: bool = True):
    builder = StateGraph(ResearchState)

    nodes = {
        "decompose": decompose,
        "retrieve": retrieve,
        "aggregate": aggregate,
        "generate_queries": generate_queries,
        "synthesize": synthesize,
    }

    for name, fn in nodes.items():
        builder.add_node(name, _wrap_node(fn, name) if debug else fn)

    builder.add_edge(START, "decompose")
    builder.add_edge("decompose", "retrieve")
    builder.add_edge("retrieve", "aggregate")

    builder.add_conditional_edges(
        "aggregate",
        check_gaps,
        {
            "retrieve": "retrieve",
            "generate_queries": "generate_queries",
            "synthesize": "synthesize",
        },
    )

    builder.add_edge("generate_queries", "retrieve")
    builder.add_edge("synthesize", END)

    return builder.compile(checkpointer=InMemorySaver())
