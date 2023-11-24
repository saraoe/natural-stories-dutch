"""
Cloze task
"""

from psychopy import visual, core, event, gui, data
import os
import numpy as np
import string
from typing import List
from util import read_text, list_to_csv
from show_stim import show_text


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
        up_stim.fillColor = "grey"
        down_stim.fillColor = "grey"
    else:
        scroll = n_lines - max_lines

    while True:
        if isinstance(scroll, int) == True:
            story_stim.text = "\n".join(lines[scroll : max_lines + scroll])
            up_stim.fillColor = "white"
            down_stim.fillColor = "white"
            if scroll == 0:
                up_stim.fillColor = "grey"
            if scroll + max_lines == n_lines:
                down_stim.fillColor = "grey"
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


def experiment(paths: dict, max_lines: int, maxchar_pr_line: int):
    characters = list(string.ascii_lowercase)
    escape_keys = ["escape", "q"]
    stopwatch = core.Clock()

    # GUI information
    dlg = gui.Dlg(title="Cloze Task")
    dlg.addField("Participant ID: ")
    dlg.addField("Age: ")
    dlg.addField("Gender: ", choices=["Female", "Male", "Other"])
    dlg.show()

    if dlg.OK:
        gui_data = dlg.data
        gui_information = {
            "participant_id": gui_data[0],
            "age": gui_data[1],
            "gender": gui_data[2],
        }
    elif dlg.Cancel:
        core.quit()

    # for saving data
    if not os.path.exists(paths["out_data"]):
        os.makedirs(paths["out_data"])

    date = data.getDateStr()
    file_end = f"{gui_information['participant_id']}_{date}"

    # defining a window
    win = visual.Window(color="black", fullscr=False)
    text_stim = visual.TextStim(win=win)
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
        borderColor="grey",
    )
    up = make_arrows("up", storybox_stim, win)
    down = make_arrows("down", storybox_stim, win)

    # show instruction:
    inst_path = os.path.join(paths["instructions"], "cloze_instruction*.txt")
    for instruction in read_text(inst_path):
        show_text(instruction, text_stim, win, escape_keys)

    # start experiment
    for story_name, story in read_text(paths["stories"], stories=True):
        show_text(story_name, text_stim, win, escape_keys)
        paragraphs = story.split("\n\n")

        lines = [""]
        response, rt = "NA", "NA"
        responses = []
        for paragraph in paragraphs:
            words = paragraph.split()
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
        # save
        list_to_csv(
            df_list=responses,
            out_path=os.path.join(paths["out_data"], f"cloze_{file_end}.csv"),
            extra_cols=gui_information,
        )

    # show ending
    end_path = os.path.join(paths["instructions"], "end.txt")
    for end in read_text(end_path):
        show_text(end, text_stim, win, escape_keys)



if __name__ == "__main__":
    # paths
    paths = {
        "instructions": os.path.join("instructions"),
        "stories": os.path.join("..", "texts", "edited", "*"),
        "out_data": os.path.join("data"),
    }


    # experimental setup
    maxchar_pr_line = 35
    max_lines = 7

    experiment(paths, max_lines, maxchar_pr_line)
