# Self-Paced Reading EEG experiment

Experiment for the Self-Paced Reading (SPR) EEG study.


## Organization
```
├── README.md
├── requirements.txt
├── instructions                <- txt-files with written intructions
├── data                        <- data collected during experiment
├── questions.xlsx              <- comprehension question for SPR experiment
├── src
│   ├──  self-paced_reading.py  <- psychopy script of SPR experiment
│   ├──  cloze.py               <- psychopy script of cloze task
│   └── ...
```

## Run experiment
To run the experiment, you first have to make a virtualenv with python version 3.8. Then you can run ```pip install -r requirements.txt``` to install the correct version of PsychoPy. 

To run the Self-Paced Reading experiment:
```
python src/self-paced_reading.py
```

To run Cloze Task experiment
```
python src/cloze_task.py
```