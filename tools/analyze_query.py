from os import initgroups
from typing import Dict
from google import genai
from base import Tools


llm=genai.Client(api_key="AIzaSyAhvD6Vs5W8H9HTbkUH-3hrwtnrwGjhfgI")

class AnalyzeQueryTool(Tools):
    name="analyze_query",
    description="Extracts Intent and metadata from the query"
    input_schema={
            "query" : "string" 
            }
    output_schema={
            "intent": "string",
            "query_type": "string",
            "domain": "string",
            "entities": "list[string]",
            "constraints": "list[sting]"
    }
    uses_llm=True

    def run(self,query: str) -> dict:
        messages=[{
                "role": "system",
                "content":(
                    "Analyze the user query and extract:\n"
                    "- intent\n" 
                    "- query_type\n" 
                    "- domain\n" 
                    "- entities\n"
                    "- constraints\n " 
                    )},
                  {"role":"user","content": query }
                  ]
        response=llm.models.generate_content(
                model="gemini-2.5-flash",contents=str(messages)
                )
        return response.text

tool=AnalyzeQueryTool()
res=tool.run("Hello , Tell me about India")
print(res)
