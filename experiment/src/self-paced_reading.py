"""
Self-paced reading experiment
"""

import os, json
import re
import argparse
import pandas as pd
from random import shuffle
from util import read_text, get_n_session, get_finished_texts, send_eeg_trigger
from show_stim import show_text_from_path, show_text
from experiment_questionnaire import exp_questionnaire
from reading_funcs import spr_w_questions, rsvp_w_questions
from config import exp_config, exp_paths


def experiment(
    paths: dict,
    times: dict,
    keys: str,
    eeg: bool,
    fullscreen: bool,
):
    # for saving data
    if not os.path.exists(paths["out_data"]):
        os.makedirs(paths["out_data"])

    # questions
    questions_df = pd.read_excel(paths["questions"])
    questions_df["story"] = questions_df["Story"].apply(
        lambda s: re.sub("[^a-zA-Z\s]+", "", s).lower().replace(" practice text", "")
    )
    doc_ids = pd.Series(
        questions_df.document_id.values, index=questions_df.story
    ).to_dict()
    text_types = pd.Series(
        questions_df.text_type.values, index=questions_df.story
    ).to_dict()

    # GUI information
    gui_information, tmp_file = exp_questionnaire(paths["out_data"], exp="spr")
    cont_crash = True if tmp_file else None

    if tmp_file:
        tmp_subfix = tmp_file["participant_subfix"].replace("_s1", "")
        n_session = get_n_session(
            out_path=paths["out_data"], filename=f"rt_{tmp_subfix}*.csv"
        )
        participant_subfix = f"{tmp_subfix}_s{n_session}"
    else:
        participant_subfix = gui_information["participant_subfix"]
        tmp_subfix = participant_subfix

    # config
    config = exp_config(
        fullscreen, keys, hand_condition=gui_information["hand"], eeg=eeg
    )
    full_paths = exp_paths(
        paths,
        experiment="spr",
        save_subfix=participant_subfix,
        tmp_subfix=tmp_subfix,
        hand_condition=gui_information["hand"],
    )

    # read in stories
    if cont_crash:
        stories = tmp_file["stories"]
        n_stories = len(stories)
        finished_texts = get_finished_texts(paths["out_data"], f"rt_{tmp_subfix}*.csv")
    else:
        stories = list(
            read_text(
                full_paths.stories,
                stories=True,
                ignore_paths=[
                    full_paths.practice_text_rsvp,
                    full_paths.practice_text_spr,
                ],
            )
        )
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
        show_text_from_path(full_paths.inst, config, align_text="left")

    # experiment start
    spr_practice = False if cont_crash else True
    send_eeg_trigger(config, config.trigger_exp_start, reset=True)
    for n, (story_name, story) in enumerate(stories, start=1):
        if cont_crash and story_name in finished_texts:
            continue

        document_id = doc_ids[story_name]
        inst_path = (
            full_paths.rsvp_inst
            if document_id == gui_information["rsvp_document_id"]
            else full_paths.spr_inst
        )
        show_text_from_path(inst_path, config, align_text="left")

        if document_id == gui_information["rsvp_document_id"]:
            # practice
            show_text_from_path(full_paths.practice_info, config)
            rsvp_w_questions(
                story=practice_story["rsvp"],
                story_name="practice story jorinde en joringel",
                document_id=12,
                text_type=text_types["jorinde en joringel"],
                questions_df=questions_df,
                config=config,
                times=times,
                full_paths=full_paths,
                extra_cols=gui_information,
            )
            show_text_from_path(full_paths.practice_end, config)

            # experimental text
            show_text(
                f"{story_name.title()}\n\nTekst {n} van {n_stories}",
                config.text_stim,
                config.win,
                config.escape_keys,
                config.show_text_ending,
            )
            rsvp_w_questions(
                story=story,
                story_name=story_name,
                document_id=document_id,
                text_type=text_types[story_name.replace("practice story ", "")],
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
                    story_name="practice story de uil",
                    document_id=11,
                    text_type=text_types["de uil"],
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
                f"{story_name.title()}\n\nTekst {n} van {n_stories}",
                config.text_stim,
                config.win,
                config.escape_keys,
                config.show_text_ending,
            )
            spr_w_questions(
                story=story,
                story_name=story_name,
                document_id=document_id,
                text_type=text_types[story_name.replace("practice story ", "")],
                questions_df=questions_df,
                config=config,
                times=times,
                full_paths=full_paths,
                extra_cols=gui_information,
            )

        # pause
        send_eeg_trigger(config, config.trigger_pause, reset=True)
        show_text_from_path(full_paths.pause, config)

    # show ending
    show_text_from_path(full_paths.end, config, align_text="left")

    # remove tmp file
    os.remove(full_paths.tmp_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--fullscreen", dest="fullscreen", action="store_true")
    parser.add_argument("--no-fullscreen", dest="fullscreen", action="store_false")
    parser.add_argument("--eeg", dest="eeg", action="store_true")
    parser.add_argument("--no-eeg", dest="eeg", action="store_false")
    parser.set_defaults(fullscreen=True, eeg=True)
    parser.add_argument("--keys", type=str, required=False, default="computer")
    args = parser.parse_args()
    print(args)

    # paths
    paths = {
        "instructions": os.path.join("instructions"),
        "stories": os.path.join("..", "texts", "edited"),
        "questions": os.path.join("questions.xlsx"),
        "out_data": os.path.join("data", "spr"),
    }

    # experimental times (in sec)
    times = {
        "fixation": 0.5,
        "blackscreen_short": 0.2,
        "blackscreen_long": 0.75,
        "rsvp_pr_char": 0.19,
        "rsvp_min": 0.25,
    }

    # experimental device
    fullscreen = args.fullscreen
    keys = args.keys.lower()
    eeg = args.eeg

    experiment(paths=paths, times=times, keys=keys, eeg=eeg, fullscreen=fullscreen)
