"""
functions for showing stimuli in psychopy scripts
"""
from psychopy import core, event
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
    question: str, answers: dict, text_stim, win, escape_keys, question_keys
):
    answers_list = list(answers.keys())
    shuffle(answers_list)
    q_str = f"{question} \n\n"
    for i, answer in enumerate(answers_list, start=1):
        q_str += f"{i}: {answer} \n"

    key = show_text(
        q_str, text_stim, win, escape_keys, possible_keys=escape_keys + question_keys
    )
    response_key = int(key)
    response_letter = answers[answers_list[response_key - 1]]
    return response_letter


def show_questions(
    questions_df: pd.DataFrame, text_stim, win, escape_keys, question_keys
):
    response_list = []

    for index, row in questions_df.iterrows():
        ans_cols = ["a-correct", "b", "c", "d"]
        answers = {row[col]: col for col in ans_cols}
        response = show_question(
            row["Question"], answers, text_stim, win, escape_keys, question_keys
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
