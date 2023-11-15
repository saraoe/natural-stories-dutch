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
)


def self_paced_reading(
    story,
    story_name,
    document_id,
    questions_df,
    win,
    fix_cross,
    text_stim,
    stopwatch,
    blackscreen_time,
    escape_keys,
    question_keys,
):
    rt_list = []
    paragraphs = story.split("\n\n")

    show_text(story_name, text_stim, win, escape_keys)

    for paragraph in paragraphs:
        show_fixation(fix_cross, win, sec=fixation_time)
        words = paragraph.split(" ")
        for word in words:
            rt = show_word(word, text_stim, win, stopwatch, escape_keys)
            rt_list.append(
                {"reation_time": rt, "document_id": document_id, "word": word}
            )

            show_blackscreen(win, sec=blackscreen_time)

    # questions
    qs = questions_df[questions_df["document_id"] == document_id]
    response = show_questions(qs, text_stim, win, escape_keys, question_keys)
    return rt_list, response


def experiment(
    paths: dict,
    fixation_time: int,
    blackscreen_time: int,
    keys: str,
    fullscreen: bool = True,
):
    stopwatch = core.Clock()

    if keys == "computer":
        escape_keys = ["escape", "q"]
        question_keys = ["1", "2", "3", "4"]

    # questions
    questions_df = pd.read_excel(paths["questions"])
    questions_df["story"] = questions_df["Story"].apply(
        lambda s: re.sub("[^a-zA-Z\s]+", "", s).lower()
    )
    doc_ids = pd.Series(
        questions_df.document_id.values, index=questions_df.story
    ).to_dict()

    # GUI information
    dlg = gui.Dlg(title="Reading experiment")
    dlg.addField("Participant ID: ")
    dlg.addField("Age: ")
    dlg.addField("Gender: ", choices=["Female", "Male", "Other"])
    dlg.addField("Hand: ", choices=["Left", "Right"])
    dlg.show()

    if dlg.OK:
        gui_data = dlg.data
        gui_information = {
            "participant_id": gui_data[0],
            "age": gui_data[1],
            "gender": gui_data[2],
            "hand": gui_data[3].lower(),
        }
    elif dlg.Cancel:
        core.quit()

    # defining a window
    win = visual.Window(color="black", fullscr=fullscreen)
    text_stim = visual.TextStim(win=win)
    fix_cross = visual.TextStim(win=win, text="+", alignText="center")

    # show instruction:
    inst_path = os.path.join(paths["instructions"], "eeg_instruction*.txt")
    for instruction in read_text(inst_path):
        show_text(instruction, text_stim, win, escape_keys)

    # practice phase start
    practice_info_path = os.path.join(paths["instructions"], "practice_info*.txt")
    practice_text_path = os.path.join(paths["instructions"], "practice_text*.txt")
    practice_end_path = os.path.join(paths["instructions"], "practice_end*.txt")
    for info in read_text(practice_info_path):
        show_text(info, text_stim, win, escape_keys)
    for practice_story in read_text(practice_text_path):
        story_name = "Practice Story"
        document_id = 1  ## fix this!
        rts, responses = self_paced_reading(
            practice_story,
            story_name,
            document_id,
            questions_df,
            win,
            fix_cross,
            text_stim,
            stopwatch,
            blackscreen_time,
            escape_keys,
            question_keys,
        )
    for instruction in read_text(practice_end_path):
        show_text(instruction, text_stim, win, escape_keys)

    # experiment start
    stories = list(read_text(paths["stories"], stories=True))
    n_stories = len(stories)
    pause_path = os.path.join(paths["instructions"], "pause.txt")
    pause_text = list(read_text(pause_path))[0]
    for n, (story_name, story) in enumerate(stories):
        show_fixation(fix_cross, win, sec=fixation_time)
        show_text(f"Story {n} out of {n_stories}", text_stim, win, escape_keys)
        document_id = doc_ids[story_name]

        tmp_rts, tmp_responses = self_paced_reading(
            story,
            story_name,
            document_id,
            questions_df,
            win,
            fix_cross,
            text_stim,
            stopwatch,
            blackscreen_time,
            escape_keys,
            question_keys,
        )
        rts += tmp_rts
        responses += tmp_responses

        # pause
        show_text(pause_text, text_stim, win, escape_keys)

    # show ending
    end_path = os.path.join(paths["instructions"], "end.txt")
    for end in read_text(end_path):
        show_text(end, text_stim, win, escape_keys)

    # saving data
    if not os.path.exists(paths["out_data"]):
        os.makedirs(paths["out_data"])

    date = data.getDateStr()
    file_end = f"{gui_information['participant_id']}_{date}"

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
        "instructions": os.path.join("..", "instructions"),
        "stories": os.path.join("..", "..", "texts", "edited", "*"),
        "questions": os.path.join("..", "questions.xlsx"),
        "out_data": os.path.join("..", "data"),
    }

    # experimental parameters
    fixation_time = 0.5
    blackscreen_time = 0.2

    # experimental device
    keys = "computer"
    fullscreen = False

    experiment(paths, fixation_time, blackscreen_time, keys, fullscreen)
