"""
Cloze task
"""

from psychopy import visual, core, event
import os
import pandas as pd
import string
from typing import List
from read_txt import read_text
from show_stim import show_text


def type_response(characters: List[str], text_stim, win):
    win.flip()
    response = ""

    while True:
        key = event.waitKeys()[0]

        if key == "escape":
            win.close()
            core.quit()
        if key == "return":
            break

        if key == "space":
            response += " "
        elif key == "backspace":
            response = response[:-1]
        elif key in characters:
            response += key

        text_stim.text = response
        text_stim.draw()
        win.flip()
    return response


def experiment(stories_path: str, instructions_path: dict, data_path: str):
    df = pd.DataFrame()
    characters = list(string.ascii_lowercase)

    # GUI

    # defining a window
    win = visual.Window(color="black", fullscr=False)
    text_stim = visual.TextStim(win=win)

    # show welcome text
    for welcome in read_text(instructions_path["welcome"]):
        show_text(welcome, text_stim, win)

    # show instruction:
    for instruction in read_text(instructions_path["instruction"]):
        show_text(instruction, text_stim, win)

    # start experiment
    for story_name, story in read_text(stories_path, stories=True):
        words = story.split()
        show_text(story_name, text_stim, win)

        for n, word in enumerate(words):
            show_text(word, text_stim, win)
            response = type_response(characters, text_stim, win)
            df = df.append(
                {"response": response, "story": story_name, "prev_word": word},
                ignore_index=True,
            )

            if n == 10:
                break

    # show ending
    for end in read_text(instructions_path["end"]):
        show_text(end, text_stim, win)

    # saving data
    if not os.path.exists(data_path):
        os.makedirs(data_path)
    df.to_csv(os.path.join(data_path, "cloze_data.csv"))  # change path!


if __name__ == "__main__":
    # paths
    stories_path = os.path.join("..", "stories", "*")
    instructions_path = {
        "welcome": os.path.join("..", "instructions", "welcome.txt"),
        "instruction": os.path.join("..", "instructions", "instruction*.txt"),
        "end": os.path.join("..", "instructions", "end.txt"),
    }
    data_path = os.path.join("..", "data")

    experiment(stories_path, instructions_path, data_path)
