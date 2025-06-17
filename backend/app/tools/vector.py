import streamlit as st
from graph_logic import graph, llm
from langchain_community.vectorstores.neo4j_vector import Neo4jVector
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain.schema import StrOutputParser


# Create the Neo4jVector
neo4jvector = Neo4jVector.from_existing_index(
    llm.ollama_emb,                              # (1)
    graph=graph.graph,                             # (2)
    index_name="resume_embed",                 # (3)
    node_label="Employees",                      # (4)
    text_node_property="resume",               # (5)
    embedding_node_property="resume_embed",  # (6)
    retrieval_query="""
RETURN
    node.resume AS text,
    score,
    {
        name: node.name,
        Position: labels(node)
    } AS metadata
"""
)

# Create the retriever
retriever = neo4jvector.as_retriever()
# Create the prompt
instructions = """"
    Be helpful and kind, detail the answer.
    Never refer to the user, use the context and metadata to answer questions, refer with names. 
    Do not answer any questions using your pre-trained knowledge.
    Always use the return from neo4j as context for your answer.
    Include always the name or names provided in the answer.
    Context: {context}
    """

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", instructions),
        ("human", "{input}"),
    ]
)
# Create the chain
question_answer_chain = create_stuff_documents_chain(llm.llm, prompt)
plot_retriever = create_retrieval_chain(
    retriever,
    question_answer_chain,
)


# Create a function to call the chain
def get_resume(u_input):
    return plot_retriever.invoke({"input": u_input})
