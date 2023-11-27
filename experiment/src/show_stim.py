"""
functions for showing stimuli in psychopy scripts
"""
from psychopy import core, event, gui, visual
import re
import pandas as pd
from random import shuffle


def show_fixation(stim, win, sec, escape_keys):
    stim.draw()
    win.flip()
    core.wait(sec)
    key = event.waitKeys()[0]
    if key in escape_keys:
        win.close()
        core.quit()


def show_blackscreen(win, sec):
    win.flip()
    core.wait(sec)


def show_text(text: str, text_stim, win, escape_keys, possible_keys=None):
    text_stim.text = text
    text_stim.draw()
    win.flip()
    key = event.waitKeys(keyList=possible_keys)[0]
    if key in escape_keys:
        win.close()
        core.quit()
    return key


def show_word(word: str, text_stim, win, stopwatch, escape_keys):
    text_stim.text = word
    text_stim.draw()
    win.flip()
    stopwatch.reset()
    key = event.waitKeys()[0]
    rt = stopwatch.getTime()
    if key in escape_keys:
        win.close()
        core.quit()
    return rt


def show_question(
    question: str,
    answers: dict,
    qtext_stim,
    respondtext,
    win,
    escape_keys,
    question_keys,
    q_stim,
):
    answers_list = list(answers.keys())
    shuffle(answers_list)
    qtext_stim.text = f"{question}"

    pos_list = [(-0.5, 0.2), (0.5, 0.2), (-0.5, -0.5), (0.5, -0.5)]
    response_key = None

    while True:
        qtext_stim.draw()
        for i, (answer, pos) in enumerate(zip(answers_list, pos_list), start=1):
            if i == response_key:
                q_stim.borderColor = "green"
            else:
                q_stim.borderColor = "grey"
            q_stim.pos = pos
            q_stim.text = f"{i}: {answer}"
            q_stim.draw()
        win.flip()
        key = event.waitKeys(keyList=escape_keys + question_keys)[0]
        if key in escape_keys:
            win.close()
            core.quit()
        if key == question_keys[-1]:
            if response_key:
                break
            else:
                continue
        response_key = int(key)
        respondtext.draw()
    response_letter = answers[answers_list[response_key - 1]]
    return response_letter


def show_questions(
    questions_df: pd.DataFrame,
    qtext_stim,
    respond_stim,
    win,
    escape_keys,
    question_keys,
):
    q_stim = visual.TextBox2(
        win=win,
        text="",
        size=[0.85, 0.55],
        letterHeight=0.05,
        borderColor="grey",
    )
    response_list = []

    for index, row in questions_df.iterrows():
        ans_cols = ["a-correct", "b", "c", "d"]
        answers = {row[col]: col for col in ans_cols}
        response = show_question(
            row["Question"],
            answers,
            qtext_stim,
            respond_stim,
            win,
            escape_keys,
            question_keys,
            q_stim,
        )
        correct = 1 if response == "a-correct" else 0

        response_list.append(
            {
                "response": response,
                "correct": correct,
                "document_id": row["document_id"],
                "question_id": row["question_id"],
            }
        )
    return response_list


def show_scale(
    question: str,
    document_id: int,
    question_id,
    qtext_stim,
    respondtext,
    scale_stim,
    win,
    escape_keys,
    question_keys,
):
    qtext_stim.text = question
    response = None

    while True:
        qtext_stim.draw()
        scale_stim.draw()
        win.flip()
        key = event.waitKeys(keyList=escape_keys + question_keys)[0]
        if key in escape_keys:
            win.close()
            core.quit()
        if key == question_keys[-1]:
            if response:
                break
            else:
                continue
        response = int(key)
        scale_stim.markerPos = response
        respondtext.draw()

    response_list = [
        {
            "response": response,
            "correct": "NA",
            "document_id": document_id,
            "question_id": question_id,
        }
    ]
    return response_list


def fix_name(name: str):
    return re.sub(r"[\s]", "_", name).lower()


def make_gui(fields: dict, title: str):
    dlg = gui.Dlg(title=title)
    for field, choices in fields.items():
        dlg.addField(f"{field} :", choices=choices)
    dlg.show()

    if dlg.OK:
        gui_data = dlg.data
        gui_information = {
            fix_name(field): gui_data[i] for i, field in enumerate(fields.keys())
        }
    else:
        core.quit()
    return gui_information
