"""
Util functions
"""
import re, os
from glob import glob
import pandas as pd
from typing import List


def get_name_from_path(path: str):
    name = os.path.split(path)[1]
    name = name.replace("_", " ")
    name = name.replace("txt", "")
    name = re.sub(r"[^\w\s]", "", name)
    return name


def read_text(path: str, stories: bool = False):
    for text_path in glob(path):
        f = open(text_path, "r", encoding="utf8")
        text = f.read()
        if stories:
            text_name = get_name_from_path(text_path)
            yield text_name, text
        else:
            yield text


def list_to_csv(df_list: List[dict], out_path: str, extra_cols: dict = {}):
    df = pd.DataFrame(df_list, index=range(len(df_list)))
    for name, values in extra_cols.items():
        df[name] = values
    df.to_csv(out_path, mode="a", header=not os.path.exists(out_path))


def get_scale_question(document_id: int, story_name: str):
    if document_id in [0, 1, 2]:
        q = f"In hoeverre was je bekend met het sprookje {story_name} dat werd verteld in de vorige tekst?"
    elif document_id in [5, 6]:
        q = f"In hoeverre was je bekend met de roman/film {story_name} waarover werd verteld in de vorige tekst?"
    elif document_id in [3, 4, 7, 8, 9, 10]:
        q = "In hoeverre was je bekend met het onderwerp van de vorige tekst?"
    return q
