# SPR-EEG Data 

```
├── README.md
├── mean_amplitude.csv  
├── erp_lp.csv 
├── exclude.xlsx    
├── spr
│   └── ...     <- files from SPR-EEG experiment
├── cloze
│   └── ...     <- files from Cloze Task
├── epochs
    └── ...     <- epochs after preprocessing
└── erps
    └── ...     <- erps for every participant

```

## Mean amplitude and ERPs
The csv-file ``mean_amplitude.csv`` contains the mean amplitude for specific channels in a specific time window (see table). The mean amplitudes are created in ``src/summarize_eeg.r``.

| colname | channels | time window | 
| --- | --- | --- |
| n170 | O1, Oz, O2 | 160-210 ms |
| n400 | Cz, Pz, C4, CP6, P4, P3, CP5, C3, P8, PO3, PO4, P7 | 300-500 ms |
| p600 | Cz, CP2, Pz, CP1, C4, CP6, P4, P3, CP5, C3, T8, TP8, P8, PO4, PO3, P7, TP7, T7 | 500-700 ms |

The csv-file ``erp_lp.csv`` is made in ``src/summarize_erps.r`` and relies on the files from the ``erps/`` folder, which is created in ``src/summarize_eeg.r``. This file contains ERPs averaged for three different conditions: *high_lp* (log-probability of word in highest quartile), *low_lp* (log-probability of word in lowest quartile), and *med_lp* (words with log-probability between lowest and highest quartile). These ERPs have been averaged for trials with SPR, RSVP or both (indicated by the ``reading_type`` column) for either all words (``.value``) or only content words (``.value_content_words``). The log-probability quantiles are calculated separately for all words and only content words, making sure that *high_lp* and *low_lp* were calculated from an equal amount of datapoints.


## SPR EEG

For each participant there are two seperate csv-files, one json-file, and one bdf-file.

- reaction times: ```rt_*.csv```
- responses: ```responses_*.csv```
- participant information: ```participant_info_*.json```
- eeg data from Bio-Semi: ``TCMR_EGG_*.bdf``

All files except the EEG-file have the same subfix of filename, indicating the partipant id, participant number, date of data collection, and session. The subfix of the EEG-file is the participant number.

If the file end with ```_sn``` where n > 1, this indicates that the experiment crashed during data collection, and this is the data collected during the n'th session. Thus, there will for this participant exist n versions of every file.

The **reation times** file include the following columns:
- reading_type: (str) indicates whether reading was excuted in SPR or RSVP framework
- reaction_time: (float) in seconds (for SPR it is reaction time, for RSVP it is the time the word was present)
- story_name: (str) name of the story
- document_id: (int)
- timestamp_buttonpress: (float) timestamp of the buttonpress in seconds
- document_trigger: (str) eeg trigger for the unique document
- word: (str)
- word_n: (int) word number
- paragraph_n: (int) paragraph number
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

Trigger codes for the **EEG data**:
| Trigger | Trigger Code |
| --- | --- |
| Start Experiment | 201 |
| Pause | 202 |
| Questions | 203 |
| Start Document | Document ID | 
| Paragraph | 103 |
| Word (uneven) | 101 |
| Word (even) | 102 |

## Cloze Task
For each participant in the cloze task experiment, two csv-file and one json-file are saved 

- The main file (with responded word and reaction times): ```cloze_*.csv```
- Responses of scale questions: ```responses_*.csv```
- Participant information: ```participant_info_*.json```

The subfix of the filename is created similarly to those for the SPR experiment (i.e. partipant id, participant number, date of data collection, and session).

If the file end with ```_sn``` where n > 1, this indicates that the experiment crashed during data collection, and this is the data collected during the n'th session. Thus, there will for this participant exist n versions of every file.

The main **cloze** file includes the following columns:
- response: (str) the two words the participant responded with (seperated by whitespace)
- reaction_time: (flot) time it took to respond
- story_name: (str) name of the story
- correct_word: (str) the correct word (i.e. if the participant responded correctly, this should correpond with the first of the words in the *response* column)
- number_word: (int) Number of the word in the story
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

## Epochs and ERPs
In the ``epochs/`` folder, epochs created in the ``src/preprocessing.r`` are saved as RDS-files. Every files is epochs from a single participant, and the name is the participant number.

In the ``erps/`` folder, erps created on ``src/summarize_eeg.r`` are saved as csv-files. Every files is erps from a single participant, and the name indicates the participant number. The file contains averaged EEG signal from all channels in three conditions (high, med, and low log-probability) for the two presentation rates (SPR and RSVP) separately. A value for all words and a value for only content words are calculated. See *Mean amplitude and ERPs* above for a more in depth explanation.