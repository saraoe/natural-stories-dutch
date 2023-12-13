"""
Questionnaire in the beginning of experiment.
Include Participant ID, demographics, and language ability 
"""
from psychopy import core, gui, data
import string
import os, json, glob


def add_info(old_info: dict, new_info: dict):
    for key, value in new_info.items():
        old_info[key] = value
    return old_info


def required_field(s: str):
    return s + "*"


def check_id(participant_id: str):
    if len(participant_id) != 5:
        return False
    letters = list(string.ascii_lowercase)
    digits = list(string.digits)
    for n, char in enumerate(participant_id, start=1):
        if n <= 3 and char not in letters:
            return False
        if 3 < n <= 5 and char not in digits:
            return False
    return True


def check_list(response_list):
    return all([r != "-" for r in response_list])


def participant_id_gui():
    # participant number (for determining hand and condition)
    hand_d = {n: hand for n, hand in zip(range(4), ["left", "left", "right", "right"])}
    cond_d = {n: cond for n, cond in zip(range(4), [1, 7, 1, 7])}

    dlg = gui.Dlg(title="Participant Number")
    dlg.addText("Please let the experimenter fill out you participant number")
    dlg.addField(required_field("Participant Number"), choices=range(1, 200))
    dlg.show()

    if dlg.OK:
        participant_number = dlg.data[0]

        participant_info = {
            "participant_number": participant_number,
            "hand": hand_d[participant_number % 4],
            "rsvp_document_id": cond_d[participant_number % 4],
        }
    else:
        core.quit()

    # participant id
    missing_id = True
    while missing_id:
        dlg = gui.Dlg(title="Participant ID")
        q_text = """We willen je vragen om je eigen unieke experimentele ID te creëren.\nJe creëert je experimentele ID (bestaande uit 3 letters en 2 cijfers) op de volgende manier:

        1. De eerste letter van de voornaam van je moeder
        2. De tweede letter van de voornaam van je vader
        3. De derde letter van je eigen naam
        4. De laatste twee cijfers van je telefoonnummer

        Bijv. ABC12
        """
        dlg.addText(q_text)
        dlg.addField(required_field("Participant ID"))
        dlg.show()

        if dlg.OK:
            participant_id = dlg.data[0].lower()
            if check_id(participant_id):
                missing_id = False
                participant_info["participant_id"] = participant_id
        else:
            core.quit()

    return participant_info


def demographics_gui():
    missing_demographics = True
    dlg = gui.Dlg(title="Demographics")
    dlg.addField(
        required_field("Geslacht"),
        choices=["-", "Man", "Vrouw", "Non-binair", "Geef ik liever niet aan"],
    )
    dlg.addField(required_field("Leeftijd"), choices=["-"] + list(range(18, 100)))
    dlg.addField(
        required_field("Wat is je hoogst afgeronde opleiding?"),
        choices=[
            "-",
            "Ik heb geen opleiding afgerond",
            "Basisschool",
            "Vmbo",
            "Havo",
            "Vwo",
            "Mbo",
            "Hbo bachelor",
            "Hbo master",
            "Wo bachelor",
            "Wo master",
            "Phd",
            "Anders",
        ],
    )
    dlg.addText(
        "\nIf you responded Anders in the last question, please name your highest finished educations"
    )
    dlg.addField("Namelijk")
    while missing_demographics:
        dlg.show()

        if dlg.OK:
            gui_info = dlg.data
            if not check_list(gui_info):
                continue

            demographics = {
                field: value
                for field, value in zip(["gender", "age", "education"], gui_info)
            }

            if demographics["education"] == "Anders":
                demographics["education"] = gui_info[3]
                if demographics["education"] == "":
                    continue

            missing_demographics = False

        else:
            core.quit()

    return demographics


