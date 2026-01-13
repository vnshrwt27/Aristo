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




Also create a proper agent that does deep research , verifies data and uses postgres for versioning and other  purposes 
uses vecor databse for semantic seraches creates a structured way of travesrsing forks by assighnin exh forks and questions values higher valued forks are prefferred more whne answering but alos implement a sytem to keep in mind the lesser score versions(maybe adding some probalities or some randomness to fork selection) 
implement RL  concelpt like exploration vs exploitaion , use pat experienc as well as explore more 
Value user input allow data sourece control while also keeping the forks so a reranker tochange the vlaue to forks when a data source is changed
understant the user intent hidden , ak for clarifictaions if needde (this should be minimal ) 
Important to use Statistics and dome models dfunctions that determine these thing instead of pluggin  LLM everywhere 


Very important : Keep the LLM usage to minimum for this as it is not onlu my current project but also a learning experience

Note: you can refer to yaml style formating for actions and tools for those actions , with carefully written prompts and deatiled files  Refer to AgentForge for this 
