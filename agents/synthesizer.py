from typing import List,Dict,Any
import os 
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from agents.state import AgentState
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI

class SynthesizerAgent:
    def __init__(self, model_name: str ="gemini-2.5-pro"):
        self.llm=ChatGoogleGenerativeAI(model=model_name)
    
    def format_context(self, chunks):
        """Format retrieved chunks into context for LLM"""
        context_parts=[]
        for idx,chunk in enumerate(chunks):
            text=chunk.get("payload",{}).get("content")
            context_parts.append(f"Context[{idx}]:\n{text}")
        return "\n\n".join(context_parts)
    
    async def synthesize(self,query:str ,chunks: List[Dict[str,Any]]):
        """Generate response using llm with retrieved context"""
        context=self.format_context(chunks=chunks)
        prompt = f"""
You are an analytical Research Assistant specializing in synthesizing information from multiple retrieved sources.
Combine evidence from the provided context to form a coherent, factual, and technically accurate answer to the user's query.
Avoid speculation and clearly indicate any uncertainty or missing data.
Context :{context}
User Query:{query}
Provide a clear and concise answer"""
        response=await self.llm.ainvoke(prompt)
        return response.content

    async def execute(self, state: AgentState) -> AgentState:
        """Langraph node for synthesizer """
        # FIXED: Added await and standardized variable name
        response = await self.synthesize(state.query, state.retrieved_chunks)
        state.synthesized_response = response
        state.sender = "synthesizer"
        state.receiver = "reporter"
        return state
# Testing
if __name__ == "__main__":
    import asyncio
    
    async def test():
        synthesizer = SynthesizerAgent()
        
        # Mock chunks for testing
        test_chunks = [
            {
                "payload": {
                    "content": "Docling is a document parsing and conversion tool developed by IBM Research."
                }
            },
            {
                "payload": {
                    "content": "It supports converting various document formats including PDF, DOCX, and HTML to structured formats."
                }
            }
        ]
        
        response = await synthesizer.synthesize("What is docling?", test_chunks)
        print("Synthesized Response:")
        print(response)
    
    asyncio.run(test())
