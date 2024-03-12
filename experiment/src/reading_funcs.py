"""
Functions for self-paced reading (SPR) and rapid series visual representation (RSVP)
"""

import re
from util import list_to_csv, add_word, get_scale_question, send_eeg_trigger
from show_stim import (
    show_blackscreen,
    show_fixation,
    show_word,
    show_word_fixed,
    type_response,
    show_scale,
    show_questions,
)


# for SPR exp
def spr(
    story: str,
    story_name: str,
    document_id: int,
    config,
    times: dict,
    save_path: str,
    extra_cols: dict,
):
    document_trigger = config.trigger_documents[document_id]
    send_eeg_trigger(config, document_trigger, reset=True)

    paragraphs = re.split("\n\n", story)
    for paragraph in paragraphs:
        send_eeg_trigger(config, config.trigger_paragraph)

        show_fixation(
            config.fix_cross,
            config.win,
            sec=times["fixation"],
            escape_keys=config.escape_keys,
        )
        send_eeg_trigger(config, 0)

        words = re.split(r"[\s]", paragraph)
        for n, word in enumerate(words):
            word_trigger = (
                config.trigger_word_even if n % 2 == 0 else config.trigger_word_uneven
            )

            rt = show_word(
                word,
                config.text_stim,
                config.win,
                config.stopwatch,
                config.escape_keys,
                config,
                word_trigger,
            )
            list_to_csv(
                df_list=[
                    {
                        "reading_type": "SPR",
                        "reation_time": rt,
                        "story_name": story_name,
                        "document_id": document_id,
                        "document_trigger": document_trigger,
                        "word": word,
                        "word_n": n,
                        "word_trigger": word_trigger,
                    }
                ],
                out_path=save_path,
                extra_cols=extra_cols,
            )

            show_blackscreen(config.win, sec=times["blackscreen_short"])
    show_blackscreen(config.win, sec=times["blackscreen_long"])


def rsvp(
    story: str,
    story_name: str,
    document_id: int,
    times: dict,
    config,
    save_path: str,
    extra_cols: dict,
):
    document_trigger = config.trigger_documents[document_id]
    send_eeg_trigger(config, document_trigger)

    paragraphs = re.split("\n\n", story)
    for paragraph in paragraphs:
        send_eeg_trigger(config, config.trigger_paragraph)

        show_fixation(
            config.fix_cross,
            config.win,
            sec=times["fixation"],
            escape_keys=config.escape_keys,
        )

        words = re.split(r"[\s]", paragraph)
        for n, word in enumerate(words):
            word_trigger = (
                config.trigger_word_even if n % 2 == 0 else config.trigger_word_uneven
            )

            word_time = show_word_fixed(
                word,
                times["rsvp_pr_char"],
                times["rsvp_min"],
                config.text_stim,
                config.win,
                config.escape_keys,
                config,
                word_trigger,
            )
            list_to_csv(
                df_list=[
                    {
                        "reading_type": "RSVP",
                        "reation_time": word_time,
                        "story_name": story_name,
                        "document_id": document_id,
                        "document_trigger": document_trigger,
                        "word": word,
                        "word_n": n,
                        "word_trigger": word_trigger,
                    }
                ],
                out_path=save_path,
                extra_cols=extra_cols,
            )
            show_blackscreen(config.win, times["rsvp_min"])


def text_questions(
    story_name: str,
    document_id: int,
    text_type: str,
    questions_df,
    config,
    save_path: str,
    extra_cols: dict,
):
    send_eeg_trigger(config, config.trigger_questions, reset=True)
    extra_cols["story_name"] = story_name

    scale_question = get_scale_question(story_name, text_type)
    scale_response = show_scale(
        scale_question,
        qtext_stim=config.qtext_stim,
        respondtext=config.respond_stim,
        scale_stim=config.scale_stim,
        win=config.win,
        escape_keys=config.escape_keys,
        question_keys=config.scale_keys + [config.respond_key],
    )
    list_to_csv(
        df_list=[
            {
                "response": scale_response,
                "correct": "NA",
                "document_id": document_id,
                "question_id": 0,
            }
        ],
        out_path=save_path,
        extra_cols=extra_cols,
    )
    qs = questions_df[questions_df["document_id"] == document_id]
    q_responses = show_questions(
        qs,
        config.qtext_stim,
        config.respond_stim,
        config.win,
        config.escape_keys,
        config.question_keys + [config.respond_key],
    )
    list_to_csv(df_list=q_responses, out_path=save_path, extra_cols=extra_cols)


def spr_w_questions(
    story: str,
    story_name: str,
    document_id: int,
    text_type: str,
    questions_df,
    config,
    times: dict,
    full_paths,
    extra_cols: dict,
):
    spr(
        story,
        story_name,
        document_id,
        config,
        times,
        full_paths.save_rt,
        extra_cols,
    )

    text_questions(
        story_name,
        document_id,
        text_type,
        questions_df,
        config,
        full_paths.save_response,
        extra_cols,
    )


def rsvp_w_questions(
    story: str,
    story_name: str,
    document_id: int,
    text_type: str,
    questions_df,
    config,
    times: dict,
    full_paths,
    extra_cols: dict,
):
    rsvp(story, story_name, document_id, times, config, full_paths.save_rt, extra_cols)

    text_questions(
        story_name,
        document_id,
        text_type,
        questions_df,
        config,
        full_paths.save_response,
        extra_cols,
    )


# cloze task
def cloze_task(
    story,
    story_name,
    document_id,
    config,
    save_path,
    extra_cols,
):
    paragraphs = story.split("\n\n")

    text = ""
    response, rt = "NA", "NA"
    n_word = 0
    for paragraph in paragraphs:
        words = re.split(r"[\s]", paragraph)
        for word in words:
            n_word += 1
            list_to_csv(
                df_list=[
                    {
                        "response": response,
                        "reaction_time": rt,
                        "correct_word": word,
                        "document_id": document_id,
                        "story_name": story_name,
                        "number_word": n_word,
                    }
                ],
                out_path=save_path,
                extra_cols=extra_cols,
            )
            text = add_word(text, word)
            response, rt = type_response(
                config.storybox_stim,
                text,
                config.writebox_stim,
                config.stopwatch,
                config.win,
                last_word=(word == words[-1]),
                time_out=6,
            )
        text += "\n\n"


def cloze_scale_question(
    document_id,
    story_name,
    text_type,
    config,
    save_path,
    extra_cols,
):
    scale_question = get_scale_question(story_name, text_type)
    scale_response = show_scale(
        scale_question,
        qtext_stim=config.qtext_stim,
        respondtext=config.respond_stim,
        scale_stim=config.scale_stim,
        win=config.win,
        escape_keys=config.escape_keys,
        question_keys=config.scale_keys + [config.respond_key],
    )
    list_to_csv(
        df_list=[
            {
                "response": scale_response,
                "question": scale_question,
                "document_id": document_id,
                "story_name": story_name,
            }
        ],
        out_path=save_path,
        extra_cols=extra_cols,
    )
