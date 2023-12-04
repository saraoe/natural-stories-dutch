"""
Functions for self-paced reading (SPR) and rapid series visual representation (RSVP)
"""
import re
from util import list_to_csv, make_lines
from show_stim import (
    show_blackscreen,
    show_fixation,
    show_word,
    show_word_fixed,
    type_response,
)


# for SPR exp
def spr(
    story,
    document_id,
    win,
    fix_cross,
    text_stim,
    stopwatch,
    blackscreen_time_short,
    blackscreen_time_long,
    fixation_time,
    escape_keys,
    save_path,
    extra_cols,
):
    rt_list = []
    paragraphs = re.split("\n\n", story)

    for paragraph in paragraphs:
        show_fixation(fix_cross, win, sec=fixation_time, escape_keys=escape_keys)
        words = re.split(r"[\s]", paragraph)
        for word in words:
            rt = show_word(word, text_stim, win, stopwatch, escape_keys)
            rt_list.append(
                {"reation_time": rt, "document_id": document_id, "word": word}
            )
            list_to_csv(
                df_list=[
                    {"reation_time": rt, "document_id": document_id, "word": word}
                ],
                out_path=save_path,
                extra_cols=extra_cols,
            )

            show_blackscreen(win, sec=blackscreen_time_short)
    show_blackscreen(win, sec=blackscreen_time_long)


def rsvp(
    story,
    sec,
    win,
    text_stim,
    escape_keys,
):
    paragraphs = re.split("\n\n", story)

    for paragraph in paragraphs:
        words = re.split(r"[\s]", paragraph)
        for word in words:
            show_word_fixed(word, sec, text_stim, win, escape_keys)

        show_word_fixed("+", sec, text_stim, win, escape_keys)


def cloze_task(
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
    save_path,
    extra_cols,
):
    paragraphs = story.split("\n\n")

    lines = [""]
    response, rt = "NA", "NA"
    responses = []
    for paragraph in paragraphs:
        words = re.split(r"[\s]", paragraph)
        for word in words:
            list_to_csv(
                df_list=[
                    {
                        "response": response,
                        "reaction_time": rt,
                        "correct_word": word,
                        "document_id": document_id,
                    }
                ],
                out_path=save_path,
                extra_cols=extra_cols,
            )
            responses.append(
                {
                    "response": response,
                    "reaction_time": rt,
                    "correct_word": word,
                    "document_id": document_id,
                }
            )
            lines = make_lines(lines, word, maxchar_pr_line)
            response, rt = type_response(
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
