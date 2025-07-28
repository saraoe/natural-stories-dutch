"""
Make a df with all words in the corpus
"""

from pathlib import Path
import re
import pandas as pd


def get_name_from_path(path: str):
    name = path.parts[-1]
    name = name.replace("_", " ")
    name = name.replace("txt", "")
    name = re.sub(r"[^\w\s]", "", name)
    return name


def read_texts(path: Path):
    text_paths = sorted(path.glob("*.txt"))
    for text_path in text_paths:
        f = open(text_path, "r", encoding="utf8")
        text = f.read()
        text_name = get_name_from_path(text_path)
        yield text_name, text


def fix_filename(file_name: str):
    file_name = re.sub("texts", "", file_name)
    file_name = re.sub("txt", "", file_name)
    file_name = re.sub(r"[\s]", "_", file_name)
    file_name = re.sub(r"[^_\w]", "", file_name)
    file_name = re.sub("_", " ", file_name)
    file_name = file_name.lower()
    return file_name


def create_word_df(stories_path: Path, index_path: Path, df_path: Path):
    df_list = []

    # get document ids
    stories_index = pd.read_excel(index_path)
    stories_index["file_name"] = [
        fix_filename(filename) for filename in stories_index["Filename"]
    ]
    doc_ids = stories_index.set_index("file_name").to_dict()["id"]

    for story_name, story in read_texts(stories_path):
        print(story_name)

        paragraphs = re.split("\n\n", story)
        for m, paragraph in enumerate(paragraphs):
            words = re.split(r"[\s]", paragraph)
            for n, word in enumerate(words):
                if not word:  # if word is an empty str
                    continue

                df_list.append(
                    {
                        "story_name": story_name,
                        "document_id": int(doc_ids[story_name]),
                        "word": word,
                        "word_n": n,
                        "paragraph_n": m,
                    }
                )

    df = pd.DataFrame(df_list, index=range(len(df_list)))
    df = df.sort_values(by=["document_id", "paragraph_n", "word_n"])
    df.to_csv(df_path / "words_corpus.csv", index=None)


if __name__ == "__main__":
    stories_path = Path("texts", "edited")
    index_path = Path("data", "stories_index.xlsx")
    df_path = Path("data")
    create_word_df(stories_path, index_path, df_path)
