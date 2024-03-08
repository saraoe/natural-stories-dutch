"""
Define config used in the experiments
"""

from psychopy import visual, core, parallel
import os


class exp_config:
    def __init__(
        self,
        fullscreen: bool,
        keys: str,
        cloze: bool = None,
        hand_condition: str = None,
        eeg: bool = None,
    ) -> None:
        self.win = visual.Window(color="grey", fullscr=fullscreen, allowStencil=True)
        self.stopwatch = core.Clock()

        # eeg triggers
        self.eeg = eeg
        self.trigger_exp_start = "exp start"
        self.trigger_pause = "pause"
        self.trigger_questions = "questions"
        self.trigger_word_even = "word even"
        self.trigger_word_uneven = "word uneven"
        self.trigger_paragraph = "paragraph"
        doc_ids = range(1, 13)  # ten texts and two practice texts
        doc_triggers = [f"document {i}" for i in doc_ids]
        self.trigger_documents = {
            doc_id: trigger for doc_id, trigger in zip(doc_ids, doc_triggers)
        }
        self.trigger_wait = 0.45  # in sec
        # parallel port
        if eeg:
            self.port = parallel.ParallelPort(address="/dev/parport0")
            self.port.setData(4)
            self.port.readPin(2)
            self.port.setPin(2, 1)

        # define stim
        self.text_stim = visual.TextStim(win=self.win)
        self.smalltext_stim = visual.TextBox2(
            win=self.win, text="", letterHeight=0.05, size=[1.4, None]
        )
        self.fix_cross = visual.TextStim(win=self.win, text="+", alignText="center")

        # define keys
        if keys == "computer":
            self.respond_key = "return"
            self.respond_key_name = "enter"
            self.escape_keys = ["escape", "q"]
            self.question_keys = ["1", "2", "3", "4"]

        # define question stim
        self.qtext_stim = visual.TextStim(win=self.win)
        self.respond_stim = visual.TextStim(
            win=self.win,
            pos=(0, -0.8),
            text=f"Druk op {self.respond_key_name} om verder te gaan",
        )
        self.scale_stim = visual.Slider(
            win=self.win,
            font="Open Sans",
            labelHeight=0.05,
            ticks=(1, 2, 3, 4, 5),
            labels=[
                "1\nIk heb er nog nooit van gehoord",
                "2\nIk ben er een heel klein beetje bekend mee",
                "3\nIk ben er tot op zekere hoogte bekend mee",
                "4\nIk ben er bekend mee",
                "5\nIk ben er heel bekend mee",
            ],
        )
        self.scale_keys = [str(tick) for tick in self.scale_stim.ticks]
        self.scale_keys.append(self.respond_key)

        # button press text
        if hand_condition:
            # hand condition
            hand_dutch = "linker" if hand_condition == "left" else "rechter"
            self.show_text_ending = (
                f"(Druk op de knop met je {hand_dutch}hand om door te gaan!)"
            )
        else:
            self.show_text_ending = "(Druk op een toets om door te gaan!)"

        # extra config only for cloze
        if cloze:
            self.storybox_stim = visual.TextBox2(
                win=self.win,
                text="",
                pos=(0, 0.1),
                size=[1.4, 1.2],
                letterHeight=0.07,
                lineSpacing=1,
                # overflow="hidden",
                alignment="bottom-left",
                padding=0.07,
            )
            self.writebox_stim = visual.TextBox2(
                win=self.win,
                text="",
                pos=(0, -0.7),
                size=[1, 0.2],
                borderColor="darkgrey",
                letterHeight=0.07,
            )


class exp_paths:
    def __init__(
        self,
        paths: dict,
        experiment: str,
        save_subfix: str,
        tmp_subfix: str,
        hand_condition: str = None,
    ) -> None:
        # general paths
        self.tmp_path = os.path.join(paths["out_data"], f"tmp_{tmp_subfix}.json")
        self.practice_info = os.path.join(paths["instructions"], "practice_info.txt")
        self.practice_end = os.path.join(
            paths["instructions"], f"practice_end_{experiment}.txt"
        )
        self.pause = os.path.join(paths["instructions"], "pause.txt")
        self.end = os.path.join(paths["instructions"], "end.txt")
        self.stories = os.path.join(paths["stories"], "*.txt")

        if experiment == "spr":
            # instructions
            self.inst = os.path.join(paths["instructions"], "eeg_instruction*.txt")
            self.rsvp_inst = os.path.join(
                paths["instructions"], f"rsvp_instructions_{hand_condition}.txt"
            )
            self.practice_text_rsvp = os.path.join(
                paths["stories"], f"practice_text_jorinde_en_joringel.txt"
            )
            self.spr_inst = os.path.join(
                paths["instructions"], f"spr_instructions_{hand_condition}.txt"
            )
            self.practice_text_spr = os.path.join(
                paths["stories"], f"practice_text_de_uil.txt"
            )

            # save paths
            self.save_rt = os.path.join(paths["out_data"], f"rt_{save_subfix}.csv")
            self.save_response = os.path.join(
                paths["out_data"], f"responses_{save_subfix}.csv"
            )

        if experiment == "cloze":
            # instructions
            self.inst = os.path.join(paths["instructions"], "cloze_instruction*.txt")
            self.practice_text = os.path.join(
                paths["stories"], f"practice_text_de_uil.txt"
            )

            # save paths
            self.save_cloze = os.path.join(
                paths["out_data"], f"cloze_{save_subfix}.csv"
            )
            self.save_responses = os.path.join(
                paths["out_data"], f"responses_{save_subfix}.csv"
            )
