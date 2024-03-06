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


def read_text(path: str, stories: bool = False, ignore_paths: List[str] = []):
    text_paths = glob(path)
    text_paths.sort()
    for text_path in text_paths:
        if text_path in ignore_paths:
            continue
        f = open(text_path, "r", encoding="utf8")
        text = f.read()
        if stories:
            text_name = get_name_from_path(text_path)
            yield text_name, text
        else:
            yield text


def get_n_session(out_path: str, filename: str):
    try:
        all_files = glob(os.path.join(out_path, filename))
        all_files.sort()
        latest_file = all_files[-1]
        return int(latest_file.split(".")[-2][-1]) + 1
    except IndexError:
        return 1


def story_name_from_id(doc_ids: dict, doc_id):
    return list(doc_ids.keys())[list(doc_ids.values()).index(doc_id)]


def get_finished_texts(out_path: str, filename: str):
    finished_texts = []
    for file in glob(os.path.join(out_path, filename)):
        finished_texts += [t for t in pd.read_csv(file)["story_name"].unique()]
    return finished_texts


def list_to_csv(df_list: List[dict], out_path: str, extra_cols: dict = {}):
    df = pd.DataFrame(df_list, index=range(len(df_list)))
    for name, values in extra_cols.items():
        df[name] = values
    df.to_csv(out_path, mode="a", header=not os.path.exists(out_path))


def get_scale_question(story_name: str, text_type: str):
    story_name = story_name.replace("practice story ", "")
    story_name = story_name.title()
    if text_type == "fairy tale":
        q = f"In hoeverre was je bekend met het sprookje {story_name} dat werd verteld in de vorige tekst?"
    elif text_type in ["novel", "synopsis show"]:
        q = f"In hoeverre was je bekend met de roman/film {story_name} waarover werd verteld in de vorige tekst?"
    elif text_type in ["technical text", "history"]:
        q = "In hoeverre was je bekend met het onderwerp van de vorige tekst?"
    return q


def get_punct_dict():
    key_punct = {
        "period": ".",
        "comma": ",",
        "minus": "-",
        "slash": "/",
        "semicolon": ";",
        "1": "!",
    }
    shift_punct = {
        "slash": "?",
        "1": "!",
        "semicolon": ":",
        "9": "(",
        "0": ")",
        "minus": "_",
    }
    return key_punct, shift_punct


def remove_font(line: str):
    return re.sub(r"</?[a-z]>", "", line)


def add_word(current_text: str, word: str, last_word_font: str = "i"):
    current_text = remove_font(current_text)
    text = current_text + f"<{last_word_font}>{word}</{last_word_font}> "
    return text


def send_eeg_trigger(eeg, eeg_trigger: str):
    if eeg:
        pass
    else:
        print(eeg_trigger)
