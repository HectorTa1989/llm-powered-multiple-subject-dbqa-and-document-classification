from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain import hub
from langchain.chains import RetrievalQA
from langchain.callbacks import get_openai_callback

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


# directory separator for windows

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def retrieve_database(filename, question):
    embedding_function = OpenAIEmbeddings()

    # get current directory
    # current_dir = os.getcwd()
    
    # get current directory of the file
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # db path
    full_path = current_dir + "\\chroma_db\\" + filename + "_db"
    # Load the existing Chroma database
    vectorstore = Chroma(persist_directory=full_path,
                         embedding_function=embedding_function)
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 6})

    llm = ChatOpenAI(model_name="gpt-3.5-turbo-1106", temperature=0)
    # prompt = hub.pull("rlm/rag-prompt")
    # # print(
    # prompt.invoke(
    #     {"context": "filler context", "question": "filler question"}
    # ).to_string()
    # # )

    # Retrieve relevant documents based on the question
    # relevant_docs = retriever.get_relevant_documents(question)
    # # print(relevant_docs[0].page_content)
    # print(relevant_docs)

    qa = RetrievalQA.from_chain_type(llm=llm, 
                                     chain_type="stuff", retriever=retriever, return_source_documents=True)
    answer = qa({"query" : question})
    # source_docs = answer["source_documents"]
    # for doc in source_docs:
    #     print(doc.page_content)
    #     print("---------------------------------------------------")

    # print(answer)
    

    # get 'result' from answer json
    result = answer["result"]
    # print(result)

    return result

if __name__ == "__main__":

    with get_openai_callback() as cb:
        filename = input("Enter the filename: ")
        question = input("Enter the question: ")
        answer = retrieve_database(filename, question)
        print(answer)
        print(cb)
