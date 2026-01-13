from dataclasses import dataclass, field 
from typing import Optional , Any ,List,Dict
@dataclass
class AgentState:
    """Shared state between all agents"""
    query: str
    sender: str = "user"
    receiver: str = ""
    
    # Query refinement
    refined_query: Optional[str] = None
    query_intent: Optional[str] = None
    query_complexity: Optional[str] = None  # ✅ Add this
    requires_multi_hop: bool = False  # ✅ Add this

    
    # Retrieval (Standardize on 'retrieved_chunks')
    retrieved_chunks: List[Any] = field(default_factory=list)
    
    # Synthesis
    synthesized_response: Optional[str] = None
    
    # Final Output
    final_report: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
