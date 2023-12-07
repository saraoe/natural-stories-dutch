"""
Self-paced reading experiment
"""

from psychopy import visual, core, data
import os, glob, json
import re
import pandas as pd
from random import shuffle
from util import read_text, get_scale_question, list_to_csv
from reading_funcs import spr, rsvp
from show_stim import (
    show_text,
    show_questions,
    show_scale,
    make_gui,
)


def text_questions(
    story_name,
    document_id,
    questions_df,
    win,
    respond_key,
    escape_keys,
    question_keys,
    save_path,
    extra_cols,
):
    # define stim
    qtext_up = visual.TextStim(win=win)
    respond_stim = visual.TextStim(
        win=win, pos=(0, -0.8), text=f"Press {respond_key} to respond"
    )
    scale = visual.Slider(
        win=win,
        font="Open Sans",
        labelHeight=0.05,
        ticks=(1, 2, 3, 4, 5),
        labels=[
            "1\nIk heb er nog nooit van gehoord",
            "2\nIk ben er een heel klein beetje bekend meel",
            "3\nIk ben er tot op zekere hoogte bekend mee",
            "4\nIk ben er bekend mee",
            "5\nIk ben er heel bekend mee",
        ],
    )
    scale_keys = [str(tick) for tick in scale.ticks]
    scale_keys.append(respond_key)

    scale_question = get_scale_question(document_id, story_name)
    scale_response = show_scale(
        scale_question,
        qtext_stim=qtext_up,
        respondtext=respond_stim,
        scale_stim=scale,
        win=win,
        escape_keys=escape_keys,
        question_keys=scale_keys,
    )
    list_to_csv(
        df_list=[
            {
                "response": scale_response,
                "correct": "NA",
                "document_id": document_id,
                "question_id": 0,
            }
        ],
        out_path=save_path,
        extra_cols=extra_cols,
    )
    qs = questions_df[questions_df["document_id"] == document_id]
    q_responses = show_questions(
        qs,
        qtext_up,
        respond_stim,
        win,
        escape_keys,
        question_keys,
        save_path=save_path,
        extra_cols=extra_cols,
    )
    list_to_csv(df_list=q_responses, out_path=save_path, extra_cols=extra_cols)


