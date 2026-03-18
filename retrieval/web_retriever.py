
from tavily import TavilyClient
import os 

from dotenv import load_dotenv

load_dotenv()

TAVILY_API_KEY= os.getenv("TAVILY_API_KEY")


class WebRetriever:

    def __init__(self, api_key: str):
        self.client = TavilyClient(api_key=TAVILY_API_KEY)

    def search(self, query: str, k: int = 5, search_depth : "fast"):
        """
        Search the web for new information.
        """

        response = self.client.search(
            query=query,
            max_results=k,
            search_depth=search_depth
        )

        results = []

        for r in response["results"]:
            results.append(
                {
                    "title": r["title"],
                    "content": r["content"],
                    "url": r["url"]
                }
            )

        return results