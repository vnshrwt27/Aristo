from abc import abstractmethod
from typing import Any, Dict, Optional


class Tools:
    name: str
    description: str 
    input_schema: Optional[dict]

    output_schema: Optional[dict]

    max_calls_per_run : int=1
    uses_llm: bool =False

    @abstractmethod
    def run(self,**kwargs) -> Any:

        raise NotImplementedError
