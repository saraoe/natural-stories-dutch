"""
Functions for self-paced reading (SPR) and rapid series visual representation (RSVP)
"""
import re
from util import list_to_csv, make_lines, read_text
from show_stim import (
    show_blackscreen,
    show_fixation,
    show_word,
    show_word_fixed,
    show_text,
    type_response,
)


# for SPR exp
def spr(
    story,
    story_name,
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
    paragraphs = re.split("\n\n", story)

    for paragraph in paragraphs:
        show_fixation(fix_cross, win, sec=fixation_time, escape_keys=escape_keys)
        words = re.split(r"[\s]", paragraph)
        for word in words:
            rt = show_word(word, text_stim, win, stopwatch, escape_keys)
            list_to_csv(
                df_list=[
                    {
                        "reation_time": rt,
                        "story_name": story_name,
                        "document_id": document_id,
                        "word": word,
                    }
                ],
                out_path=save_path,
                extra_cols=extra_cols,
            )

            show_blackscreen(win, sec=blackscreen_time_short)
    show_blackscreen(win, sec=blackscreen_time_long)


def spr_w_practice(
    story,
    story_name,
    document_id,
    n,
    n_stories,
    win,
    fix_cross,
    text_stim,
    smalltext_stim,
    stopwatch,
    blackscreen_time_short,
    blackscreen_time_long,
    fixation_time,
    escape_keys,
    save_path,
    extra_cols,
    practice_story,
    practice_info_path,
    practice_end_path,
):
    if practice_story:
        for info in read_text(practice_info_path):
            show_text(info, smalltext_stim, win, escape_keys)
        spr(
            practice_story,
            "practice story",
            0,
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
        )
        for end in read_text(practice_end_path):
            show_text(end, smalltext_stim, win, escape_keys)

    show_text(
        f"{story_name.title()}\n\nStory {n} out of {n_stories}",
        text_stim,
        win,
        escape_keys,
    )
    spr(
        story,
        story_name,
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
    )


def rsvp(
    story,
    pr_char_sec,
    min_sec,
    fixation_sec,
    win,
    text_stim,
    escape_keys,
):
    paragraphs = re.split("\n\n", story)

    for paragraph in paragraphs:
        show_word_fixed(
            "+", fixation_sec - 0.02, fixation_sec, text_stim, win, escape_keys
        )

        words = re.split(r"[\s]", paragraph)
        for word in words:
            show_word_fixed(word, pr_char_sec, min_sec, text_stim, win, escape_keys)
            show_blackscreen(win, min_sec)


def rsvp_w_practice(
    story,
    story_name,
    pr_char_sec,
    min_sec,
    fixation_sec,
    n,
    n_stories,
    win,
    text_stim,
    smalltext_stim,
    escape_keys,
    practice_story,
    practice_info_path,
    practice_end_path,
):
    if practice_story:
        for info in read_text(practice_info_path):
            show_text(info, smalltext_stim, win, escape_keys)
        rsvp(
            practice_story,
            pr_char_sec,
            min_sec,
            fixation_sec,
            win,
            text_stim,
            escape_keys,
        )
        for end in read_text(practice_end_path):
            show_text(end, smalltext_stim, win, escape_keys)

    show_text(
        f"{story_name.title()}\n\nStory {n} out of {n_stories}",
        text_stim,
        win,
        escape_keys,
    )
    rsvp(
        story,
        pr_char_sec,
        min_sec,
        fixation_sec,
        win,
        text_stim,
        escape_keys,
    )


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
