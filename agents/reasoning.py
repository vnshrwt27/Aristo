"""Reasoning Agent that performs multi-step reasoning over retrieved information"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from agents.state import AgentState
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from typing import List, Dict, Any
import json


class ReasoningAgent:
    """Performs multi-step reasoning over retrieved information"""
    
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        self.llm = ChatGoogleGenerativeAI(model=model_name)
    
    async def reason(self, query: str, chunks: List[Dict[str, Any]], 
                     intent: str, requires_multi_hop: bool) -> Dict[str, Any]:
        """Perform reasoning over retrieved chunks"""
        
        # Format chunks for reasoning
        context_parts = []
        for idx, chunk in enumerate(chunks):
            content = chunk.get("payload", {}).get("content", "")
            source = chunk.get("payload", {}).get("source", "unknown")
            score = chunk.get("score", 0.0)
            context_parts.append(f"[{idx}] Source: {source} (Score: {score:.2f})\n{content}")
        
        context = "\n\n".join(context_parts)
        
        reasoning_prompt = f"""You are a reasoning engine that breaks down complex queries into logical steps.

Query Intent: {intent}
Requires Multi-Hop Reasoning: {requires_multi_hop}

Context:
{context}

User Query: {query}

Perform step-by-step reasoning:
1. Identify what information is present in the context
2. Identify what information is missing or unclear
3. If multi-hop reasoning is needed, break down the logical steps
4. Determine confidence in being able to answer the query (0-100%)

Return ONLY valid JSON:
{{
    "reasoning_steps": [
        {{"step": 1, "description": "...", "findings": "..."}},
        {{"step": 2, "description": "...", "findings": "..."}}
    ],
    "identified_gaps": ["gap1", "gap2"],
    "can_answer": true/false,
    "confidence": 85,
    "requires_additional_retrieval": false
}}"""
        
        response = await self.llm.ainvoke(reasoning_prompt)
        content = response.content.strip()
        
        try:
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            reasoning_result = json.loads(content)
            return reasoning_result
        except Exception as e:
            print(f"Warning: Failed to parse reasoning result: {e}")
            return {
                "reasoning_steps": [],
                "identified_gaps": [],
                "can_answer": True,
                "confidence": 70,
                "requires_additional_retrieval": False
            }
    
    async def execute(self, state: AgentState) -> AgentState:
        """Execute reasoning step"""
        reasoning_result = await self.reason(
            state.query,
            state.retrieved_chunks or [],
            state.query_intent or "understand",
            state.requires_multi_hop
        )
        
        state.reasoning_steps = reasoning_result.get("reasoning_steps", [])
        state.identified_gaps = reasoning_result.get("identified_gaps", [])
        state.confidence_score = reasoning_result.get("confidence", 70) / 100.0
        
        return state


if __name__ == "__main__":
    import asyncio
    
    async def test():
        reasoning = ReasoningAgent()
        
        test_chunks = [
            {
                "score": 0.95,
                "payload": {
                    "content": "Docling is a document parsing tool developed by IBM Research.",
                    "source": "doc1.pdf"
                }
            },
            {
                "score": 0.87,
                "payload": {
                    "content": "It supports PDF, DOCX, and HTML formats with high accuracy.",
                    "source": "doc2.pdf"
                }
            }
        ]
        
        result = await reasoning.reason(
            "What is docling and how does it work?",
            test_chunks,
            "understand",
            False
        )
        
        print("Reasoning Result:")
        print(f"  Steps: {len(result.get('reasoning_steps', []))}")
        print(f"  Gaps: {result.get('identified_gaps', [])}")
        print(f"  Confidence: {result.get('confidence', 0)}%")
        print(f"  Can Answer: {result.get('can_answer', False)}")
    
    asyncio.run(test())
