from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter
from langchain.document_loaders import PyPDFLoader
from langchain.document_loaders import UnstructuredPDFLoader
import fitz  # PyMuPDF
import os


# # these three lines swap the stdlib sqlite3 lib with the pysqlite3 package
# __import__('pysqlite3')
# import sys
# sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(os.path.dirname(os.path.abspath(__file__)), "db.sqlite3"),
#     }
# }

dir_name = "all_files"

# directory separator for windows
separator = "\\"
# if os.name == "nt":
#     separator = "\\"
# else:
#     separator = "/"

def create_database(filename):

    # path = os.getcwd() + separator + dir_name + separator + filename
    path = filename
    print("filename: " + filename)

    # get last part of path
    separated_filename = path.split(separator)
    filename = separated_filename[len(separated_filename) - 1]
    print("filename: " + filename)

    chroma_db_path = os.getcwd() + separator + "src\chroma_db" + separator + filename + "_db"
    print("chroma_db_path: " + chroma_db_path)

    # Load with PyPDF
    # loader = PyPDFLoader(path)

    # Load with UnstructuredPDFLoader
    loader = UnstructuredPDFLoader(path)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    splits = text_splitter.split_documents(documents)
    # for split in splits:
    #     print(split.page_content)
    #     print("---------------------------------------------------")
    # exit()

    # Create Chroma database
    Chroma.from_documents(
        documents=splits,
        embedding=OpenAIEmbeddings(),
        persist_directory=chroma_db_path,
    )

if __name__ == "__main__":

    filename = input("Enter the filename: ")
    create_database(filename)
    print(f"Database for {filename} created successfully.")

