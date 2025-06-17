import os
import streamlit as st
from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate

from langchain_community.embeddings import OllamaEmbeddings

from langchain.schema import StrOutputParser

from langchain.chains import create_retrieval_chain

from langchain.chains.combine_documents import create_stuff_documents_chain


# Create the LLM
prompt = ChatPromptTemplate.from_messages([(
    "system", "You are a kind person that answers brief"
    "Do not answer any questions that do not relate to Apex Systems, Employees"
    ", Associates, Managers, Supervisors, Sr, Tech Leads or Directors."
    "Do not answer any questions using your pre-trained knowledge."),

 ("human", "{input}")
])

# model = SentenceTransformer('all-MiniLM-L6-v2nomic-embed-text')
llm = Ollama(model="llama3", base_url="http://ollama-container:11434")

ollama_emb = OllamaEmbeddings(model='nomic-embed-text', base_url="http://ollama-container:11434")

chain = prompt | llm | StrOutputParser()
