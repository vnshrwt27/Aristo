# Plan For Aristo

**Aristo** right now only has Baseline RAG, to improve the efficiency of RAG we are going to breakdown this into a more complex system 
We will use lexical+vector search as planned (Create an agent to determine based on query which kind of search should it prioritise)

We will  aslo have to add documnet-wise search (create summaries for documents to do broad search accross documents and then then deep search in those documnents)

PostgreSQL will be used for metadata filtering (will look into more ways to implemnet Postgres)

Better processing for documents which are rich in images and tables (document enrichment)



## Basic Langgraph Plan for Aristo 

**Planner** : Will Plan all the worklfow (for now will also determine which kind of search to do will also determine wether or not to contnue searchin in the vector database)
**Reporter** : Will report all the results proclaimed so far in a structured format (like Markdowm ,html or json)
**Synthesizer** : Will Synthesize all the results proclaimed by the Planner 

