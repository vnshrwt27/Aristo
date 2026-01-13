from os import GRND_NONBLOCK
import yaml 
from core.agent_registry import AgentSpec ,GLOBAL_AGENT_REGISTRY

def load_agent_from_yaml(path:str):
    with open(path,"r") as f:
        data=yaml.safe_load(f)

    agent=data["agent"]
    spec=AgentSpec(
            id= agent["id"],
            role=agent.get("role",""),
            description=agent.get("description",""),
            prompt=agent.get("prompt",{}),
            input_spec=agent.get("input",{}),
            output_spec=agent.get("output",{}))
    GLOBAL_AGENT_REGISTRY.register(spec)
