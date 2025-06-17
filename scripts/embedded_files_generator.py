import os
import re
from files_processor import getFilesByPattern
from langchain_community.embeddings import OllamaEmbeddings

ollama_emb = OllamaEmbeddings(model="nomic-embed-text", base_url=os.environ["OLLAMA_HOST"])

def embedFiles():
  """
  Embed the plain text files from a folder using Ollama.
  """

  EMBEDDED_RESUMES_FOLDER = "../.embedded_resumes"
  EXTENSION_LENGTH = 4
  RESUMES_FOLDER = "../.resumes"
  
  resume_files = getFilesByPattern(RESUMES_FOLDER, lambda file: file.endswith(".txt"))

  for resume_file in resume_files:
    embedded_file_content = ''

    with open(f"{RESUMES_FOLDER}/{resume_file}", 'r', encoding='utf-8') as rf:
      resume_file_content = rf.read()
      embedded_file_content = ollama_emb.embed_query(resume_file_content)

    with open(f"{EMBEDDED_RESUMES_FOLDER}/{resume_file[:-EXTENSION_LENGTH]}.txt", "w") as rfe:
      rfe.write(str(embedded_file_content))

embedFiles()