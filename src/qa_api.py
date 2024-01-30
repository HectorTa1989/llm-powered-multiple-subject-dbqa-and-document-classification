from openai import OpenAI
import pickle
import hashlib
import os
import time
from src import db_retriever
from langchain.callbacks import get_openai_callback
import concurrent.futures
import warnings
import asyncio


dir_name = "all_files"
bin_dir_name = "bin_files"
request_file_name = bin_dir_name + "/request.bin"

CONC_MAX = 5

PRICE_INPUT = 0.001 # for 1000 tokens
PRICE_OUTPUT = 0.002 # for 1000 tokens

# define cost class
class Cost:
    # tokens used, prompt token, completion token, total cost(usd)

    # no parameter constructor
    def __init__(self):
        self.total_tokens = 0
        self.prompt_token = 0
        self.completion_token = 0
        self.total_cost = 0

    # print cost
    def print_cost(self):
        print("\n\nTotal tokens: " + str(self.total_tokens))
        print("Prompt tokens: " + str(self.prompt_token))
        print("Completion tokens: " + str(self.completion_token))
        print("Total cost (USD): " + str(self.total_cost))

    # reset cost
    def reset_cost(self):
        self.total_tokens = 0
        self.prompt_token = 0
        self.completion_token = 0
        self.total_cost = 0

REQUEST_CHAR_LIMIT = 5000
answers = []
cost = Cost()

def log_dialogue(question, answers, gpt_answer):

    # open in utf-8 mode to support turkish characters
    with open("dialogue_log.txt", "a", encoding="utf-8") as dialogue_log_file:
        dialogue_log_file.write("Question: " + question + "\n")
        dialogue_log_file.write("Answers: " + str(answers) + "\n")
        dialogue_log_file.write("GPT Answer: \n" + gpt_answer + "\n\n")

def worker_thread(file_name, question, subject):
    response = db_retriever.retrieve_database(file_name, question)
    # print("Subject: " + subject + "\n" + response + "\n\n")

    message_with_subject = subject + ": " + response
    return message_with_subject

def dbqa_answer(question, subject_source):
    print(subject_source)
    print(question)
    answers.clear()
    cost.reset_cost()

    with concurrent.futures.ThreadPoolExecutor(max_workers=CONC_MAX) as executor:
        future_to_subject = {executor.submit(worker_thread, file_name, question, subject): subject for file_name, subject in subject_source.items()}
        for future in concurrent.futures.as_completed(future_to_subject):
            answers.append(future.result())

    return answers

def gpt_answer(question, answers): 
    client = OpenAI()

    # read system message from file "system_message.txt"
    path = os.path.dirname(os.path.abspath(__file__))
    system_message_path = path + "\\system_message.txt"
    system_message = ""
    with open(system_message_path, "r", encoding="utf-8") as system_message_file:
        system_message = system_message_file.read()

    if system_message == "":
        print("system message file is empty")
        exit()

    content = "\nQuestion: " + question + "\nAnswers: \n" + str(answers)

    completion = client.chat.completions.create(
    model="gpt-3.5-turbo-1106",
    messages=[
        {"role": "system", "content": system_message},
        {"role": "user", "content": content}   
    ]
    )

    prompt_tokens = completion.usage.prompt_tokens
    completion_tokens = completion.usage.completion_tokens

    cost = ((prompt_tokens * PRICE_INPUT) + (completion_tokens * PRICE_OUTPUT)) / 1000

    # print(completion)
    # print("unified answer: " + completion.choices[0].message.content)

    return completion.choices[0].message.content, cost

def get_subjects_and_request():
    # read request_id dictionary from the file
    request_dict = {}
    if os.path.exists(request_file_name) and os.path.getsize(request_file_name) > 0:
        with open(request_file_name, "rb") as request_file:
            request_dict = pickle.load(request_file)
    else:
        print("request file does not exist")
        exit()

    print(request_dict)

    # print(request_dict)
    request_list = list(request_dict.values())

    # get request from user
    for i, request in enumerate(request_list):
        print(str(i) + ": " + request)
    selection = input("Select Context: ")

    # hash the request using sha256
    id_request = hashlib.sha256(request_list[int(selection)].encode("utf-8")).hexdigest()

    # read id file dictionary from the file
    file_dict = {}
    file_name_bin = bin_dir_name + "/" + str(id_request) + ".bin"
    if os.path.exists(file_name_bin) and os.path.getsize(file_name_bin) > 0:
        with open(file_name_bin, "rb") as file:
            file_dict = pickle.load(file)
    else:
        print("file does not exist")
        exit()

    print(file_dict)
    request = request_list[int(selection)]

    return file_dict, request