def lang_ability_gui():
    # general language abilities
    degree_choices = [
        "-",
        "Geen problemen",
        "Een klein beetje",
        "Regelmatig",
        "Vaak",
        "Heel vaak",
    ]
    time_choices = [
        "-",
        "Minder dan 1 uur per week",
        "1 tot 3 uur per week",
        "3 tot 6 uur per week",
        "7 tot 10 uur per week",
        "Meer dan 10 uur per week",
    ]

    dlg = gui.Dlg(title="Language Ability")
    dlg.addField(
        required_field("Heb je problemen met lezen in het Nederlands?"),
        choices=degree_choices,
    )
    dlg.addField(
        required_field(
            "Hoeveel uur per week lees je gemiddeld in het Nederlands\nvoor school/werk (boeken, tijdschriften, kranten, internet)?"
        ),
        choices=time_choices,
    )
    dlg.addField(
        required_field(
            "Hoeveel uur per week lees je gemiddeld in het Nederlands\nin je vrije tijd (boeken, tijdschriften, kranten, internet)?"
        ),
        choices=time_choices,
    )
    dlg.addField(
        required_field("Heb je problemen met spelling in het Nederlands?"),
        choices=degree_choices,
    )
    dlg.addField(
        required_field(
            "Hoeveel uur per week schrijf je gemiddeld in het Nederlands \n(sociale media, e-mail, brieven, dagboek, school/werk opdrachten etc.)?"
        ),
        choices=time_choices,
    )
    dlg.addField(
        required_field(
            "Kun je beter in het Nederlands lezen of in (een) andere taal/talen"
        ),
        choices=[
            "-",
            "Ik lees beter in het Nederlands",
            "Ik lees beter in (een) anderen taal/talen",
            "Ik lees even goed in het Nederlands als in (een) andere taal/talen",
        ],
    )
    dlg.addText(
        "\nIf you responded\n - Ik lees beter in (een) anderen taal/talen or\n - Ik lees even goed in het Nederlands als in (een) andere taal/talen \nin the last question, please name the language"
    )
    dlg.addField("Namelijk")

    missing_la = True
    while missing_la:
        dlg.show()

        if dlg.OK:
            gui_info = dlg.data
            if not check_list(gui_info):
                continue

            info_cols = [
                "problem_reading",
                "read_school_or_work_pr_week",
                "read_freetime_pr_week",
                "problem_spelling",
                "write_pr_week",
                "best_reading_language",
            ]
            lang_abililty = {field: value for field, value in zip(info_cols, gui_info)}

            if (
                lang_abililty["best_reading_language"]
                == "Ik lees beter in het Nederlands"
            ):
                lang_abililty["best_reading_language_named"] = "dutch"
            else:
                lang_abililty["best_reading_language_named"] = gui_info[-1]
                if lang_abililty["best_reading_language_named"] == "":
                    continue

            missing_la = False

        else:
            core.quit()

    # speak_languages
    n = 5
    dlg = gui.Dlg(title="Language Ability")
    dlg.addText(
        "Welke talen spreek je?\n\nNote: if you don't speak any other languages than Dutch, you can leave all fields blank."
    )
    for i in range(1, n + 1):
        dlg.addText(f"{i}:")
        dlg.addField("Taal")
        dlg.addField("Wanneer geleerd?")
        dlg.addField("Vloeiend?", choices=["ja", "nee"])

    missing_lang = True
    while missing_lang:
        dlg.show()

        if dlg.OK:
            lang_abililty["other_languages"] = {}
            gui_info = dlg.data

            for i in [x * 3 for x in range(n)]:
                lang = gui_info[i]
                if lang:
                    # check that the other fields are filled
                    if not gui_info[i + 1] or not gui_info[i + 2]:
                        missing_lang = True
                    else:
                        lang_abililty["other_languages"][lang] = {
                            "learned": gui_info[i + 1],
                            "fluent": gui_info[i + 2],
                        }
                        missing_lang = False

            if not lang_abililty["other_languages"]:  # not other languages than dutch
                missing_lang = False

        else:
            core.quit()

    return lang_abililty


def existing_gui_info(out_path: str, subfix: str):
    tmp_path = glob.glob(os.path.join(out_path, f"tmp_{subfix}.json"))
    if tmp_path:
        dlg = gui.Dlg(title="Continue Experiment?")
        dlg.addField(
            "Do you want to jump into experiment,\n where you ended?",
            choices=["yes", "no"],
        )
        dlg.show()

        if dlg.OK:
            cont_crash = True if dlg.data[0] == "yes" else None
            if cont_crash:
                tmp_path = tmp_path[0]
        else:
            core.quit()

    return tmp_path


def exp_questionnaire(
    out_path: str,
    participant_id: bool = True,
    demographics: bool = True,
    lang_ability: bool = True,
):
    gui_info = {}

    if participant_id:
        gui_info = add_info(gui_info, participant_id_gui())

    # use participant id to make subfix
    date = data.getDateStr()
    save_subfix = (
        f"{gui_info['participant_id']}_{gui_info['participant_number']}_{date}"
    )
    gui_info["participant_subfix"] = save_subfix

    # check if tmp_file exists
    tmp_path = existing_gui_info(
        out_path,
        subfix=f"{gui_info['participant_id']}_{gui_info['participant_number']}*",
    )
    if tmp_path:
        with open(tmp_path) as f:
            tmp_file = json.load(f)
        return tmp_file["gui_information"], tmp_file

    if demographics:
        gui_info = add_info(gui_info, demographics_gui())
    gui_info_returned = (
        gui_info  # only participant id and demographics should be returned
    )

    if lang_ability:
        gui_info = add_info(gui_info, lang_ability_gui())

    save_path = os.path.join(out_path, f"participant_info_{save_subfix}.json")
    with open(save_path, "w") as fp:
        json.dump(gui_info, fp)

    return gui_info_returned, None
