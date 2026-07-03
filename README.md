# Tilburg corpus of Natural Dutch Texts (TiNT)

The Tilburg corpus of Natural Dutch Texts (TiNT) is a psycholinguistic corpus of joint electroencephalography (EEG) and self-paced reading (SPR) of natural, medium-length, Dutch texts. The corpus contains recordings from 71 native Dutch speakers reading eight naturally occurring texts of around 600 words each.

## Data availability

The data will be available is available from DataverseNL [here](https://doi.org/10.34894/0O5XQ7).

If you use the corpus please cite the paper and the dataset:
```
@data{
author = {Østergaard, Sara Møller and Lichtenberg, Lenneke and Boon, Laura and Nicenboim, Bruno},
publisher = {DataverseNL},
title = {{EEG and Self-Paced Reading of Natural, Dutch Texts (Towards a computational model of reading (TCMR))}},
year = {2026},
version = {V1},
doi = {10.34894/0O5XQ7},
url = {https://doi.org/10.34894/0O5XQ7}
}

@inproceedings{
  title = {A Corpus of Joint EEG and Self-Paced Reading of Natural Dutch Texts},
  author = {Østergaard, Sara Møller and Lichtenberg, Lenneke Doris and Boon, Laura and Nicenboim, Bruno},
  booktitle = {Proceedings of the Fifteenth Language Resources and Evaluation Conference (LREC 2026)},
  month = {May},
  year = {2026},
  pages = {11260--11271},
  address = {Palma, Mallorca, Spain},
  publisher = {European Language Resources Association (ELRA)},
  editor = {Piperidis, Stelios and Bel, Núria and van den Heuvel, Henk and Ide, Nancy and Krek, Simon and Toral, Antonio},
  doi = {10.63317/49tvxys2q4zc},
}
```

## Organization

This repository includes three parts: stimuli, experiment, and paper. 

- The ``stimuli/`` folder contains the linguistic stimuli as well as the code for generating descriptive statistics of the stimuli and extracting log-prababilities, word frequencies. 
- The ``experiment/`` folder contains the psychopy script used for collecting the EEG and behavioral data. The experiment also relies on the stimuli that is within the stimuli folder.
- The ``paper/`` folder contains the code for validation analysis of the data. This includes preproccessing, extracting ERP components, running Bayesian hierarchical models, and summaries and plots for the paper (excluding the plots of descriptive statistics of the stimuli, which is in the stimuli folder).

Inside the three folders are ``README.md`` files explaining how to run the code. *NB: Different environments are needed for the different parts.*