"""
functions for showing stimuli in psychopy scripts
"""

from psychopy import core, event, gui, visual
import re
import string
import pandas as pd
from random import shuffle
from util import get_punct_dict, read_text, send_eeg_trigger


def show_fixation(stim, win, sec, escape_keys):
    stim.foreColor = "darkgrey"
    stim.draw()
    win.flip()
    core.wait(sec)
    stim.foreColor = "white"
    stim.draw()
    win.flip()
    key = event.waitKeys()[0]
    if key in escape_keys:
        win.close()
        core.quit()


def show_blackscreen(win, sec, config):
    win.flip()
    send_eeg_trigger(config, 0)
    core.wait(sec)


def show_text(
    text: str,
    text_stim,
    win,
    escape_keys,
    text_ending,
    possible_keys=None,
):
    event.clearEvents(eventType="keyboard")
    text_stim.text = text + f"\n\n{text_ending}"
    text_stim.draw()
    win.flip()
    key = event.waitKeys(keyList=possible_keys)[0]
    if key in escape_keys:
        win.close()
        core.quit()
    return key


def show_text_from_path(path: str, config, align_text: str = "left"):
    config.smalltext_stim.alignment = align_text

    for t in read_text(path):
        show_text(
            t,
            config.smalltext_stim,
            config.win,
            config.escape_keys,
            config.show_text_ending,
        )


def show_word(word: str, text_stim, win, stopwatch, escape_keys, config, eeg_trigger):
    event.clearEvents(eventType="keyboard")
    text_stim.text = word
    text_stim.draw()
    win.flip()
    send_eeg_trigger(config, eeg_trigger)
    stopwatch.reset()
    key = event.waitKeys()[0]
    rt = stopwatch.getTime()
    if key in escape_keys:
        win.close()
        core.quit()
    return rt


def show_word_fixed(
    word: str,
    pr_char_sec,
    min_sec,
    text_stim,
    win,
    escape_keys,
    config,
    eeg_trigger,
):
    char_time = pr_char_sec[0] * len(word) + pr_char_sec[1]
    sec = char_time if char_time >= min_sec else min_sec
    text_stim.text = word
    text_stim.draw()
    win.flip()
    send_eeg_trigger(config, eeg_trigger)
    core.wait(sec)

    pressed_escape_keys = event.getKeys(keyList=escape_keys)
    if pressed_escape_keys:
        win.close()
        core.quit()
    return sec


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
                q_stim.borderColor = "darkgrey"
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
        borderColor="darkgrey",
    )
    qtext_stim.pos = (0, 0.8)

    responses = []

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

        responses.append(
            {
                "response": response,
                "correct": correct,
                "document_id": row["document_id"],
                "question_id": row["question_id"],
            }
        )
    return responses


def show_scale(
    question: str,
    qtext_stim,
    respondtext,
    scale_stim,
    win,
    escape_keys,
    question_keys,
):
    qtext_stim.text = question
    qtext_stim.pos = (0, 0.6)
    scale_stim.markerPos = None
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
    return response


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


def type_response(
    story_stim,
    text,
    text_stim,
    stopwatch,
    win,
    last_word: bool,
    time_out: int,
):
    # possible characters
    char = list(string.ascii_lowercase + string.digits)
    punct, shift_punct = get_punct_dict()

    response_prefix = "Je antwoord: "
    response = ""
    story_stim.text = text + "\n"

    if time_out:
        timed_out = False
        time_out_stim = visual.TextStim(win=win, text="", pos=(0, -0.85), color="pink")
        time_out_stim.size = 0.07

    stopwatch.reset()
    while True:
        text_stim.text = response_prefix + response

        if time_out:
            current_time = stopwatch.getTime()
            if current_time >= time_out:
                time_out_stim.text = "\n Time-out!"
                timed_out = True
            elif current_time >= time_out / 2:
                time_out_stim.text = "\n Probeer snel te antwoorden"
            time_out_stim.draw()

        text_stim.draw()
        story_stim.draw()
        win.flip()

        if timed_out:
            core.wait(0.5)
            rt = current_time
            break

        keys = event.getKeys()
        if keys:
            key = keys[-1]
        else:
            continue

        if key == "escape":
            win.close()
            core.quit()
        if key == "return":
            if response != "" or last_word:
                rt = stopwatch.getTime()
                break

        if key == "backspace":
            response = response[:-1]
        elif key in char:
            response += key
        elif key in punct.keys():
            response += punct[key]
        elif key in ["lshift", "rshift"]:
            second_key = event.waitKeys()[0]
            if second_key in shift_punct.keys():
                response += shift_punct[second_key]
            elif second_key in char:
                response += second_key.upper()

    return response, rt