# return <file_name, subject> dictionary and request(topic)
def get_subjects_and_request_v2(topic):

    # get path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # path of request file
    request_file_name = current_dir + "\\bin_files\\request.bin"

    # read request_id dictionary from the file
    request_dict = {}
    if os.path.exists(request_file_name) and os.path.getsize(request_file_name) > 0:
        with open(request_file_name, "rb") as request_file:
            request_dict = pickle.load(request_file)
    else:
        return None, None
    
    # get subjects if request is same as topic
    id_file_name = ""
    for file_name, subject in request_dict.items():
        if subject == topic:
            id_file_name = file_name
            break

    # if no subject found, return None
    if id_file_name == "":
        return None, None
    
    # read id file dictionary from the file
    file_dict = {}
    file_name_bin = current_dir + "\\bin_files\\" + id_file_name + ".bin"
    if os.path.exists(file_name_bin) and os.path.getsize(file_name_bin) > 0:
        with open(file_name_bin, "rb") as file:
            file_dict = pickle.load(file)
    else:
        return None, None
    
    # if no subject found, return None
    if len(file_dict) == 0:
        return None, None
    
    return file_dict, topic

# return <file_name, subject> dictionary
def get_subjects_source(topic):
    
        # get path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # path of request file
        request_file_name = current_dir + "\\bin_files\\request.bin"
    
        # read request_id dictionary from the file
        request_dict = {}
        if os.path.exists(request_file_name) and os.path.getsize(request_file_name) > 0:
            with open(request_file_name, "rb") as request_file:
                request_dict = pickle.load(request_file)
        else:
            return None
        
        # get subjects if request is same as topic
        id_file_name = ""
        for file_name, subject in request_dict.items():
            if subject == topic:
                id_file_name = file_name
                break
    
        # if no subject found, return None
        if id_file_name == "":
            return None
        
        # read id file dictionary from the file
        file_dict = {}
        file_name_bin = current_dir + "\\bin_files\\" + id_file_name + ".bin"
        if os.path.exists(file_name_bin) and os.path.getsize(file_name_bin) > 0:
            with open(file_name_bin, "rb") as file:
                file_dict = pickle.load(file)
        else:
            return None
        
        # if no subject found, return None
        if len(file_dict) == 0:
            return None
        
        return file_dict
    

# ask single question to a single document
def ask_single_doc(query, doc_name):
    answer = ""

    answer = db_retriever.retrieve_database(doc_name, query)

    return answer, 0

def ask_single_subject(query, subject_name, topic):
    # get document related to the subject
    doc_name = get_document(subject_name, topic)

    # ask question to the document
    if doc_name is not None:
        return ask_single_doc(query, doc_name)
    
    return "No document found for the subject: " + subject_name, 0
    

def get_document(subject_name, topic):
    subject_source = get_subjects_source(topic)

    # find document related to the subject
    for file_name, subject in subject_source.items():
        if subject == subject_name:
            return file_name
        
    return None

def ask_question(question, topic, subject_name):
    cost.reset_cost()
    # if subject is "Get All Subjects", get all subjects
    if subject_name != "All Subjects":
        return ask_single_subject(question, subject_name, topic)

    subject_source, request = get_subjects_and_request_v2(topic)

    # get answers from the API
    answers = dbqa_answer(question, subject_source)

    answer, cost_gpt = gpt_answer(question, answers)

    log_dialogue(question, answers, answer)

    return answer, cost_gpt

def ask_question_test(question, topic, subject_name):
    # if subject is "Get All Subjects", get all subjects
    if subject_name != "All Subjects":
        return ask_single_subject(question, subject_name, topic)

    subject_source, request = get_subjects_and_request_v2(topic)

    # get answers from the API
    answers = dbqa_answer(question, subject_source)

    answer, cost_gpt = gpt_answer(question, answers)

    log_dialogue(question, answers, answer)

    return answer, cost_gpt

warnings.filterwarnings("ignore")

# main function if this file is run directly
if __name__ == "__main__":
    # get subjects and request
    subject_source, request = get_subjects_and_request()
    print("\nSubjects: " + str(list(subject_source.values())))
    print("\nContext: " + request + "\n\n")

    # get question from user
    question = input("\n\nQuestion >> ")

    # set start time
    start_time = time.time()

    answer, gpt_cost = ask_question_test(question, request, "All Subjects")
    # print("answer: \n\n" + gpt_answer)
    # print("\n\n")
    # print cost
    cost.total_cost += gpt_cost
    cost.print_cost()

    print("\n\nAnswer: \n\n" + answer)

    # print the elapsed time
    print("\n\nElapsed time: " + str(time.time() - start_time))
