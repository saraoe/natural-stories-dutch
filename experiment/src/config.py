"""
Define config used in the experiments
"""
from psychopy import visual, core
import os
import numpy as np


def make_arrows(direction: str, textbox, win):
    if direction == "up":
        v = np.array([[0, 1], [-0.5, 0], [0.5, 0]])
    if direction == "down":
        v = np.array([[0, -1], [-0.5, 0], [0.5, 0]])
    arrow = visual.ShapeStim(
        win=win,
        vertices=v,
        size=textbox.size / 8,
    )
    if direction == "up":
        arrow.pos = (
            textbox.pos[0] + textbox.size[0] / 2 + arrow.size[0],
            textbox.pos[1] + arrow.size[1],
        )
    else:
        arrow.pos = (
            textbox.pos[0] + textbox.size[0] / 2 + arrow.size[0],
            textbox.pos[1] - arrow.size[1],
        )
    return arrow


class exp_config:
    def __init__(self, fullscreen: bool, keys: str) -> None:
        self.win = visual.Window(color="grey", fullscr=fullscreen)
        self.stopwatch = core.Clock()

        # define stim
        self.text_stim = visual.TextStim(win=self.win)
        self.smalltext_stim = visual.TextStim(win=self.win)
        self.smalltext_stim.size = 0.05
        self.fix_cross = visual.TextStim(win=self.win, text="+", alignText="center")

        # define keys
        if keys == "computer":
            self.respond_key = "return"
            self.escape_keys = ["escape", "q"]
            self.question_keys = ["1", "2", "3", "4"]

        # define question stim
        self.qtext_stim = visual.TextStim(win=self.win)
        self.respond_stim = visual.TextStim(
            win=self.win, pos=(0, -0.8), text=f"Press {self.respond_key} to respond"
        )
        self.scale_stim = visual.Slider(
            win=self.win,
            font="Open Sans",
            labelHeight=0.05,
            ticks=(1, 2, 3, 4, 5),
            labels=[
                "1\nIk heb er nog nooit van gehoord",
                "2\nIk ben er een heel klein beetje bekend meel",
                "3\nIk ben er tot op zekere hoogte bekend mee",
                "4\nIk ben er bekend mee",
                "5\nIk ben er heel bekend mee",
            ],
        )
        self.scale_keys = [str(tick) for tick in self.scale_stim.ticks]
        self.scale_keys.append(self.respond_key)


class exp_paths:
    def __init__(self, paths: dict, experiment: str, save_subfix: str) -> None:
        # general paths
        self.practice_info = os.path.join(paths["instructions"], "practice_info*.txt")
        self.practice_end = os.path.join(paths["instructions"], "practice_end*.txt")
        self.pause = os.path.join(paths["instructions"], "pause.txt")
        self.end = os.path.join(paths["instructions"], "end.txt")
        self.stories = paths["stories"]

        if experiment == "spr":
            self.inst_path = os.path.join(paths["instructions"], "eeg_instruction*.txt")
            self.rsvp_inst = os.path.join(
                paths["instructions"], "rsvp_instructions*.txt"
            )
            self.practice_text_rsvp = os.path.join(
                paths["instructions"], f"practice_text_rsvp.txt"
            )
            self.spr_inst = os.path.join(paths["instructions"], "spr_instructions*.txt")
            self.practice_text_spr = os.path.join(
                paths["instructions"], f"practice_text_spr.txt"
            )

            self.tmp_path = os.path.join(paths["out_data"], f"tmp_{save_subfix}.json")

            self.save_rt = os.path.join(paths["out_data"], f"rt_{save_subfix}.csv")
            self.save_response = os.path.join(
                paths["out_data"], f"responses_{save_subfix}.csv"
            )

        if experiment == "cloze":
            pass
