from langchain.agents import create_agent

from retrieval.retrieval_tools import retrieval_tools


class ResearchAgent:

    def __init__(self, llm, max_iters: int = 5):

        self.agent = create_agent(
            tools=retrieval_tools,
            model=llm,
            name= "Aristo Research"
        )

    def run(self, topic: str):

        prompt = f"""
        You are an autonomous research agent.

        Your goal is to deeply research the following topic:

        TOPIC: {topic}

        You can:
        - search internal documents
        - search the web

        Instructions:
        - Explore the topic thoroughly
        - Perform multiple searches if needed
        - Refine your queries based on findings
        - Gather useful insights

        Finally, return:
        1. Key insights (bullet points)
        2. Important sources (if available)
        """

        result = self.agent.run(prompt)

        return result