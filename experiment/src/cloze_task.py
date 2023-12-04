"""
Cloze task
"""

from psychopy import visual, core, event, gui, data
import os, re
import numpy as np
import string
from typing import List
from util import read_text, list_to_csv, get_scale_question
from show_stim import show_text, make_gui, show_scale


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


def make_lines(current_lines: List[str], word: str, maxchar: int):
    line = current_lines[-1]
    tmp_line = line + f" {word}"
    if len(tmp_line) > maxchar:
        lines = current_lines + [word]
    else:
        lines = current_lines[:-1] + [tmp_line]
    return lines


def key_scroll(scroll: int, key: str, max_lines: int, n_lines: int):
    if key == "up":
        scroll -= 1
        if scroll < 0:
            scroll = 0
    if key == "down":
        scroll += 1
        if max_lines + scroll > n_lines:
            scroll = n_lines - max_lines
    return scroll


def type_response(
    characters: List[str],
    story_stim,
    lines,
    max_lines,
    up_stim,
    down_stim,
    text_stim,
    stopwatch,
    win,
):
    response_prefix = "Your response: "
    response = ""

    # scroll if there a more lines than can be viewed
    n_lines = len(lines)
    if n_lines <= max_lines:
        scroll = None
        up_stim.fillColor = "darkgrey"
        down_stim.fillColor = "darkgrey"
    else:
        scroll = n_lines - max_lines

    while True:
        if isinstance(scroll, int) == True:
            story_stim.text = "\n".join(lines[scroll : max_lines + scroll])
            up_stim.fillColor = "white"
            down_stim.fillColor = "white"
            if scroll == 0:
                up_stim.fillColor = "darkgrey"
            if scroll + max_lines == n_lines:
                down_stim.fillColor = "darkgrey"
        else:
            story_stim.text = "\n".join(lines)
        text_stim.text = response_prefix + response
        text_stim.draw()
        story_stim.draw()
        up_stim.draw()
        down_stim.draw()
        win.flip()
        stopwatch.reset()
        key = event.waitKeys()[0]

        if key == "escape":
            win.close()
            core.quit()
        if key == "return":
            rt = stopwatch.getTime()
            break

        if key == "space":
            response += " "
        elif key == "backspace":
            response = response[:-1]
        elif key in characters:
            response += key

        # scroll through text
        if isinstance(scroll, int) == True:
            scroll = key_scroll(scroll, key, max_lines, n_lines)

    return response, rt


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
    characters = list(string.ascii_lowercase)
    escape_keys = ["escape", "q"]
    stopwatch = core.Clock()

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
    n_stories = len(stories)
    pause_path = os.path.join(paths["instructions"], "pause.txt")
    pause_text = list(read_text(pause_path))[0]
    for n, (story_name, story) in enumerate(stories, start=1):
        show_text(f"Story {n} out of {n_stories}", text_stim, win, escape_keys)
        show_text(f"Title: {story_name.title()}", text_stim, win, escape_keys)
        paragraphs = story.split("\n\n")

        lines = [""]
        response, rt = "NA", "NA"
        responses = []
        for paragraph in paragraphs:
            words = re.split(r"[\s]", paragraph)
            for word in words:
                responses.append(
                    {
                        "response": response,
                        "reaction_time": rt,
                        "story": story_name,
                        "correct_word": word,
                    }
                )
                lines = make_lines(lines, word, maxchar_pr_line)
                response, rt = type_response(
                    characters,
                    storybox_stim,
                    lines,
                    max_lines,
                    up,
                    down,
                    writebox_stim,
                    stopwatch,
                    win,
                )
            lines.append("\n")
        show_scale_question(1, story_name, win, file_end, gui_information)
        # save
        list_to_csv(
            df_list=responses,
            out_path=os.path.join(paths["out_data"], f"cloze_{file_end}.csv"),
            extra_cols=gui_information,
        )
        # pause
        show_text(pause_text, text_stim, win, escape_keys)

    # show ending
    end_path = os.path.join(paths["instructions"], "end.txt")
    for end in read_text(end_path):
        show_text(end, text_stim, win, escape_keys)


if __name__ == "__main__":
    # paths
    paths = {
        "instructions": os.path.join("instructions"),
        "stories": os.path.join("..", "texts", "edited", "*"),
        "out_data": os.path.join("data", "cloze"),
    }

    # experimental setup
    fullscreen = True

    experiment(paths, fullscreen)
