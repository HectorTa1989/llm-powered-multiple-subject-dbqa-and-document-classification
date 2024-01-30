import os
import fitz  # PyMuPDF
import requests
from openai import OpenAI 
import json
import pickle
import hashlib
from src import db_creation

# import threading
import concurrent.futures
from concurrent.futures import as_completed, ThreadPoolExecutor
import time

dir_name = "all_files"
bin_dir_name = "bin_files"
request_file_name = bin_dir_name + "/request.bin"

# ask at most N files same time
N = 1

CONC_REQUEST_MAX = 5

CHAR_LIMIT = 250
REQUEST_CHAR_LIMIT = 5000

PRICE_INPUT = 0.001 # for 1000 tokens
PRICE_OUTPUT = 0.002 # for 1000 tokens

def process_pdf(pdf_path):
    count = 0
    p_text = ""

    with fitz.open(pdf_path) as pdf_document:
        i = 0
        while count < CHAR_LIMIT and i < len(pdf_document):
            page = pdf_document.load_page(i)
            text = page.get_text("text")
            total_len = len(text)
            pos = 0

            while count < CHAR_LIMIT and pos < total_len:
                p_text += process_text(text[pos:pos + CHAR_LIMIT])
                
                count += len(p_text)
                pos += CHAR_LIMIT

            i += 1
    
    if p_text == "":
        return ""

    s_text = summarize_text(p_text)

    return s_text

# topic: the topic of the documents
# path: directory of the documents will be classified
# return: <file_name, subject> dictionary
def generate_documents(topic, path):
    files = {}

    if not os.path.exists(path):
        print("Path does not exist")
        return None

    with ThreadPoolExecutor(max_workers=CONC_REQUEST_MAX) as executor:
        futures = {executor.submit(process_pdf, os.path.join(path, file_name)): 
                   file_name for file_name in os.listdir(path) if file_name.endswith(".pdf")}

        for future in as_completed(futures):
            file_name = futures[future]
            try:
                s_text = future.result()
                files[file_name] = s_text
            except Exception as e:
                print(f"Error processing {file_name}: {e}")

    # total_text_size = sum(len(text) for text in files.values())
    # print("Total text size:", total_text_size)
    # print(files)

    result_json_arr = ask_gpt(files, topic)
    print(result_json_arr)

    file_dict = {}
    for result_json in result_json_arr:
        file_dict.update(process_json(result_json))

    # print("Context:", topic)
    # print(file_dict)

    return file_dict

def save_documents(topic, path, file_dict):
    # add all files in the directory to the source
    log_files(file_dict, topic)

    # create database for each file if it does not exist
    for file_name in file_dict.keys():
        if file_name.endswith(".pdf"):
            pdf_path = os.path.join(path, file_name)
            db_creation.create_database(pdf_path)

def process_text(text):
    new_text = ""

    # get words newline by newline
    for line in text.splitlines():
        # get words word by word
        for word in line.split():
            # remove punctuation
            word = word.strip(",.?!:;()[]{}")
            # check if it contains only letters
            if word.isalpha():
                # add to the new text
                new_text += word + " "
    return new_text

def ask_gpt_single(client, system_message, content):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": content}
        ]
    )
    return completion.choices[0].message.content, completion.usage.prompt_tokens, completion.usage.completion_tokens

def ask_gpt(files, request):
    client = OpenAI()

    # read system message from file "system_message_doc_classification.txt"
    cur_path = os.path.dirname(os.path.abspath(__file__))
    system_message_path = cur_path + "/system_message_doc_classification.txt"
    system_message = ""
    # open in utf-8 encoding
    with open(system_message_path, "r", encoding="utf-8") as system_message_file:
        system_message = system_message_file.read()

    # add type and request to system message
    system_message += "\nrequest: " + request

    result = []
    prompt_token = 0
    completion_token = 0

    with ThreadPoolExecutor(max_workers=CONC_REQUEST_MAX) as executor:
        futures = []

        for i in range(0, len(files), N):
            # concatenate all texts with file names
            content = ""
            for file_name, text in list(files.items())[i:i + N]:
                content += "\n" + file_name + ":\n" + text + "\n"

            # Submit the task to the thread pool
            future = executor.submit(ask_gpt_single, client, system_message, content)
            futures.append(future)

        for future in futures:
            try:
                content_result, prompt_tokens, completion_tokens = future.result()
                prompt_token += prompt_tokens
                completion_token += completion_tokens
                result.append(content_result)
            except Exception as e:
                print(f"Error processing task: {e}")

    print("Prompt tokens: " + str(prompt_token))
    print("Completion tokens: " + str(completion_token))
    print("Price: " + str((prompt_token * PRICE_INPUT + completion_token * PRICE_OUTPUT) / 1000))

    return result

