"""
Functions for reading txt files
"""
import re
from glob import glob


def get_name_from_path(path: str):
    path = path.replace("_", " ")
    path = path.replace("stories", "")
    path = path.replace("txt", "")
    path = re.sub(r"[^\w\s]", "", path)
    return path


def read_text(path: str, stories: bool = False):
    for text_path in glob(path):
        f = open(text_path, "r", encoding="utf8")
        text = f.read()
        if stories:
            text_name = get_name_from_path(text_path)
            yield text_name, text
        else:
            yield text
