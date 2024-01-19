# Data collected during experiments

```
├── README.md
├── spr
│   └── ...     <- files from SPR EEG experiment
├── cloze
│   └── ...     <- files from Cloze Task

```

## SPR EEG

For each participant, two seperate csv-files and one json-file are saved during the SPR-experiment:

- reaction times: ```rt_*.csv```
- responses: ```responses_*.csv```
- participant information: ```participant_info_*.json```

All files have the same subfix of filename, indicating the partipant id, participant number, date of data collection, and session. 

If the file end with ```_sn``` where n > 1, this indicates that the experiment crashed during data collection, and this is the data collected during the n'th session. Thus, there will for this participant exist n versions of every file.

The **reation times** file include the following columns:
- reading_type: (str) indicates whether reading was excuted in SPR or RSVP framework
- reation_time: (numeric) in seconds (for SPR it is reaction time, for RSVP it is the time the word was present)
- story_name: (str) name of the story
- document_id: (int)
- document_trigger: (str) eeg trigger for the unique document
- word: (str)
- word_trigger: (str) eeg trigger sent for the word (alternating)
- participant_id: (int)

The **response** file are the responses to the questions in the ```../questions.xlsx``` file. The file includes the following columns:
- response: (str) the answer the participant chose (indicated by the letter of the response, i.e. a, b,, c, or d)
- correct: (int) indicate if the response was correct
- story_name: (str) name of the story
- document_id: (int)
- question_id: (int)
- participant_id: (int)

*Note: Both csv-files also include all participant information except the questions related to language abilities.*

The **participant information** file include the following information:
- Participant identification:
    - participant_number: (int) number assigned to the participant by the experimenter, that determines hand and RSVP text 
    - hand: (str) which hand the participant was instructed to use (i.e., left or right) 
    - rsvp_document_id: (int) document id of the the text showed in RSVP 
    - participant_id: (str) 
    - participant_subfix: (str) subfix of all files related to this participant
- Demographics:
    - gender: (str) 
    - age: (int) 
    - education": (str) highest finished education, 
- Dutch language ability
    - problem_reading: (str) *Heb je problemen met lezen in het Nederlands?* 
    - read_school_or_work_pr_week: (str) *Hoeveel uur per week lees je gemiddeld in het Nederlands voor school/werk (boeken, tijdschriften, kranten, internet)?* 
    - read_freetime_pr_week: (str) *Hoeveel uur per week lees je gemiddeld in het Nederlands in je vrije tijd (boeken, tijdschriften, kranten, internet)?* 
    - problem_spelling: (str) *Heb je problemen met spelling in het Nederlands?*
    - write_pr_week: (str) *Hoeveel uur per week schrijf je gemiddeld in het Nederlands (sociale media, e-mail, brieven, dagboek, school/werk opdrachten etc.)?*  
    - best_reading_language: (str) *Kun je beter in het Nederlands lezen of in (een) andere taal/talen*
    - best_reading_language_named: (str) Name of the language the participant reads the best in
    - other_languages: (Dict[Dict[str or int]]) dictionary with other languages the participant speaks (keys) and when they learned and whether they speak in fluently or not (values)

## Cloze Task
For each participant in the cloze task experiment, two csv-file and one json-file are saved 

- The main file (with responded word and reaction times): ```cloze_*.csv```
- Responses of scale questions: ```responses_*.csv```
- Participant information: ```participant_info_*.json```

The subfix of the filename is created similarly to those for the SPR experiment (i.e. partipant id, participant number, date of data collection, and session).

If the file end with ```_sn``` where n > 1, this indicates that the experiment crashed during data collection, and this is the data collected during the n'th session. Thus, there will for this participant exist n versions of every file.

The main **cloze** file includes the following columns:
- response: (str) the two words the participant responded with (seperated by whitespace)
- story_name: (str) name of the story
- correct_word: (str) the correct word (i.e. if the participant responded correctly, this should correpond with the first of the words in the *response* column)
- participant_id: (int)

The **responses** files includes the following columns:
- response: (int) the response on a 5-scale
- question: (str) the formulation of the question they were asked
- story_name: (str) name of the story
- document_id: (int)
- participant_id: (int)

*Note: Both csv-files also include all participant information except the questions related to language abilities.*

The **participant information** file include the following information:
- Participant identification:
    - participant_number: (int) number assigned to the participant by the experimenter, that determines hand and RSVP text 
    - included_documents: (list) list of documents included in the experiment (the list is ordered). *NB: this variable is not included in the csv-files*
    - participant_id: (str) 
    - participant_subfix: (str) subfix of all files related to this participant
- Demographics:
    - gender: (str) 
    - age: (int) 
    - education": (str) highest finished education, 
- Dutch language ability
    - problem_reading: (str) *Heb je problemen met lezen in het Nederlands?* 
    - read_school_or_work_pr_week: (str) *Hoeveel uur per week lees je gemiddeld in het Nederlands voor school/werk (boeken, tijdschriften, kranten, internet)?* 
    - read_freetime_pr_week: (str) *Hoeveel uur per week lees je gemiddeld in het Nederlands in je vrije tijd (boeken, tijdschriften, kranten, internet)?* 
    - problem_spelling: (str) *Heb je problemen met spelling in het Nederlands?*
    - write_pr_week: (str) *Hoeveel uur per week schrijf je gemiddeld in het Nederlands (sociale media, e-mail, brieven, dagboek, school/werk opdrachten etc.)?*  
    - best_reading_language: (str) *Kun je beter in het Nederlands lezen of in (een) andere taal/talen*
    - best_reading_language_named: (str) Name of the language the participant reads the best in
    - other_languages: (Dict[Dict[str or int]]) dictionary with other languages the participant speaks (keys) and when they learned and whether they speak in fluently or not (values)