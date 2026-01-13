from langgraph.graph import StateGraph, START, END
from typing import Dict, Any, Optional, List, Annotated
from typing_extensions import TypedDict
from dataclasses import dataclass, field
import asyncio

from state import AgentState
# Import your agents
from agents.retriever import RetrieverAgent
from agents.synthesizer import SynthesizerAgent
from agents.query_refiner import QueryRefinerAgent
from agents.reporter import ReporterAgent
# from agents.reasoning import ReasoningAgent # Optional: Enable if you want the reasoning step


class AgentOrchestrator:
    def __init__(self):
        # Initialize actual instances
        self.query_refiner = QueryRefinerAgent()
        self.retriever = RetrieverAgent()
        self.synthesizer = SynthesizerAgent()
        self.reporter = ReporterAgent()
        
        # Build graph immediately
        self.graph = self.build_graph()

    def build_graph(self) -> StateGraph:
        workflow = StateGraph(AgentState)

        # 1. Add Nodes
        workflow.add_node("refine_query", self.query_refiner.execute)
        workflow.add_node("retrieve_data", self.retriever.execute)        
        workflow.add_node("synthesize_data", self.synthesizer.execute)
        workflow.add_node("generate_report", self.reporter.execute)

        # 2. Add Edges (Strings must match Node names exactly)
        workflow.add_edge(START, "refine_query")
        workflow.add_edge("refine_query", "retrieve_data")
        workflow.add_edge("retrieve_data", "synthesize_data")
        workflow.add_edge("synthesize_data", "generate_report")
        workflow.add_edge("generate_report", END)

        return workflow.compile()

    async def run(self, query: str):
        initial_state = AgentState(query=query)
        result = await self.graph.ainvoke(initial_state)
        return result