def experiment(
    paths: dict,
    times: dict,
    keys: str,
    fullscreen: bool = True,
):
    stopwatch = core.Clock()
    cont_crash = None

    if keys == "computer":
        respond_key = "return"
        escape_keys = ["escape", "q"]
        question_keys = ["1", "2", "3", "4"]
        question_keys.append(respond_key)

    # questions
    questions_df = pd.read_excel(paths["questions"])
    questions_df["story"] = questions_df["Story"].apply(
        lambda s: re.sub("[^a-zA-Z\s]+", "", s).lower()
    )
    doc_ids = pd.Series(
        questions_df.document_id.values, index=questions_df.story
    ).to_dict()

    # GUI information
    participant_id = make_gui(
        {
            "Participant ID": None,
        },
        title="Self-Paced Reading",
    )["participant_id"]

    # check if tmp-file for participant exists
    tmp_path = glob.glob(os.path.join(paths["out_data"], f"tmp_{participant_id}*.json"))
    if tmp_path:
        ans = list(
            make_gui(
                {
                    "Do you want to jump into experiment,\n where you ended?": [
                        "yes",
                        "no",
                    ]
                },
                title="Self-Paced Reading",
            ).values()
        )[0]
        cont_crash = True if ans == "yes" else None
        tmp_path = tmp_path[0]

    if cont_crash:
        with open(tmp_path) as f:
            tmp_file = json.load(f)
        gui_information = tmp_file["gui_information"]
    else:
        fields = {
            "Age": None,
            "Gender": ["Female", "Male", "Other"],
            "Hand": ["Left", "Right"],
            "Condition": [1, 2],
        }
        gui_information = make_gui(fields, title="Self-Paced Reading")
        gui_information["participant_id"] = participant_id
    rsvp_text = 1 if gui_information["condition"] == 1 else 7

    # for saving data
    if not os.path.exists(paths["out_data"]):
        os.makedirs(paths["out_data"])

    if cont_crash:
        file_end = old_file_end + "_s2"
    else:
        date = data.getDateStr()
        file_end = f"{gui_information['participant_id']}_{date}"

    # defining a window
    win = visual.Window(color="grey", fullscr=fullscreen)
    text_stim = visual.TextStim(win=win)
    smalltext_stim = visual.TextStim(win=win)
    smalltext_stim.size = 0.05
    fix_cross = visual.TextStim(win=win, text="+", alignText="center")

    # text paths for experiment
    practice_info_path = os.path.join(paths["instructions"], "practice_info*.txt")
    practice_text_path = os.path.join(paths["instructions"], "practice_text*.txt")
    practice_end_path = os.path.join(paths["instructions"], "practice_end*.txt")
    pause_path = os.path.join(paths["instructions"], "pause.txt")

    # read in stories
    if cont_crash:
        stories = tmp_file["stories"]
        n_stories = len(stories) - 1
        old_file_end = tmp_file["file_end"]
        finished_texts = pd.read_csv(
            os.path.join(paths["out_data"], f"rt_{old_file_end}.csv")
        )["story_name"].unique()
    else:
        stories = list(read_text(paths["stories"], stories=True))
        shuffle(stories)
        n_stories = len(stories)
        practice_story = list(read_text(practice_text_path))[0]
        stories = [("practice story", practice_story)] + stories
    pause_text = list(read_text(pause_path))[0]

    # save info in tmp file
    if not cont_crash:
        tmp_info = {
            "gui_information": gui_information,
            "stories": stories,
            "file_end": file_end,
        }
        tmp_path = os.path.join(paths["out_data"], f"tmp_{file_end}.json")
        with open(tmp_path, "w") as fp:
            json.dump(tmp_info, fp)

    # show instruction:
    if not cont_crash:
        inst_path = os.path.join(paths["instructions"], "eeg_instruction*.txt")
        for instruction in read_text(inst_path):
            show_text(instruction, smalltext_stim, win, escape_keys)
    smalltext_stim.size = 0.07

    # experiment start
    for n, (story_name, story) in enumerate(stories):
        if cont_crash and story_name in finished_texts:
            continue

        if n == 0:  # practice text
            for info in read_text(practice_info_path):
                show_text(info, text_stim, win, escape_keys)
            document_id = 0
        else:
            show_text(
                f"{story_name.title()}\n\nStory {n} out of {n_stories}",
                text_stim,
                win,
                escape_keys,
            )
            document_id = doc_ids[story_name]

        if document_id == rsvp_text:
            rsvp_inst_path = os.path.join(
                paths["instructions"], "rsvp_instructions*.txt"
            )
            for inst in read_text(rsvp_inst_path):
                show_text(inst, smalltext_stim, win, escape_keys)
            rsvp(
                story,
                times["rsvp_prchar_time"],
                times["rsvp_min_time"],
                times["fixation_time"],
                win,
                text_stim,
                escape_keys,
            )
        else:
            spr(
                story,
                story_name,
                document_id,
                win,
                fix_cross,
                text_stim,
                stopwatch,
                times["blackscreen_time_short"],
                times["blackscreen_time_long"],
                times["fixation_time"],
                escape_keys,
                save_path=os.path.join(paths["out_data"], f"rt_{file_end}.csv"),
                extra_cols=gui_information,
            )

        # questions
        text_questions(
            story_name,
            document_id,
            questions_df,
            win,
            respond_key,
            escape_keys,
            question_keys,
            save_path=os.path.join(paths["out_data"], f"responses_{file_end}.csv"),
            extra_cols=gui_information,
        )

        if n == 0:
            for end in read_text(practice_end_path):
                show_text(end, smalltext_stim, win, escape_keys)
        else:
            # pause
            show_text(pause_text, smalltext_stim, win, escape_keys)

    # show ending
    end_path = os.path.join(paths["instructions"], "end.txt")
    for end in read_text(end_path):
        show_text(end, text_stim, win, escape_keys)

    # remove tmp file
    os.remove(tmp_path)


if __name__ == "__main__":
    # paths
    paths = {
        "instructions": os.path.join("instructions"),
        "stories": os.path.join("..", "texts", "edited", "*"),
        "questions": os.path.join("questions.xlsx"),
        "out_data": os.path.join("data", "spr"),
    }

    # experimental parameters
    times = {
        "fixation_time": 0.5,
        "blackscreen_time_short": 0.2,
        "blackscreen_time_long": 0.75,
        "rsvp_prchar_time": 0.19,
        "rsvp_min_time": 0.25,
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
