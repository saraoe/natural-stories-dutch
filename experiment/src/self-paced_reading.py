"""
Self-paced reading experiment
"""

from psychopy import visual, core, gui, data
import os
import re
import pandas as pd
from util import read_text, list_to_csv
from show_stim import (
    show_fixation,
    show_text,
    show_word,
    show_blackscreen,
    show_questions,
    show_scale,
    make_gui,
)


def self_paced_reading(
    story,
    document_id,
    win,
    fix_cross,
    text_stim,
    stopwatch,
    blackscreen_time,
    escape_keys,
):
    rt_list = []
    paragraphs = re.split("\n\n", story)

    for paragraph in paragraphs:
        words = re.split(r"[\s]", paragraph)
        for word in words:
            rt = show_word(word, text_stim, win, stopwatch, escape_keys)
            rt_list.append(
                {"reation_time": rt, "document_id": document_id, "word": word}
            )

            show_blackscreen(win, sec=blackscreen_time)
        show_fixation(fix_cross, win, sec=fixation_time, escape_keys=escape_keys)

    return rt_list


def get_scale_question(document_id: int, story_name: str):
    if document_id in [0, 1, 2]:
        q = f"In hoeverre was je bekend met het sprookje {story_name} dat werd verteld in de vorige tekst?"
    elif document_id in [5, 6]:
        q = f"In hoeverre was je bekend met de roman/film {story_name} waarover werd verteld in de vorige tekst?"
    elif document_id in [3, 4, 7, 8, 9, 10]:
        q = "In hoeverre was je bekend met het onderwerp van de vorige tekst?"
    return q


def experiment(
    paths: dict,
    fixation_time: int,
    blackscreen_time: int,
    keys: str,
    fullscreen: bool = True,
):
    stopwatch = core.Clock()

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
    fields = {
        "Participant ID": None,
        "Age": None,
        "Gender": ["Female", "Male", "Other"],
        "Hand": ["Left", "Right"],
    }
    gui_information = make_gui(fields, title="Self-Paced Reading")

    # for saving data
    if not os.path.exists(paths["out_data"]):
        os.makedirs(paths["out_data"])

    date = data.getDateStr()
    file_end = f"{gui_information['participant_id']}_{date}"

    # defining a window
    win = visual.Window(color="black", fullscr=fullscreen)
    text_stim = visual.TextStim(win=win)
    smalltext_stim = visual.TextStim(win=win)
    smalltext_stim.size = 0.05
    fix_cross = visual.TextStim(win=win, text="+", alignText="center")
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

    # show instruction:
    inst_path = os.path.join(paths["instructions"], "eeg_instruction*.txt")
    for instruction in read_text(inst_path):
        show_text(instruction, smalltext_stim, win, escape_keys)
    smalltext_stim.size = 0.07

    # practice phase start
    practice_info_path = os.path.join(paths["instructions"], "practice_info*.txt")
    practice_text_path = os.path.join(paths["instructions"], "practice_text*.txt")
    practice_end_path = os.path.join(paths["instructions"], "practice_end*.txt")
    for info in read_text(practice_info_path):
        show_text(info, text_stim, win, escape_keys)
    for practice_story in read_text(practice_text_path):
        story_name = "Practice Text"  # fix this
        document_id = 0
        rts = self_paced_reading(
            practice_story,
            document_id,
            win,
            fix_cross,
            text_stim,
            stopwatch,
            blackscreen_time,
            escape_keys,
        )

        # questions
        scale_question = get_scale_question(document_id, story_name)
        response_scale = show_scale(
            scale_question,
            document_id,
            question_id=0,
            qtext_stim=qtext_up,
            respondtext=respond_stim,
            scale_stim=scale,
            win=win,
            escape_keys=escape_keys,
            question_keys=scale_keys,
        )
        qs = questions_df[questions_df["document_id"] == document_id]
        responses = show_questions(
            qs, qtext_up, respond_stim, win, escape_keys, question_keys
        )

        # save
        list_to_csv(
            df_list=rts,
            out_path=os.path.join(paths["out_data"], f"rt_{file_end}.csv"),
            extra_cols=gui_information,
        )
        list_to_csv(
            df_list=responses,
            out_path=os.path.join(paths["out_data"], f"responses_{file_end}.csv"),
            extra_cols=gui_information,
        )
    for end in read_text(practice_end_path):
        show_text(end, smalltext_stim, win, escape_keys)

    # experiment start
    stories = list(read_text(paths["stories"], stories=True))
    n_stories = len(stories)
    pause_path = os.path.join(paths["instructions"], "pause.txt")
    pause_text = list(read_text(pause_path))[0]
    for n, (story_name, story) in enumerate(stories, start=1):
        show_text(
            f"{story_name.title()}\n\nStory {n} out of {n_stories}",
            text_stim,
            win,
            escape_keys,
        )
        document_id = doc_ids[story_name]

        rts = self_paced_reading(
            story,
            document_id,
            win,
            fix_cross,
            text_stim,
            stopwatch,
            blackscreen_time,
            escape_keys,
        )

        # questions
        scale_question = get_scale_question(document_id, story_name)
        response_scale = show_scale(
            scale_question,
            document_id,
            question_id=0,
            qtext_stim=qtext_up,
            respondtext=respond_stim,
            scale_stim=scale,
            win=win,
            escape_keys=escape_keys,
            question_keys=scale_keys,
        )
        qs = questions_df[questions_df["document_id"] == document_id]
        responses = show_questions(
            qs, qtext_up, respond_stim, win, escape_keys, question_keys
        )

        # save
        list_to_csv(
            df_list=rts,
            out_path=os.path.join(paths["out_data"], f"rt_{file_end}.csv"),
            extra_cols=gui_information,
        )
        list_to_csv(
            df_list=response_scale + responses,
            out_path=os.path.join(paths["out_data"], f"responses_{file_end}.csv"),
            extra_cols=gui_information,
        )

        # pause
        show_text(pause_text, smalltext_stim, win, escape_keys)

    # show ending
    end_path = os.path.join(paths["instructions"], "end.txt")
    for end in read_text(end_path):
        show_text(end, text_stim, win, escape_keys)


if __name__ == "__main__":
    # paths
    paths = {
        "instructions": os.path.join("instructions"),
        "stories": os.path.join("..", "texts", "edited", "*"),
        "questions": os.path.join("questions.xlsx"),
        "out_data": os.path.join("data"),
    }

    # experimental parameters
    fixation_time = 0.5
    blackscreen_time = 0.2

    # experimental device
    keys = "computer"
    fullscreen = False

    experiment(paths, fixation_time, blackscreen_time, keys, fullscreen)
