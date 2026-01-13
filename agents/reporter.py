"""Agent that generates the final report for the query"""
import asyncio
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from agents.state import AgentState
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI

class ReporterAgent:
    """Generates a final report for the User query"""
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro")
    
    async def generate_report(self, query: str, synthesis: str, metadata: dict):
        prompt = f"""
        You are a professional Technical Reporter.
        
        User Query: {query}
        Raw Synthesis: {synthesis}
        
        Please format this into a clean, professional Markdown report.
        1. Use clear headings.
        2. If the synthesis mentions code, format it properly.
        3. Include a "Key Takeaways" section at the top.
        """
        response = await self.llm.ainvoke(prompt)
        return response.content

    async def execute(self, state: AgentState) -> AgentState:
        report = await self.generate_report(state.query, state.synthesized_response, state.metadata)
        state.final_report = report
        state.sender = "reporter"
        state.receiver = "user"
        return state