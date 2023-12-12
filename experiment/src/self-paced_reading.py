"""
Self-paced reading experiment
"""

from psychopy import data
import os, json
import re
import pandas as pd
from random import shuffle
from util import read_text
from show_stim import show_text_from_path, show_text
from experiment_questionnaire import exp_questionnaire
from reading_funcs import spr_w_questions, rsvp_w_questions
from config import exp_config, exp_paths


def experiment(
    paths: dict,
    times: dict,
    keys: str,
    fullscreen: bool = True,
):
    # questions
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

    # for saving data
    if not os.path.exists(paths["out_data"]):
        os.makedirs(paths["out_data"])

    if tmp_file:
        old_participant_subfix = tmp_file["participant_subfix"]
        participant_subfix = old_participant_subfix + "_s2"
    else:
        participant_subfix = gui_information["participant_subfix"]

    # config
    config = exp_config(fullscreen, keys)
    full_paths = exp_paths(paths, experiment="spr", save_subfix=participant_subfix)

    # read in stories
    if cont_crash:
        stories = tmp_file["stories"]
        n_stories = len(stories)
        finished_texts = pd.read_csv(
            os.path.join(paths["out_data"], f"rt_{old_participant_subfix}.csv")
        )["story_name"].unique()
    else:
        stories = list(read_text(full_paths.stories, stories=True))
        shuffle(stories)
        n_stories = len(stories)

    practice_story = {}
    for reading_task, path in zip(
        ["spr", "rsvp"], [full_paths.practice_text_spr, full_paths.practice_text_rsvp]
    ):
        practice_story[reading_task] = list(read_text(path))[0]

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
        show_text_from_path(full_paths.inst_path, config)

    # experiment start
    spr_practice = False if cont_crash else True
    for n, (story_name, story) in enumerate(stories, start=1):
        if cont_crash and story_name in finished_texts:
            continue

        document_id = doc_ids[story_name]
        inst_path = (
            full_paths.rsvp_inst
            if document_id == gui_information["rsvp_document_id"]
            else full_paths.spr_inst
        )
        show_text_from_path(inst_path, config)

        if document_id == gui_information["rsvp_document_id"]:
            # practice
            show_text_from_path(full_paths.practice_info)
            rsvp_w_questions(
                story=practice_story["rsvp"],
                story_name="practice story rsvp",
                document_id=0,
                questions_df=questions_df,
                config=config,
                times=times,
                full_paths=full_paths,
                extra_cols=gui_information,
            )
            show_text_from_path(full_paths.practice_end)

            # experimental text
            show_text(
                f"{story_name.title()}\n\nStory {n} out of {n_stories}",
                config.text_stim,
                config.win,
                config.escape_keys,
            )
            rsvp_w_questions(
                story=story,
                story_name=story_name,
                document_id=document_id,
                questions_df=questions_df,
                config=config,
                times=times,
                full_paths=full_paths,
                extra_cols=gui_information,
            )
        else:
            # practice
            if spr_practice:
                show_text_from_path(full_paths.practice_info, config)
                spr_w_questions(
                    story=practice_story["spr"],
                    story_name="practice story spr",
                    document_id=0,
                    questions_df=questions_df,
                    config=config,
                    times=times,
                    full_paths=full_paths,
                    extra_cols=gui_information,
                )
                show_text_from_path(full_paths.practice_end, config)

                spr_practice = None  # only practice first time

            # experimental text
            show_text(
                f"{story_name.title()}\n\nStory {n} out of {n_stories}",
                config.text_stim,
                config.win,
                config.escape_keys,
            )
            spr_w_questions(
                story=story,
                story_name=story_name,
                document_id=document_id,
                questions_df=questions_df,
                config=config,
                times=times,
                full_paths=full_paths,
                extra_cols=gui_information,
            )

        # pause
        show_text_from_path(full_paths.pause, config)

    # show ending
    show_text_from_path(full_paths.end, config)

    # remove tmp file
    os.remove(full_paths.tmp_path)


if __name__ == "__main__":
    # paths
    paths = {
        "instructions": os.path.join("instructions"),
        "stories": os.path.join("..", "texts", "edited", "*"),
        "questions": os.path.join("questions.xlsx"),
        "out_data": os.path.join("data", "spr"),
    }

    # experimental times (in sec)
    times = {
        "fixation": 0.5,
        "blackscreen_short": 0.2,
        "blackscreen_long": 0.75,
        "rsvp_prchar": 0.19,
        "rsvp_min": 0.25,
    }

    # experimental device
    keys = "computer"
    fullscreen = False

    experiment(
        paths,
        times,
        keys,
        fullscreen,
    )
