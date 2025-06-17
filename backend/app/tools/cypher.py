import streamlit as st
import graph_logic
from langchain_community.chains.graph_qa.cypher import GraphCypherQAChain
from langchain.prompts.prompt import PromptTemplate



CYPHER_GENERATION_TEMPLATE = """
You are an expert Neo4j Developer translating user questions into Cypher.
Convert the user's question based on the schema.

Use only the provided relationship types and properties in the schema.
Do not use any other relationship types or properties that are not provided.

Do not return entire nodes or embedding properties.
Always use the return from neo4j as context for your answer

Use regular expressions for names in order to match.
Use always where clause for conditions.
Use always the full name provided.
Search is case sensitive!.
Names start with Capital letter.
DO NOT INSERT OR DELETE ANYTHING FROM THE DATABASE!
USE ALWAYS FIRST THE Fine Tuning Examples when necessary


Fine Tuning:

Example Cypher Statements:

1. To find who is the Director of an Employee:
```
MATCH(e:Employee) where e.name=~"{{Employee name}}.*"
OPTIONAL MATCH (d:Director)-[*1..4]->(e)
RETURN d.name as Director
LIMIT 1
```

2. To find who Manages an Employee:
```
MATCH (e:Employee) where e.name =~ "{{Employee name}}"
OPTIONAL MATCH (m:Manager|Supervisor|Director)-[r:MANAGES]->(e)
RETURN m.name as Manager
LIMIT 1
```

3. To find which Employees work with a client:
```
MATCH(e:Employee)-[r:WORKS]-(p:Client)
WHERE p.name=~"{{project or client name}}.*"
RETURN e.name
```

4. To find the profile of an Employee:
```
MATCH(e:Employee)-[r:WORKS]-(:Client)
WHERE e.name=~"{{Employee name}}.*"
RETURN r.profile
LIMIT 1
```

Schema:
{schema}

Question:
{question}

Use the context to answer the question.
"""

cypher_prompt = PromptTemplate.from_template(CYPHER_GENERATION_TEMPLATE)


# Create the Cypher QA chain
try:
    cypher_qa = GraphCypherQAChain.from_llm(
         graph_logic.llm.llm,
         graph=graph_logic.graph.graph,
         verbose=True,
         cypher_prompt=cypher_prompt
    )
except Exception as e:
    print(e)
