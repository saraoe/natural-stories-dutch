# Event-Related Potentials of Surprisal in Self-Paced Reading

This study aims to explore the neural correlates of surprisal and the connections to reading times relying on data from self-paced reading (SPR). 

## Pipeline
| Step | File | Output folder |
| --- | --- | --- |
| Preprocessing | ``src/preprocessing.r`` | epochs saved in ``data/epochs/`` and plots of artifacts in ``figs/preprocessing/`` |
| Summarize epochs and create ERPs | ``src/summarize_eeg.r`` | csv-files with mean amplitudes ``data/`` and ERPs in ``data/erps`` |
| Models and plots | ``src/analysis.r  --rt=TRUE --n400=TRUE --p600=TRUE`` | models saved in ``src/brms_models/`` |

## Install dependencies
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