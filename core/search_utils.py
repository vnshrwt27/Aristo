from vdb_client import client
from embedding import model
import asyncio

query="What is Docling?"
embedded_query=model.encode(query)


#print(embedded_query)
#TODO: Create a better search utility to search in RAG database
#TODO: Improve Accuracy 
async def main():
    res=await client.query_points(collection_name="document",query=embedded_query,limit=10)
    #print(res.points)
    for i in res.points:
        print(i.payload['content'])
    
asyncio.run(main())