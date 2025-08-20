"""
Cloze values from BLOOM 
"""

from transformers import BloomTokenizerFast, BloomForCausalLM
import torch
import spacy
import pandas as pd
from math import log
from get_descriptives import read_texts, fix_filename


class BloomHeadModel:
    """
    class (slightly modified to fit with Bloom) from https://stackoverflow.com/questions/76397904/generate-the-probabilities-of-all-the-next-possible-word-for-a-given-text
    """

    def __init__(self, model_name):
        # Initialize the model and the tokenizer.
        self.model = BloomForCausalLM.from_pretrained(model_name)
        self.tokenizer = BloomTokenizerFast.from_pretrained(model_name)

    def get_predictions(self, sentence):
        # Encode the sentence using the tokenizer and return the model predictions.
        inputs = self.tokenizer.encode(sentence, return_tensors="pt")
        with torch.no_grad():
            outputs = self.model(inputs)
            predictions = outputs[0]
        return predictions

    def get_next_word_probabilities_top(self, sentence, top_k=500):
        # Get the model predictions for the sentence.
        predictions = self.get_predictions(sentence)

        # Get the next token candidates.
        next_token_candidates_tensor = predictions[0, -1, :]

        # Get the top k next token candidates.
        topk_candidates_indexes = torch.topk(
            next_token_candidates_tensor, top_k
        ).indices.tolist()

        # Get the token probabilities for all candidates.
        all_candidates_probabilities = torch.nn.functional.softmax(
            next_token_candidates_tensor, dim=-1
        )

        # Filter the token probabilities for the top k candidates.
        topk_candidates_probabilities = all_candidates_probabilities[
            topk_candidates_indexes
        ].tolist()

        # Decode the top k candidates back to words.
        topk_candidates_tokens = [
            self.tokenizer.decode([idx]).strip() for idx in topk_candidates_indexes
        ]

        # Return the top k candidates and their probabilities.
        return list(zip(topk_candidates_tokens, topk_candidates_probabilities))

    def get_next_word_probabilities_word(self, sentence, word):
        # Get the model predictions for the sentence.
        predictions = self.get_predictions(sentence)

        # Get the next token candidates.
        next_token_candidates_tensor = predictions[0, -1, :]

        # Get the token probabilities for all candidates.
        all_candidates_probabilities = torch.nn.functional.softmax(
            next_token_candidates_tensor, dim=-1
        )

        # encode word
        encoded_word = self.tokenizer.encode(word)

        # Filter the token probabilities for the top k candidates.
        word_probability = all_candidates_probabilities[encoded_word].tolist()[0]

        # Return the top k candidates and their probabilities.
        return word_probability


def main(text_path: str, out_path: str, include_only: list = None):
    model = BloomHeadModel("bigscience/bloom-560m")
    nlp = spacy.load("nl_core_news_sm")

    df_list = []
    for name, text in read_texts(text_path):
        if include_only:
            if fix_filename(name) not in text_names:
                continue

        print(f"working on file: {name}")
        doc = nlp(text)

        sentences = doc.sents
        for n, sentence in enumerate(sentences, start=1):
            print(f"starting sentence {n}")

            prompt = ""  # init prompt
            for token in sentence:
                if prompt == "":
                    prompt += token.text
                    continue

                prob = model.get_next_word_probabilities_word(prompt, token.text)
                tmp = {
                    "file_name": fix_filename(name),
                    "n_sentence": n,
                    "token": token.text,
                    "probability": prob,
                    "surprisal": -log(prob),
                }
                df_list.append(tmp)

                prompt += token.text  # update prompt for next word

    df = pd.DataFrame(df_list, index=range(len(df_list)))
    df.to_csv(out_path)


if __name__ == "__main__":
    text_path = "texts/*"
    out_path = "data/cloze.csv"

    # only use relevant texts
    text_names = [
        "mijn_heer_zak_met_rijst",
        "waarom_de_reuzen_in_limburg_zijn_uitgestorven",
        "de_eerste_opiumoorlog",
        "aspasia",
        "de_zilveren_schaatsen",
        "carrie",
        "permafrost",
        "nomadisch_pastoralisme",
        "kieming",
        "vleermuizen",
    ]

    main(text_path, out_path, include_only=text_names)
