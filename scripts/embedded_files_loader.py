import os
import streamlit as st
from files_processor import getFilesByPattern
from neo4j import GraphDatabase

def printResults(unexpected_loads, successful_loads, unsuccessful_loads):
  """
  Print the results from the task of loading embedded resumes into the Neo4J database
  """
  print(f"===> There were {len(unexpected_loads)} unexpected loads due to multiple matches found for the following names:")
  for load in unexpected_loads:
    print(f"=> {load}")
  print()

  print(f"===> There were {len(successful_loads)} successful loads due to only one match found for the following names:")
  for load in successful_loads:
    print(f"=> {load}")
  print()
  
  print(f"===> There were {len(unsuccessful_loads)} unsuccessful loads due to no matches found for the following names:")
  for load in unsuccessful_loads:
    print(f"=> {load}")


def loadFiles():
  """
  Load the embedded resume files to their corresponding node in the Neo4J database
  """

  AUTH = (st.secrets["NEO4J_USERNAME"], st.secrets["NEO4J_PASSWORD"])
  URI = st.secrets["NEO4J_URI"]

  EMBEDDED_RESUMES_FOLDER = "../.embedded_resumes"
  EMBEDDED_FILE_REAL_START_POSITION = 1
  EMBEDDED_FILE_REAL_END_POSITION = 1
  EXTENSION_LENGTH = 4
  
  driver = GraphDatabase.driver(URI, auth=AUTH)

  resume_files = getFilesByPattern(EMBEDDED_RESUMES_FOLDER, lambda file: file)
  successful_loads = []
  unexpected_loads = []
  unsuccessful_loads = []

  for file in resume_files:
    with(open(f"{EMBEDDED_RESUMES_FOLDER}/{file}", "r", encoding="UTF-8")) as rf:
      filename = file[:-EXTENSION_LENGTH]
      file_content = rf.read()[EMBEDDED_FILE_REAL_START_POSITION:-EMBEDDED_FILE_REAL_END_POSITION]
      file_content = [float(i) for i in file_content.split(", ")]

      records, summary, keys = driver.execute_query(
        "MATCH(user:Employee) WHERE user.name=$name SET user.resume_embed=$embedded_resume RETURN user",
        name=filename,
        embedded_resume=file_content
      )

      if len(records) > 1:
        unexpected_loads.append(filename)
      elif len(records) == 1:
        successful_loads.append(filename)
      else:
        unsuccessful_loads.append(filename)

  driver.close()

  printResults(unexpected_loads, successful_loads, unsuccessful_loads)

loadFiles()