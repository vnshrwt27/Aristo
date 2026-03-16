
from tavily import TavilyClient


class WebRetriever:

    def __init__(self, api_key: str):
        self.client = TavilyClient(api_key)

    def search(self, query: str, k: int = 5):
        """
        Search the web for new information.
        """

        response = self.client.search(
            query=query,
            max_results=k
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