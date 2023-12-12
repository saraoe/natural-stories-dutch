"""
Cloze task
"""

from psychopy import data
import os, re
from random import shuffle
import pandas as pd
from util import read_text
from show_stim import show_text, show_text_from_path, make_gui
from reading_funcs import cloze_task, cloze_scale_question
from config import exp_config, exp_paths


def experiment(paths: dict, fullscreen: bool):
    # get document_ids
    questions_df = pd.read_excel(paths["questions"])
    questions_df["story"] = questions_df["Story"].apply(
        lambda s: re.sub("[^a-zA-Z\s]+", "", s).lower()
    )
    doc_ids = pd.Series(
        questions_df.document_id.values, index=questions_df.story
    ).to_dict()

    # GUI information
    fields = {
        "Participant ID": None,
        "Age": None,
        "Gender": ["Female", "Male", "Other"],
    }
    gui_information = make_gui(fields, title="Cloze Task")

    # for saving data
    if not os.path.exists(paths["out_data"]):
        os.makedirs(paths["out_data"])

    date = data.getDateStr()
    participant_subfix = f"{gui_information['participant_id']}_{date}"

    # defining a window
    config = exp_config(fullscreen, keys="computer", cloze=True)
    full_paths = exp_paths(paths, experiment="cloze", save_subfix=participant_subfix)

    # read in stories
    stories = list(read_text(full_paths.stories, stories=True))
    shuffle(stories)
    n_stories = len(stories)
    practice_story = list(read_text(full_paths.practice_text))[0]
    stories = [("practice story", practice_story)] + stories

    # show instruction:
    show_text_from_path(full_paths.inst, config)

    # start experiment
    for n, (story_name, story) in enumerate(stories):
        if n == 0:  # practice text
            show_text_from_path(full_paths.practice_info, config)
            document_id = 0
        else:
            show_text(
                f"{story_name.title()}\n\nStory {n} out of {n_stories}",
                config.text_stim,
                config.win,
                config.escape_keys,
            )
            document_id = doc_ids[story_name]

        cloze_task(
            story,
            document_id,
            config,
            save_path=full_paths.save_cloze,
            extra_cols=gui_information,
        )

        cloze_scale_question(
            document_id=document_id,
            story_name=story_name,
            config=config,
            save_path=full_paths.save_responses,
            extra_cols=gui_information,
        )

        if n == 0:
            # practice end
            show_text_from_path(full_paths.practice_end, config)
        else:
            # pause
            show_text_from_path(full_paths.pause, config)

    # show ending
    show_text_from_path(full_paths.end, config)


if __name__ == "__main__":
    # paths
    paths = {
        "questions": os.path.join("questions.xlsx"),
        "instructions": os.path.join("instructions"),
        "stories": os.path.join("..", "texts", "edited", "*"),
        "out_data": os.path.join("data", "cloze"),
    }

    # experimental setup
    fullscreen = False

    experiment(paths, fullscreen)
