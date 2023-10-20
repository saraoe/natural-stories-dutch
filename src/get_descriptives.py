"""
Summary of syntactic and semantic proporties of texts in the corpus
"""

from glob import glob
from collections import Counter
import spacy
import re
import textdescriptives
import pandas as pd
import numpy as np

nlp = spacy.load("nl_core_news_sm")
nlp.add_pipe("textdescriptives/all")


def read_texts(path: str):
    for text_path in glob(path):
        f = open(text_path, "r", encoding="utf8")
        text = f.read()
        yield text_path, text


def fix_filename(filename: str):
    filename = re.sub("\s", "_", filename)
    filename = re.sub("[^_]\W", "", filename)
    filename = filename.lower()
    return filename


def fix_types(text_type: list):
    text_type = text_type.lower()
    if text_type[-1] == " ":
        return text_type[:-1]
    return text_type


def filter_tokens(doc):
    filtered_tokens = [
        word.lower for word in doc if not word.is_punct and "'" not in word.text
    ]
    return filtered_tokens


def max_dependency_depth(token, max_depth: int = 1):
    children = [child for child in token.children]
    if len(children) == 0:
        return max_depth
    return max([max_dependency_depth(child) for child in children]) + max_depth


def max_depth_from_root(sent):
    for token in sent:
        if token.dep_ == "ROOT":
            return max_dependency_depth(token)
    return 0


def rare_token_corpus(
    token_counter: Counter, tokens_in_doc: dict, n_appearance: int = 1
):
    rare_tokens = [
        token for token, count in token_counter.items() if count <= n_appearance
    ]
    for tokens in tokens_in_doc.values():
        yield sum([1 for token in tokens if token in rare_tokens])


def main(path: str):
    descriptives_list = []
    token_counter = Counter()
    tokens_in_doc = {}
    for text_path, text in read_texts(path):
        doc = nlp(text)
        # from td
        counts = doc._.counts
        token_length = doc._.token_length
        sentence_length = doc._.sentence_length
        dependency_distance = doc._.dependency_distance
        tmp = {
            **counts,
            **token_length,
            **sentence_length,
            **dependency_distance,
        }

        # other descriptive measures
        tmp["type_token_ratio"] = tmp["n_unique_tokens"] / tmp["n_tokens"]
        max_depth_sents = [max_depth_from_root(sent) for sent in doc.sents]
        tmp["dependency_depth_mean"] = np.mean(max_depth_sents)
        tmp["dependency_depth_std"] = np.std(max_depth_sents)

        # add file_name
        tmp["file_name"] = fix_filename(text_path[6:-4])

        tokens_in_doc[tmp["file_name"]] = filter_tokens(doc)
        token_counter = token_counter + Counter(
            [token for token in tokens_in_doc[tmp["file_name"]]]
        )

        descriptives_list.append(tmp)
    descriptives = pd.DataFrame(descriptives_list, index=range(len(descriptives_list)))

    descriptives["n_tokens_once_in_courpus"] = list(
        rare_token_corpus(token_counter, tokens_in_doc)
    )

    # add type of text
    stories_index = pd.read_csv("stories_index.csv")
    stories_index["file_name"] = [
        fix_filename(filename) for filename in stories_index["Filename"]
    ]
    stories_index["text_type"] = [
        fix_types(text_type) for text_type in stories_index["Type of text"]
    ]
    relevant_index = stories_index[["text_type", "file_name", "Number"]]
    descriptives = descriptives.merge(relevant_index, how="left", on="file_name")

    # save df
    descriptives.to_csv("../data/corpus_descriptives.csv")


if __name__ == "__main__":
    path = "../texts/*.txt"
    main(path)
