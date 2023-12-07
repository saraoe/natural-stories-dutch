# Data collected during experiment

```
├── README.md
├── spr
│   └── ...     <- csv-files from SPR EEG experiment
├── cloze
│   └── ...     <- csv-files from Cloze Task

```

## SPR EEG

For each participant, two seperate csv-files are saved during the SPR-experiment:

- reaction times: ```rt_*.csv```
- responses: ```responses_*.csv```

Both files have the same subfix of filename, indicating the partipant id, date of data collection, and a random string of characters (that are the same for the same participant). 

If the file end with ```_s2``` this indicates that the experiment crashed during data collection, and this is the data collected during the the second session. Thus, there will for this participant exist two version of every file.

The **reation times** file include the following columns:
- reation_time: (numeric) in seconds
- document_id: (int)
- word: (character)
- participant_id: (int)
- age: (int)
- gender: (character)

The **response** file are the responses to the questions in the ```../questions.xlsx``` file. The file includes the following columns:
- response: (character) the answer the participant chose (indicated by the letter of the response, i.e. a, b,, c, or d)
- correct: (int) indicate if the response was correct
- document_id: (int)
- question_id: (int)
- participant_id: (int)
- age: (int)
- gender: (character)

## Cloze Task
For each participant in the cloze task experiment, two csv-file are saved 

- The main file (with responded word and reaction times): ```cloze_*.csv```
- Responses of scale questions: ```responses_*.csv```

The subfix of the filename is created similarly to those for the SPR experiment (i.e. partipant id, date of data collection, and a random string of characters)

The main **cloze** file includes the following columns:
- response: (str) the two words the participant responded with (seperated by whitespace)
- story: (str) name of the story
- correct_word: (str) the correct word (i.e. if the participant responded correctly, this should correpond with the first of the words in the *response* column)
- participant_id: (int)
- age: (int)
- gender: (character)

The **responses** files includes the following columns:
- response: (int) the response on a 5-scale
- question: (str) the formulation of the question they were asked
- document_id: (int)
- participant_id: (int)
- age: (int)
- gender: (character)