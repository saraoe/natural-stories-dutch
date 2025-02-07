"""
Part of speech (pos) tags of words in corpus
"""

import spacy
import pandas as pd
import os
import re

nlp = spacy.load("nl_core_news_sm")


def get_pos(word):
    if not word:
        return None

    doc = nlp(word)
    assert len([t for t in doc]) == 1  # check there is ony one token
    return doc[0].pos_


def main(df: pd.DataFrame, out_path: str):
    df["word_rm_punct"] = df["word"].apply(lambda w: re.sub(r"\W", "", w.lower()))
    df["pos"] = df["word_rm_punct"].apply(get_pos)
    df.to_csv(out_path)


if __name__ == "__main__":
<<<<<<< HEAD:paper/src/stim_pos.py
    filepath = os.path.join("..", "data", "words_corpus.csv")
=======
    filepath = os.path.join("data", "words_corpus.csv")
>>>>>>> 3ef51f6f63a4459b202de4521680eed53fc6fafa:src/stim_pos.py
    stim_df = pd.read_csv(filepath, index_col=[0])

    main(stim_df, out_path=filepath)
