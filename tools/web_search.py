from tools.base import Tools

class WebSearchTool(Tools):
    name= "web_search",
    description= "Searches the Web for the user Query",
    input_schema={
            "query": "string",
            "k": "int"
            }
    output_schema={
            "results": "list[object]"
            }
    def run(self, query: str, k: int) -> dict:
        

        return {
                "results": "results"
                }
