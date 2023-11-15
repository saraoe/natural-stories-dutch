# Data collected during experiment

## SPR EEG

For each participant, two seperate csv-files are saved during the SPR-experiment:

- reaction times: ```rt_*.csv```
- responses: ```responses_*.csv```

Both files have the same ending in the filename, indicating the partipant id, date of data collection, and a random string of characters (that are the same for the same participant). 

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
