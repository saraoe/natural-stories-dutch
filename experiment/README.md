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
│   ├──  cloze_task.py          <- psychopy script of cloze task
│   └── ...
```

## To install dependencies

```
conda env create -f environment.yml
```

or create a python environment with Python 3.8.1 and pip install requirements.

```
pip install -r requirements.txt
```

## Run experiment
To run the Self-Paced Reading experiment:
```
conda activate expt            
python src/self-paced_reading.py
```

To run Cloze Task experiment
```
conda activate expt            
python src/cloze_task.py
```
