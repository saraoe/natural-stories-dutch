"""
Questionnaire in the beginning of experiment.
Include Participant ID, demographics, and language ability 
"""

from psychopy import core, gui
from datetime import date
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


def participant_id_gui(exp: str):
    # conditions
    if exp == "spr":
        # participant number for determining hand and rsvp condition
        hand_d = {
            n: hand for n, hand in zip(range(4), ["left", "left", "right", "right"])
        }
        rsvp_d = {
            n: rsvp_id for n, rsvp_id in zip(range(4), [1, 5, 1, 5])
        }  # mijn heer + permafrost
    if exp == "cloze":
        # participant number for determining which texts
        lists = [[1, 3], [2, 5], [4, 6], [7, 8]]  # i.e., two texts in every list
        lists += [l[::-1] for l in lists]  # reversed order
        doc_id_d = {n: ids for n, ids in enumerate(lists)}

    missing_n = True
    while missing_n:
        dlg = gui.Dlg(title="Participantnummer")
        dlg.addText("Laat de onderzoeker je participantnummer invullen")
        dlg.addField(
            required_field("Participantnummer"), choices=["-"] + list(range(1, 200))
        )
        dlg.show()

        if dlg.OK:
            participant_number = dlg.data[0]
            if check_list([participant_number]):
                missing_n = False
                participant_info = {"participant_number": participant_number}

                if exp == "spr":
                    participant_info["hand"] = hand_d[participant_number % 4]
                    participant_info["rsvp_document_id"] = rsvp_d[
                        participant_number % 4
                    ]
                if exp == "cloze":
                    participant_info["included_documents"] = doc_id_d[
                        participant_number % len(doc_id_d)
                    ]
        else:
            core.quit()

    # participant id
    missing_id = True
    while missing_id:
        dlg = gui.Dlg(title="Participant ID")
        q_text = """Creëer je eigen unieke participant ID (bestaande uit 3 letters en 2 cijfers). Je doet dit op de volgende manier:

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
    dlg = gui.Dlg(title="Demografische gegevens")
    dlg.addField(
        required_field("Geslacht"),
        choices=["-", "Man", "Vrouw", "Non-binair", "Geef ik liever niet aan"],
    )
    dlg.addField(required_field("Leeftijd"), choices=["-"] + list(range(18, 100)))
    dlg.addField(
        required_field("Wat is je huidige of hoogst genoten opleiding?"),
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
        "\nAls je “Anders” hebt geantwoord op de vorige vraag, kun je dit toelichten"
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

    dlg = gui.Dlg(title="Nederlandse taalvaardigheid")
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
        """\nAls je op de vorige vraag een van de volgende antwoorden hebt gegeven, noem dan dan deze taal/talen 
        - Ik lees beter in (een) anderen taal/talen of
        - Ik lees even goed in het Nederlands als in (een) andere taal/talen"""
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
                lang_abililty["best_reading_language_named"] = "nederlands"
            else:
                lang_abililty["best_reading_language_named"] = gui_info[-1]
                if lang_abililty["best_reading_language_named"] == "":
                    continue

            missing_la = False

        else:
            core.quit()

    # speak_languages
    n = 5
    dlg = gui.Dlg(title="Taalvaardigheid")
    dlg.addText(
        "Welke talen spreek je?\n\nOpmerking: als je geen andere talen spreekt dan Nederlands, kun je alle velden leeg laten."
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
        dlg = gui.Dlg(title="Experiment voortzetten?")
        dlg.addField(
            "Wil je verdergaan met het experiment waar je bent geëindigd?",
            choices=["ja", "nee"],
        )
        dlg.show()

        if dlg.OK:
            cont_crash = True if dlg.data[0] == "ja" else None
            if cont_crash:
                tmp_path = tmp_path[0]
            else:
                tmp_path = None
        else:
            core.quit()

    return tmp_path


def exp_questionnaire(
    out_path: str,
    exp: str,
    participant_id: bool = True,
    demographics: bool = True,
    lang_ability: bool = True,
    return_info: list = [
        "participant_number",
        "hand",
        "rsvp_document_id",
        "included_documents",
        "participant_id",
        "participant_subfix",
        "gender",
        "age",
        "education",
    ],
):
    gui_info = {}

    if participant_id:
        gui_info = add_info(gui_info, participant_id_gui(exp))

    # use participant id to make subfix
    date_str = str(date.today())
    save_subfix = (
        f"{gui_info['participant_id']}_{gui_info['participant_number']}_{date_str}_s1"
    )
    gui_info["participant_subfix"] = save_subfix

    # check if tmp_file exists
    tmp_path = existing_gui_info(
        out_path,
        subfix=save_subfix,
    )
    if tmp_path:
        with open(tmp_path) as f:
            tmp_file = json.load(f)
        return tmp_file["gui_information"], tmp_file

    if demographics:
        gui_info = add_info(gui_info, demographics_gui())

    if lang_ability:
        gui_info = add_info(gui_info, lang_ability_gui())

    save_path = os.path.join(out_path, f"participant_info_{save_subfix}.json")
    with open(save_path, "w") as fp:
        json.dump(gui_info, fp)

    gui_info_returned = {
        key: gui_info[key] for key in return_info if key in gui_info.keys()
    }

    return gui_info_returned, None
