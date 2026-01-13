"""
Agent Registry
Used to register Agents to be used by the System to call agents by capabilities instead of name
""" 


from typing import Dict,List, Optional,Type,Any
from dataclasses import dataclass ,field

@dataclass(frozen=True)
class AgentSpec:
    id: str 
    role: str
    description: Optional[str]= None
    agent_class: Optional[str]= None
    prompt: Optional[dict]= None
    output_spec: Optional[dict]= None
    input_spec: Optional[dict] = None


class AgentRegistry:

    def __init__(self) :
        self._agents :Dict[str , AgentSpec] ={}

    def register(self, spec: AgentSpec)-> None:
        if spec.id in self._agents:
            raise ValueError(f"Agent : '{spec.id}' already registered")
        
        self._agents[spec.id]=spec

    def get(self,id : str) -> AgentSpec:
        try:
            return self._agents[id]
        except:
            raise KeyError(f"Agent '{id}' not found")
    def list(self) -> List[str]:
        return list(self._agents.keys())

    #def get_by_role(self) -> AgentSpec:
    #def get_by_capability(self) -> AgentSpec:

#Global Agent Registry
GLOBAL_AGENT_REGISTRY=AgentRegistry()

        

