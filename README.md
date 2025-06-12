# Tilburg corpus of Natural Dutch Texts (TiNT)

The Tilburg corpus of Natural Dutch Texts (TiNT) is a psycholinguistic corpus of joint electroencephalography (EEG) and self-paced reading (SPR) of natural, medium-length, Dutch texts. The corpus contains recordings from 71 native Dutch speakers reading eight naturally occurring texts of around 800 words each.

## Data availability

The data will be available on DataverseNL.

If you use the corpus please cite:
[Paper and DataverseNL citation will be added]

## Organization

This repository includes three parts: stimuli, experiment, and paper. 

- The **stimuli** folder contains the linguistic stimuli as well as the code for generating descriptive statistics of the stimuli and extracting log-prababilities, word frequencies. 
- The **experiment** folder contains the psychopy script used for collecting the EEG and behavioral data. The experiment also relies on the stimuli that is within the stimuli folder.
- The **paper** folder contains the code for validation analysis of the data. This includes preproccessing, extracting ERP components, running Bayesian hierarchical models, and summaries and plots for the paper (excluding the plots of descriptive statistics of the stimuli, which is in the stimuli folder).

*NB: different environments are used for the different parts. Look at the readmes within the folders for more information.*