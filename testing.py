from core.agent_registry import GLOBAL_AGENT_REGISTRY
from core.agent_loader import load_agent_from_yaml
from google import genai
client=genai.Client(api_key="AIzaSyAhvD6Vs5W8H9HTbkUH-3hrwtnrwGjhfgI")

load_agent_from_yaml("agents/query_analyzer.yaml")
request=GLOBAL_AGENT_REGISTRY._agents["query_analyzer"]
print(request)

response=client.models.generate_content(
        model="gemini-2.5-flash",
        contents=str(request)+"Find Out about USA")
print(response.text)
