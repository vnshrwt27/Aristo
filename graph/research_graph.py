from langgraph.graph import StateGraph, END

from state.research_state import ResearchState

# Nodes



#  Stopping Logic

def should_continue(state: ResearchState):
    """
    Controls loop between query generation and retrieval
    """

    # Max iterations safeguard
    if state.get("iterations", 0) >= 3:
        return "stop"

    # If no new queries → stop
    if not state.get("queries"):
        return "stop"

    return "continue"


# Build Graph


def build_research_graph():

    builder = StateGraph(ResearchState)

    # Add nodes to the Graph 

    

    # Set Entry point for the graph 
   

    # Add Edges
    

    # Create loop for iteration (Research)
    

    # Graph end
    builder.add_edge("answer", END)

    return builder.compile()