import os
from typing import Literal
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


class WebRetriever:
    def __init__(self, api_key: str | None = None):
        self.client = TavilyClient(api_key=api_key or TAVILY_API_KEY)

    def search(
        self,
        query: str,
        k: int = 5,
        search_depth: Literal["basic", "advanced", "fast", "ultra-fast"] = "fast",
    ):
        response = self.client.search(
            query=query,
            max_results=k,
            search_depth=search_depth,
        )

        return [
            {
                "title": r["title"],
                "content": r["content"],
                "url": r["url"],
            }
            for r in response["results"]
        ]
