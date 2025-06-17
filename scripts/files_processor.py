import fitz
import os

def extract(pdf_path):
  """
  Extract text from a PDF file.

  Parameters:
    pdf_path: str
  """
  
  text = ""
  with fitz.open(pdf_path) as pdf_document:
    for page in pdf_document:
      text += page.get_text()

  return text

def getFilesByPattern(dir, matchFunc):
  """
  Retrieve all files from a folder by filtering them using a specific pattern.

  Parameters:
    dir: str
    matchFunc: function
  """

  txt_files = []
  for file in os.listdir(dir):
    if matchFunc(file):
      txt_files.append(file)

  return txt_files
  
def save(text, file_name, ext = "txt"):
  """
  Save text to a file with the specified extension.

  Parameters:
    text: str
    file_name: str
    ext: str
  """

  output_file = f"{file_name}"
  with open(output_file, "w", encoding="utf-8") as f:
    f.write(text)

def process(folder_path, type = 'pdf', output_ext = None):
  """
  Extract text from PDF files in a folder and save it to a text file.

  Parameters:
    folder_path: str
    ext: str
  """

  ext = output_ext or "txt"
  files = [f for f in os.listdir(folder_path) if f.endswith(f".{type}")]

  for f in files:
    file_path = os.path.join(folder_path, f)

    text = extract(file_path)

    output_file = os.path.join(folder_path, f"{os.path.splitext(f)[0]}.{ext}")
    save(text, output_file, ext)

process("../.resumes/")