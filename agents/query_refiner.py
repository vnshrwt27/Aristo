"""Agent that uses LLM to understand user query and refine it for better retrieval"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from agents.state import AgentState
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
import json
from typing import Dict,Any


class QueryRefinerAgent:
    """Understands and refines user queries with intent analysis"""
    
    def __init__(self, model_name: str = "gemini-2.0-flash"):
        self.llm = ChatGoogleGenerativeAI(model=model_name)
    
    async def analyze_query(self, query: str) -> Dict[str, Any]:
        """Analyze query intent, complexity, and requirements"""
        prompt = f"""Analyze this query and provide structured insights:

Query: {query}

Provide:
1. Intent: What is the user trying to achieve? (understand/compare/analyze/create/troubleshoot)
2. Complexity: Simple/Medium/Complex
3. RequiresMultiHop: Does this need information from multiple sources? (yes/no)
4. KeyConcepts: List 3-5 key concepts to search for
5. RefinedQuery: An improved version optimized for retrieval

Return ONLY valid JSON:
{{
    "intent": "...",
    "complexity": "...",
    "requires_multi_hop": true/false,
    "key_concepts": ["...", "..."],
    "refined_query": "..."
}}"""
        
        response = await self.llm.ainvoke(prompt)
        content = response.content.strip()
        
        try:
            # Remove markdown code blocks if present
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            analysis = json.loads(content)
            return analysis
        except Exception as e:
            print(f"Warning: Failed to parse query analysis: {e}")
            # Fallback if parsing fails
            return {
                "intent": "understand",
                "complexity": "medium",
                "requires_multi_hop": False,
                "key_concepts": [query],
                "refined_query": query
            }
    
    async def execute(self, state: AgentState) -> AgentState:
        """Execute query refinement with analysis"""
        analysis = await self.analyze_query(state.query)
        
        state.refined_query = analysis.get("refined_query", state.query)
        state.query_intent = analysis.get("intent", "understand")
        state.query_complexity = analysis.get("complexity", "medium")
        state.requires_multi_hop = analysis.get("requires_multi_hop", False)
        state.metadata["key_concepts"] = analysis.get("key_concepts", [])
        
        return state


if __name__ == '__main__':
    import asyncio
    
    async def test():
        refiner = QueryRefinerAgent()
        
        test_query = "What is docling and how does it compare to pypdf?"
        print(f"Original Query: {test_query}\n")
        
        analysis = await refiner.analyze_query(test_query)
        print("Analysis Result:")
        print(f"  Intent: {analysis.get('intent')}")
        print(f"  Complexity: {analysis.get('complexity')}")
        print(f"  Multi-hop: {analysis.get('requires_multi_hop')}")
        print(f"  Refined: {analysis.get('refined_query')}")
        print(f"  Key Concepts: {analysis.get('key_concepts')}")
    
    asyncio.run(test())
