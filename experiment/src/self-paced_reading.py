"""
Self-paced reading experiment
"""

from psychopy import visual, core, gui, data
import os
import pandas as pd
from util import read_text, list_to_csv
from show_stim import (
    show_fixation,
    show_text,
    show_word,
    show_blackscreen,
    show_questions,
)


def experiment(paths: dict, fixation_time: int, blackscreen_time: int):
    stopwatch = core.Clock()

    # empty lists for dfs
    rts = []
    responses = []

    # questions
    questions_df = pd.read_excel(paths["questions"])

    # GUI information
    dlg = gui.Dlg(title="Reading experiment")
    dlg.addField("Participant ID: ")
    dlg.addField("Age: ")
    dlg.addField("Gender: ", choices=["Female", "Male", "Other"])
    dlg.show()

    if dlg.OK:
        gui_data = dlg.data
    elif dlg.Cancel:
        core.quit()

    # defining a window
    win = visual.Window(color="black", fullscr=False)
    text_stim = visual.TextStim(win=win)
    fix_cross = visual.TextStim(win=win, text="+", alignText="center")

    # show instruction:
    for instruction in read_text(paths["instruction"]):
        show_text(instruction, text_stim, win)

    # experiment start
    for story_name, story in read_text(paths["stories"], stories=True):
        show_fixation(fix_cross, win, sec=fixation_time)
        show_text(story_name, text_stim, win)
        document_id = 1  # fix this!

        paragraphs = story.split("\n\n")

        for paragraph in paragraphs:
            show_fixation(fix_cross, win, sec=fixation_time)
            words = paragraph.split(" ")
            for word in words:
                rt = show_word(word, text_stim, win, stopwatch)
                rts.append(
                    {"reation_time": rt, "document_id": document_id, "word": word}
                )

                show_blackscreen(win, sec=blackscreen_time)

        # questions
        qs = questions_df[questions_df["document_id"] == document_id]
        tmp_responses = show_questions(qs, text_stim, win)
        responses += tmp_responses

    # show ending
    for end in read_text(paths["end"]):
        show_text(end, text_stim, win)

    # saving data
    if not os.path.exists(paths["out_data"]):
        os.makedirs(paths["out_data"])

    date = data.getDateStr()
    file_end = f"{gui_data[0]}_{date}"
    gui_information = {
        "participant_id": gui_data[0],
        "age": gui_data[1],
        "gender": gui_data[2],
    }

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


if __name__ == "__main__":
    # paths
    paths = {
        "instruction": os.path.join("..", "instructions", "instruction*.txt"),
        "end": os.path.join("..", "instructions", "end.txt"),
        "stories": os.path.join("..", "..", "texts", "*"),
        "questions": os.path.join("..", "questions.xlsx"),
        "out_data": os.path.join("..", "data"),
    }

    # experimental parameters
    fixation_time = 0.5
    blackscreen_time = 0.2

    experiment(paths, fixation_time, blackscreen_time)
