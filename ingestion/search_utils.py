from vdb_client import client
from embedding import model
import asyncio

query="What is Docling?"
embedded_query=model.encode(query)
#TODO: Create a proper search utils
class SearchUtils:
    def __init__(self ,collection_name: str ,model,client):
        self.model=model
        self.client=client
        self.collection_name=collection_name

    async def search_query(self,query: str):
        embedded_query=self.model.encode(query)
        res= await client.query_points(collection_name=self.collection_name,query=embedded_query, limit=5)
#print(embedded_query)
#TODO: Create a better search utility to search in RAG database
#TODO: Improve Accuracy 
async def main():
    res=await client.query_points(collection_name="document",query=embedded_query,limit=1)
    print(res)
    for i in res.points:
        print(i.payload['content'])
    
asyncio.run(main())