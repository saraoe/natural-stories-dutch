"""
Cloze task
"""

from psychopy import visual, core, event, data
import os, re
from random import shuffle
import numpy as np
import pandas as pd
from util import read_text, list_to_csv, get_scale_question
from show_stim import show_text, make_gui, show_scale
from reading_funcs import cloze_task


def make_arrows(direction: str, textbox, win):
    if direction == "up":
        v = np.array([[0, 1], [-0.5, 0], [0.5, 0]])
    if direction == "down":
        v = np.array([[0, -1], [-0.5, 0], [0.5, 0]])
    arrow = visual.ShapeStim(
        win=win,
        vertices=v,
        size=textbox.size / 8,
    )
    if direction == "up":
        arrow.pos = (
            textbox.pos[0] + textbox.size[0] / 2 + arrow.size[0],
            textbox.pos[1] + arrow.size[1],
        )
    else:
        arrow.pos = (
            textbox.pos[0] + textbox.size[0] / 2 + arrow.size[0],
            textbox.pos[1] - arrow.size[1],
        )
    return arrow


def show_scale_question(
    document_id,
    story_name,
    win,
    file_end,
    extra_cols,
    respond_key="return",
    escape_keys=["escape"],
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
        document_id,
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
                "question": scale_question,
                "document_id": document_id,
            }
        ],
        out_path=os.path.join(paths["out_data"], f"responses_{file_end}.csv"),
        extra_cols=extra_cols,
    )


def experiment(paths: dict, fullscreen: bool):
    escape_keys = ["escape", "q"]
    stopwatch = core.Clock()

    # get document_ids
    questions_df = pd.read_excel(paths["questions"])
    questions_df["story"] = questions_df["Story"].apply(
        lambda s: re.sub("[^a-zA-Z\s]+", "", s).lower()
    )
    doc_ids = pd.Series(
        questions_df.document_id.values, index=questions_df.story
    ).to_dict()

    # text size
    if fullscreen:
        maxchar_pr_line = 90
        max_lines = 10
    else:
        maxchar_pr_line = 35
        max_lines = 7

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
    file_end = f"{gui_information['participant_id']}_{date}"

    # defining a window
    win = visual.Window(color="grey", fullscr=fullscreen)
    text_stim = visual.TextStim(win=win)
    smalltext_stim = visual.TextStim(win=win)
    smalltext_stim.size = 0.05
    storybox_stim = visual.TextBox2(
        win=win,
        text="",
        pos=(0, 0.1),
        size=[1, 0.9],
    )
    writebox_stim = visual.TextBox2(
        win=win,
        text="",
        pos=(0, -0.8),
        size=[1, 0.1],
        borderColor="darkgrey",
    )
    up = make_arrows("up", storybox_stim, win)
    down = make_arrows("down", storybox_stim, win)

    # show instruction:
    inst_path = os.path.join(paths["instructions"], "cloze_instruction*.txt")
    for instruction in read_text(inst_path):
        show_text(instruction, smalltext_stim, win, escape_keys)

    # start experiment
    stories = list(read_text(paths["stories"], stories=True))
    shuffle(stories)
    n_stories = len(stories)
    pause_path = os.path.join(paths["instructions"], "pause.txt")
    pause_text = list(read_text(pause_path))[0]
    for n, (story_name, story) in enumerate(stories, start=1):
        show_text(f"Story {n} out of {n_stories}", text_stim, win, escape_keys)
        show_text(f"Title: {story_name.title()}", text_stim, win, escape_keys)
        document_id = doc_ids[story_name]

        cloze_task(
            story,
            document_id,
            maxchar_pr_line,
            max_lines,
            storybox_stim,
            writebox_stim,
            up,
            down,
            stopwatch,
            win,
            save_path=os.path.join(paths["out_data"], f"cloze_{file_end}.csv"),
            extra_cols=gui_information,
        )

        show_scale_question(document_id, story_name, win, file_end, gui_information)

        # pause
        show_text(pause_text, text_stim, win, escape_keys)

    # show ending
    end_path = os.path.join(paths["instructions"], "end.txt")
    for end in read_text(end_path):
        show_text(end, text_stim, win, escape_keys)


if __name__ == "__main__":
    # paths
    paths = {
        "questions": os.path.join("questions.xlsx"),
        "instructions": os.path.join("instructions"),
        "stories": os.path.join("..", "texts", "edited", "*"),
        "out_data": os.path.join("data", "cloze"),
    }

    # experimental setup
    fullscreen = True

    experiment(paths, fullscreen)
