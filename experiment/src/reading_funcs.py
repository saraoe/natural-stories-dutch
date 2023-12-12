"""
Functions for self-paced reading (SPR) and rapid series visual representation (RSVP)
"""
import re
from util import list_to_csv, make_lines, read_text, get_scale_question
from show_stim import (
    show_blackscreen,
    show_fixation,
    show_word,
    show_word_fixed,
    show_text,
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
    paragraphs = re.split("\n\n", story)

    for paragraph in paragraphs:
        show_fixation(
            config.fix_cross,
            config.win,
            sec=times["fixation"],
            escape_keys=config.escape_keys,
        )
        words = re.split(r"[\s]", paragraph)
        for word in words:
            rt = show_word(
                word, config.text_stim, config.win, config.stopwatch, config.escape_keys
            )
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

            show_blackscreen(config.win, sec=times["blackscreen_short"])
    show_blackscreen(config.win, sec=times["blackscreen_long"])


def rsvp(story: str, times, config):
    paragraphs = re.split("\n\n", story)

    for paragraph in paragraphs:
        show_word_fixed(
            "+",
            times["fixation"] - 0.02,
            times["fixation"],
            config.text_stim,
            config.win,
            config.escape_keys,
        )

        words = re.split(r"[\s]", paragraph)
        for word in words:
            show_word_fixed(
                word,
                times["rsvp_pr_char"],
                times["rsvp_min"],
                config.text_stim,
                config.win,
                config.escape_keys,
            )
            show_blackscreen(config.win, times["rsvp_min"])


def text_questions(
    story_name: str,
    document_id: int,
    questions_df,
    config,
    save_path: str,
    extra_cols: dict,
):
    scale_question = get_scale_question(document_id, story_name)
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
        questions_df,
        config,
        full_paths.save_response,
        extra_cols,
    )


def rsvp_w_questions(
    story: str,
    story_name: str,
    document_id: int,
    questions_df,
    config,
    times: dict,
    full_paths,
    extra_cols: dict,
):
    rsvp(story, times, config)

    text_questions(
        story_name,
        document_id,
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
                        "story_name": story_name,
                    }
                ],
                out_path=save_path,
                extra_cols=extra_cols,
            )
            lines = make_lines(lines, word, config.maxchar_pr_line)
            response, rt = type_response(
                config.storybox_stim,
                lines,
                config.max_lines,
                config.up_arrow,
                config.down_arrow,
                config.writebox_stim,
                config.stopwatch,
                config.win,
            )
        lines.append("\n")


def cloze_scale_question(
    document_id,
    story_name,
    config,
    save_path,
    extra_cols,
):
    scale_question = get_scale_question(document_id, story_name)
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
