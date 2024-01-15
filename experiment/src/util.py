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
    for text_path in glob(path):
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
    latest_file = glob(os.path.join(out_path, filename))[-1]
    return int(latest_file.split(".")[-2][-1]) + 1


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


def get_scale_question(document_id: int, story_name: str):
    story_name = story_name.replace("practice text", "")
    if document_id in [1, 2, 11, 12]:
        q = f"In hoeverre was je bekend met het sprookje {story_name} dat werd verteld in de vorige tekst?"
    elif document_id in [5, 6]:
        q = f"In hoeverre was je bekend met de roman/film {story_name} waarover werd verteld in de vorige tekst?"
    elif document_id in [3, 4, 7, 8, 9, 10]:
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


def make_lines(current_lines: List[str], word: str, maxchar: int):
    line = current_lines[-1]
    tmp_line = line + f" {word}"
    if len(tmp_line) > maxchar:
        lines = current_lines + [word]
    else:
        lines = current_lines[:-1] + [tmp_line]
    return lines


def key_scroll(scroll: int, key: str, max_lines: int, n_lines: int):
    if key == "up":
        scroll -= 1
        if scroll < 0:
            scroll = 0
    if key == "down":
        scroll += 1
        if max_lines + scroll > n_lines:
            scroll = n_lines - max_lines
    return scroll


def send_eeg_trigger(eeg_trigger: str):
    print(eeg_trigger)
