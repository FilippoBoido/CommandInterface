import json
import os

from typing import Optional


def get_list_from_file_object(file_obj):
    return file_obj.read().strip().split('\n')


def get_list_from_file(path_to_file):
    if os.path.isfile(path_to_file):
        with open(path_to_file, 'r') as file_obj:
            return get_list_from_file_object(file_obj)


def add_to_file(path_to_file, str_to_add):
    if os.path.isfile(path_to_file):
        with open(path_to_file, 'r') as file:
            list_from_file = get_list_from_file_object(file)
        if str_to_add not in list_from_file:
            with open(path_to_file, 'a') as file:
                file.write(str_to_add + '\n')
    else:
        with open(path_to_file, 'w') as file:
            file.write(str_to_add + '\n')


def remove_from_file(path_to_file, str_to_remove):
    if os.path.isfile(path_to_file):
        with open(path_to_file, 'r') as file:
            list_from_file: list = get_list_from_file_object(file)
            if str_to_remove in list_from_file:
                list_from_file.remove(str_to_remove)
            rebuilt_list = []
            if list_from_file:
                for symbol_str in list_from_file:
                    rebuilt_list.append(symbol_str + '\n')
        with open(path_to_file, 'w') as file:
            for symbol_str in rebuilt_list:
                file.write(symbol_str)


def get_json(path_to_file) -> Optional[dict]:
    if os.path.isfile(path_to_file):
        with open(path_to_file, 'r') as file:
            return json.load(file)
