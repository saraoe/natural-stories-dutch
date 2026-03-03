# Event-Related Potentials of Surprisal in Self-Paced Reading

This study aims to explore the neural correlates of surprisal and the connections to reading times relying on data from self-paced reading (SPR). 

## Pipeline
| Step | File | Output folder |
| --- | --- | --- |
| Preprocessing | ``src/preprocessing.r`` | epochs saved in ``data/epochs/`` and plots of artifacts in ``figs/preprocessing/`` |
| Summarize epochs and create ERPs | ``src/summarize_eeg.r`` | csv-files with mean amplitudes ``data/`` and ERPs in ``data/erps`` |
| Models and plots | ``src/analysis.r  --rt=TRUE --n400=TRUE --p600=TRUE`` | models saved in ``src/brms_models/`` |

## Reproduce analysis

### Download corpus
The data on which the analysis was run can be downloaded from the Dataverse-NL repositiory [here](https://doi.org/10.34894/0O5XQ7).

From the repository, it is possible to download the raw EEG data and the preprocessed EEG data. If you don't want to run preprocessing, you can download the files in the ``Supplemental material/Preprocessed data/`` folder in the Dataverse-NL repository (*mean_amplitude.csv*, *rt_eeg_triggers.csv*, and *erp_lp.csv*) and place them in the ``paper/data/`` folder of the current repository. From these files, you will be able to run the regression models in ``paper/src/analysis.r`` as well as reproduce results in the ``paper/results/`` folder. If you also want to replicate the results in the file ``paper/results/questions.rmd``, you will need to download the responses from all participants from the Dataverse-NL repository, ``Behavioral data/responses_*``, and place them in a folder called ``paper/data/spr/`` in the current repository.

If you want to reproduce the entire pipeline (including preprocessing), you must download the raw EEG and reading times files. 

### Install dependencies
To run the analysis install the following dependencies
```bash
conda create -n spreeg r-rstan r-cmdstanr r-brms r-stringr r-tidytable r-readxl r-ggplot2 r-devtools r-argparse
```

This environment can also be installed using the ``environment.yml`` file
```bash
conda env create -n spreeg -f environment.yml
```

The r-package for EEG preprocessing, [eeguana](https://github.com/bnicenboim/eeguana), must be installed from the peak branch. This can be done by running the following r-code:
```r
library(devtools)

devtools::install_github("bnicenboim/eeguana@peak")
```

*NB: cmdstan must be installed for the environment to work. It can be installed using [cmdstanr](https://mc-stan.org/cmdstanr/articles/cmdstanr.html)*

## References
- Østergaard, Sara Møller; Lichtenberg, Lenneke; Boon, Laura; Nicenboim, Bruno, 2026, "EEG and Self-Paced Reading of Natural, Dutch Texts (Towards a computational model of reading (TCMR))", https://doi.org/10.34894/0O5XQ7, DataverseNL