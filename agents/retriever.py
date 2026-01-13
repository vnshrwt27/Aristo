"""Retriever Agent That retrieves the data from database"""
import asyncio
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from core.vdb_client import client
from core.embedding import model
from agents.state import AgentState
from typing import List, Dict, Any


class RetrieverAgent:
    def __init__(self):
        self.model = model
        self.client = client

    async def get_chunks(self, query: str):
        """Retrieve chunks from vector database"""
        try:
            embedded_query = self.model.encode(query)
            response = await self.client.query_points(
                collection_name="document",
                query=embedded_query,
                limit=5
            )
            
            # Debug: Print the response type and structure
            print(f" Response type: {type(response)}")
            print(f" Response content: {response}")
            
            chunks = []
            
            # Handle different response formats from Qdrant
            if isinstance(response, tuple):
                # If it's a tuple, the points are likely in the first element
                points_list = response[0] if response else []
                print(f" Extracted from tuple, length: {len(points_list)}")
            elif hasattr(response, 'points'):
                # Standard Qdrant response object
                points_list = response.points
                print(f"Using .points attribute, length: {len(points_list)}")
            elif isinstance(response, list):
                # Already a list
                points_list = response
                print(f" Already a list, length: {len(points_list)}")
            else:
                print(f"  Unknown response format: {type(response)}")
                points_list = []
            
            # Convert points to standardized format
            for idx, point in enumerate(points_list):
                try:
                    # Handle different point formats
                    if hasattr(point, 'id'):
                        # ScoredPoint object from Qdrant
                        chunk = {
                            "id": point.id,
                            "score": getattr(point, 'score', 0.0),
                            "payload": getattr(point, 'payload', {})
                        }
                    elif isinstance(point, dict):
                        # Already a dictionary
                        chunk = {
                            "id": point.get("id", idx),
                            "score": point.get("score", 0.0),
                            "payload": point.get("payload", {})
                        }
                    elif isinstance(point, tuple):
                        # Tuple format: (id, score, payload) or similar
                        chunk = {
                            "id": point[0] if len(point) > 0 else idx,
                            "score": point[1] if len(point) > 1 else 0.0,
                            "payload": point[2] if len(point) > 2 else {}
                        }
                    else:
                        print(f" Unknown point format at index {idx}: {type(point)}")
                        continue
                    
                    chunks.append(chunk)
                    
                except Exception as e:
                    print(f"  Failed to process point {idx}: {e}")
                    continue
            
            print(f" Successfully retrieved {len(chunks)} chunks")
            return chunks
            
        except Exception as e:
            print(f" Retrieval failed: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    async def rerank(self, chunks: List[Dict[str, Any]], query: str, reranker=None):
        """To Rerank the outputs from retriever"""
        # TODO: Implement reranking logic
        # This could use a cross-encoder model or other reranking strategy
        if reranker:
            return await reranker.rerank(query, chunks)
        return chunks
    
    async def execute(self, state: AgentState) -> AgentState:
        """Execute retrieval step"""
        try:
            query_to_use = state.refined_query or state.query
            print(f" Retrieving for query: {query_to_use}")
            
            raw_chunks = await self.get_chunks(query_to_use)
            
            if not raw_chunks:
                print("  No chunks retrieved, using empty list")
            
            state.retrieved_chunks = raw_chunks
            state.sender = 'retriever'
            state.receiver = 'synthesizer'
            
            return state
            
        except Exception as e:
            print(f" Retriever execute failed: {e}")
            state.retrieved_chunks = []
            return state


if __name__ == '__main__':
    retriever = RetrieverAgent()
    
    async def main():
        print("Testing retriever...")
        res = await retriever.get_chunks("What is docling?")
        print(f"\nFinal result: {res}")
        
        # Test with state
        from agents.state import AgentState
        test_state = AgentState(query="What is docling?")
        result_state = await retriever.execute(test_state)
        print(f"\nRetrieved {len(result_state.retrieved_chunks)} chunks")
    
    asyncio.run(main())