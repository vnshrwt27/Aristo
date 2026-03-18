from typing import List, Dict, Any
from pydantic import BaseModel

class ResearchState(BaseModel):
    query: str
    
    documents: List[Dict[str, Any]] = []
    
    extracted_facts: List[str] = []
    
    summaries: List[str] = []
    
    final_answer: str | None = None
    
    sources: List[str] = []