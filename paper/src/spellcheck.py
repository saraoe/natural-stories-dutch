"""
Automatic spell check of cloze responses
"""

import os
from glob import glob
import pandas as pd
from spellchecker import SpellChecker


def main(
    cloze_path: str,
    out_folder: str = "data/cloze/spell_checked",
    word_col: str = "correct_word",
    response_col: str = "response",
    index_col: str = "story_name",
):
    df = pd.read_csv(cloze_path)
    df = df[[word_col, response_col, index_col]]

    spell = SpellChecker(language="nl")

    responses = df[response_col]
    df["corrected_word"] = [
        spell.correction(response) if not isinstance(response, float) else response
        for response in responses
    ]
    df["auto_corrected"] = df[response_col] != df["corrected_word"]
    df.to_excel(os.path.join(out_folder, f"{os.path.basename(file)[12:-4]}.xlsx"))


if __name__ == "__main__":
    for file in glob(os.path.join("data", "cloze", "cloze_*.csv")):
        print(file)
        main(file)
