"""
Functions for self-paced reading (SPR) and rapid series visual representation (RSVP)
"""
import re
from util import list_to_csv
from show_stim import show_blackscreen, show_fixation, show_word, show_word_fixed


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