# write to the log file as binary
# if the file does not exist, create it
# first write request name with id to request.bin file as: <request, id> dictionary
# id.bin: <file_name, text> dictionary
def log_files(file_dict, request):
    
    request_id_dict = {}

    bin_dir_path = os.path.dirname(os.path.abspath(__file__)) + "/" + bin_dir_name
    request_file_path = bin_dir_path + "/request.bin"

    # if directory does not exist, create it
    if not os.path.exists(bin_dir_path):
        os.makedirs(bin_dir_path)

    # if file exists, and not empty read the dictionary
    if os.path.exists(request_file_path) and os.path.getsize(request_file_path) > 0:
        with open(request_file_path, "rb") as request_file:
            request_id_dict = pickle.load(request_file)
    
    # add the request to the dictionary with a new id
    # id is hash of the request, utf-8 encoded
    id = hashlib.sha256(request.encode("utf-8")).hexdigest()
    request_id_dict[id] = request

    # write the dictionary to the file
    with open(request_file_path, "wb") as request_file:
        pickle.dump(request_id_dict, request_file)

    # write the file dictionary to the log file, file name is the id
    # write to id.bin file
    file_name_bin = bin_dir_path + "/" + str(id) + ".bin"

    old_file_dict = {}
    # if file exists, and not empty read the dictionary
    if os.path.exists(file_name_bin) and os.path.getsize(file_name_bin) > 0:
        with open(file_name_bin, "rb") as file:
            old_file_dict = pickle.load(file)
    
    # add the new file dictionary to the old one if it is not empty
    # if len(old_file_dict) > 0:
    #     old_file_dict.update(file_dict)
    # else:
    #     old_file_dict = file_dict
    old_file_dict = file_dict
    # write the dictionary to the file
    with open(file_name_bin, "wb") as file:
        pickle.dump(old_file_dict, file)

# input is the json string returned from gpt
# return is the <file_name, subject> dictionary
def process_json(json_str):
    file_dict = {}
    
    # if json surrogated with ```json and ``` remove them
    if json_str.startswith("```json"):
        json_str = json_str[7:]
    if json_str.endswith("```"):
        json_str = json_str[:-3]

    try:
        json_data = json.loads(json_str)
        for file_name, subject in json_data.items():
            if subject.lower() != "no":
                file_dict[file_name] = subject
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        print("json_str: " + json_str)
    
    return file_dict

def summarize_text(text):
    # ask gpt to summarize the text
    client = OpenAI()

    # read system message from file "system_message_doc_classification.txt"
    cur_path = os.path.dirname(os.path.abspath(__file__))
    system_message = "You are a summarizer, just give the summarized text with maximum 4 sentence."
    query = "text: " + text

    completion = client.chat.completions.create(
    model="gpt-3.5-turbo-1106",
    messages=[
        {"role": "system", "content": system_message},
        {"role": "user", "content": query}
    ]
    )
    # print("summary: " + completion.choices[0].message.content)
    return completion.choices[0].message.content

if __name__ == "__main__":

    # file, text tuple dictionary
    files = {}
    topic = input("Enter the topic: ")
    path = "all_files"

    # time the process
    start = time.perf_counter()
    # generate documents
    files = generate_documents(topic, path)
    
    finish = time.perf_counter()

    print(f"Parallel Finished in {round(finish-start, 2)} second(s)")
    print(files)
    