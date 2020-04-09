import random
import os

def generate_sha(used=[]):
    hash = ''
    while (hash == 'nan') or (hash in used):
        hash = "%032x" % random.getrandbits(128)
    return hash

def get_file_names(path):
    # get list of papers .json from path
    file_names = []
    for file_name in os.listdir(path):
        file_names.append(file_name)
    return file_names
