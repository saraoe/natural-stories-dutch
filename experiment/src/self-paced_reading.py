"""
Self-paced reading experiment
"""

from psychopy import visual, core
import os
import pandas as pd
from read_txt import read_text
from show_stim import (
    show_fixation,
    show_text,
    show_word,
    show_blackscreen,
    show_questions,
)


def experiment(paths: dict, fixation_time: int, blackscreen_time: int):
    stopwatch = core.Clock()

    # empty dfs
    rt_df = pd.DataFrame()
    responses = []

    # questions
    questions_df = pd.read_excel(paths["questions"])

    # GUI information

    # defining a window
    win = visual.Window(color="black", fullscr=False)
    text_stim = visual.TextStim(win=win)
    fix_cross = visual.TextStim(win=win, text="+", alignText="center")

    # show instruction:
    for instruction in read_text(paths["instruction"]):
        show_text(instruction, text_stim, win)

    # experiment start
    for story_name, story in read_text(paths["stories"], stories=True):
        show_fixation(fix_cross, win, sec=fixation_time)
        show_text(story_name, text_stim, win)

        paragraphs = story.split("\n\n")

        for paragraph in paragraphs:
            show_fixation(fix_cross, win, sec=fixation_time)
            words = paragraph.split(" ")
            for word in words:
                rt = show_word(word, text_stim, win, stopwatch)
                rt_df = rt_df.append(
                    {"reation_time": rt, "story": story_name, "word": word},
                    ignore_index=True,
                )

                show_blackscreen(win, sec=blackscreen_time)

        # questions
        document_id = 1  # fix this!
        qs = questions_df[questions_df["document_id"] == document_id]
        tmp_responses = show_questions(qs, text_stim, win)
        responses += tmp_responses

    # show ending
    for end in read_text(paths["end"]):
        show_text(end, text_stim, win)

    # saving data
    if not os.path.exists(paths["out_data"]):
        os.makedirs(paths["out_data"])
    rt_df.to_csv(os.path.join(paths["out_data"], "rt.csv"))  # change path!
    responses_df = pd.DataFrame(responses, index=range(len(responses)))
    responses_df.to_csv(
        os.path.join(paths["out_data"], "responses.csv")
    )  # change path!


if __name__ == "__main__":
    # paths
    paths = {
        "instruction": os.path.join("..", "instructions", "instruction*.txt"),
        "end": os.path.join("..", "instructions", "end.txt"),
        "stories": os.path.join("..", "..", "texts", "*"),
        "questions": os.path.join("..", "questions.xlsx"),
        "out_data": os.path.join("..", "data"),
    }

    # experimental parameters
    fixation_time = 0.5
    blackscreen_time = 0.2

    experiment(paths, fixation_time, blackscreen_time)
