import os
import pickle
import hashlib

def get_all_topics_str():
    # get current directory of the file
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # get all topics from request_id dictionary
    request_file_name = current_dir + "\\bin_files\\request.bin"
    request_id_dict = {}

    if os.path.exists(request_file_name) and os.path.getsize(request_file_name) > 0:
        with open(request_file_name, "rb") as request_file:
            request_id_dict = pickle.load(request_file)

    topics = []
    for topic in request_id_dict.values():
        topics.append(topic)

    return topics

# get all subjects related with the topic
def get_all_subjects_str(topic):
    # get current directory of the file
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # get all topics from request_id dictionary
    request_file_name = current_dir + "\\bin_files\\request.bin"
    request_id_dict = {}

    if os.path.exists(request_file_name) and os.path.getsize(request_file_name) > 0:
        with open(request_file_name, "rb") as request_file:
            request_id_dict = pickle.load(request_file)

    # get the id of the topic
    topic_id = None
    for id, topic_str in request_id_dict.items():
        if topic_str == topic:
            topic_id = id
            break

    # if topic is not found, return empty list
    if topic_id is None:
        return []

    # get all subjects from the file dictionary
    file_name_bin = current_dir + "\\bin_files\\" + str(topic_id) + ".bin"
    file_dict = {}

    if os.path.exists(file_name_bin) and os.path.getsize(file_name_bin) > 0:
        with open(file_name_bin, "rb") as file:
            file_dict = pickle.load(file)

    subjects = []
    for subject in file_dict.values():
        subjects.append(subject)

    return subjects


# if it is main file, run the code
if __name__ == "__main__":

    # # get all topics
    # topics = get_all_topics_str()
    # print(topics)
    # exit()

    dir_name = "all_files"
    bin_dir_name = "bin_files"
    request_file_name = bin_dir_name + "/request.bin"

    # read id request dictionary from the file
    request_id_dict = {}
    if os.path.exists(request_file_name) and os.path.getsize(request_file_name) > 0:
        with open(request_file_name, "rb") as request_file:
            request_id_dict = pickle.load(request_file)
    else:
        print("request file does not exist")

    # list all requests
    request_list = list(request_id_dict.values())

    # print all requests enumerated
    for i, request in enumerate(request_list):
        print(str(i) + ": " + request)

    # get the request id from user
    request_id = int(input("Select a request: "))

    # hash the request using sha256
    id_request = hashlib.sha256(request_list[request_id].encode("utf-8")).hexdigest()

    # read the file dictionary from the file
    file_name_bin = bin_dir_name + "/" + str(id_request) + ".bin"
    file_dict = {}

    if os.path.exists(file_name_bin) and os.path.getsize(file_name_bin) > 0:
        with open(file_name_bin, "rb") as file:
            file_dict = pickle.load(file)
    else:
        print("file does not exist")

    print(file_dict)

    # print all subjects enumerated and file names
    for i, subject in enumerate(file_dict.values()):
        print(str(i) + ": " + str(subject) + "->" + list(file_dict.keys())[i])

    selection = input("0: Delete a subject\n1: Add a subject\n")

    if selection == "1":
        # get the subject from user
        subject = input("Add a subject: ")

        # get the file name from user
        file_name = input("Enter the file name: ")

        # add the subject to the file dictionary
        file_dict[file_name] = subject

        # write the file dictionary to the file
        with open(file_name_bin, "wb") as file:
            pickle.dump(file_dict, file)

    elif selection == "0":
        # get the subject id from user
        subject_id = int(input("Delete a subject: "))
        subject = list(file_dict.values())[subject_id]

        # delete the subject from the file dictionary
        del file_dict[list(file_dict.keys())[subject_id]]

        # write the file dictionary to the file
        with open(file_name_bin, "wb") as file:
            pickle.dump(file_dict, file)

    else:
        print("Wrong selection")
        exit()