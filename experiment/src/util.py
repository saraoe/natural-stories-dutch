"""
Util functions
"""
import re
from glob import glob
import pandas as pd
from typing import List


def get_name_from_path(path: str):
    path = path.replace("_", " ")
    path = path.replace("texts", "")
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


def list_to_csv(df_list: List[dict], out_path: str, extra_cols: dict = {}):
    df = pd.DataFrame(df_list, index=range(len(df_list)))
    for name, values in extra_cols.items():
        df[name] = values
    df.to_csv(out_path)
