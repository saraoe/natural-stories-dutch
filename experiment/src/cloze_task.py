"""
Cloze task
"""

import os, re, json
from random import shuffle
import pandas as pd
from util import read_text, get_n_session, get_finished_texts
from show_stim import show_text, show_text_from_path
from experiment_questionnaire import exp_questionnaire
from reading_funcs import cloze_task, cloze_scale_question
from config import exp_config, exp_paths


def experiment(paths: dict, fullscreen: bool):
    # for saving data
    if not os.path.exists(paths["out_data"]):
        os.makedirs(paths["out_data"])

    # get document_ids
    questions_df = pd.read_excel(paths["questions"])
    questions_df["story"] = questions_df["Story"].apply(
        lambda s: re.sub("[^a-zA-Z\s]+", "", s).lower()
    )
    doc_ids = pd.Series(
        questions_df.document_id.values, index=questions_df.story
    ).to_dict()

    # GUI information
    gui_information, tmp_file = exp_questionnaire(paths["out_data"])
    cont_crash = True if tmp_file else None

    if tmp_file:
        tmp_subfix = tmp_file["participant_subfix"]
        n_session = get_n_session(
            out_path=paths["out_data"], filename=f"cloze_{tmp_subfix}*.csv"
        )
        participant_subfix = f"{tmp_subfix}_s{n_session}"
    else:
        participant_subfix = gui_information["participant_subfix"]
        tmp_subfix = participant_subfix

    # defining a window
    config = exp_config(fullscreen, keys="computer", cloze=True)
    full_paths = exp_paths(
        paths, experiment="cloze", save_subfix=participant_subfix, tmp_subfix=tmp_subfix
    )

    # read in stories
    if cont_crash:
        stories = tmp_file["stories"]
        n_stories = len(stories)
        finished_texts = get_finished_texts(
            paths["out_data"], f"cloze_{tmp_subfix}*.csv"
        )
    else:
        stories = list(
            read_text(
                full_paths.stories,
                stories=True,
                ignore_paths=[full_paths.practice_text],
            )
        )
        shuffle(stories)
        n_stories = len(stories)
        practice_story = list(read_text(full_paths.practice_text))[0]
        # only use two first sentences for practice
        practice_story = ".".join(practice_story.split(".")[:2]) + "."
        stories = [("practice story de uil", practice_story)] + stories

    # save info in tmp file
    if not cont_crash:
        tmp_info = {
            "gui_information": gui_information,
            "stories": stories,
            "participant_subfix": participant_subfix,
        }
        with open(full_paths.tmp_path, "w") as fp:
            json.dump(tmp_info, fp)

    # show instruction:
    if not cont_crash:
        show_text_from_path(full_paths.inst, config)

    # start experiment
    for n, (story_name, story) in enumerate(stories):
        if cont_crash and story_name in finished_texts:
            continue

        if n == 0:  # practice text
            show_text_from_path(full_paths.practice_info, config)
            document_id = 11
        else:
            show_text(
                f"{story_name.title()}\n\nStory {n} out of {n_stories}",
                config.text_stim,
                config.win,
                config.escape_keys,
                config.show_text_ending,
            )
            document_id = doc_ids[story_name]

        cloze_task(
            story=story,
            story_name=story_name,
            document_id=document_id,
            config=config,
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
        "stories": os.path.join("..", "texts", "edited"),
        "out_data": os.path.join("data", "cloze"),
    }

    # experimental setup
    fullscreen = False

    experiment(paths, fullscreen)
