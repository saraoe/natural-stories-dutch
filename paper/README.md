# Event-Related Potentials of Surprisal in Self-Paced Reading

This study aims to explore the neural correlates of surprisal and the connections to reading times relying on data from self-paced reading (SPR). 

## Pipeline
| Step | File | Output folder |
| --- | --- | --- |
| Preprocessing | ``src/preprocessing.r`` | epochs saved in ``data/epochs/`` and plots of artifacts in ``figs/preprocessing/`` |
| Summarize epochs | ``src/summarize_results.r`` | csv-files with mean amplitudes ``data/`` and ERPs in ``data/erps`` |
| Models and plots | ``src/analysis.rmd`` | plots in ``figs/`` |