#!/bin/bash

conda activate spreeg
cd paper

echo "Running preprocessing.r"
Rscript src/preprocessing.r

echo "Running summarize_eeg.r"
Rscript src/summarize_eeg.r

echo "Running summarize_erps.r"
Rscript src/summarize_erps.r

echo "Running analysis.r"
Rscript src/analysis.r  --rt=TRUE --n400=TRUE --p600=TRUE

echo ""
echo ">> DONE <<"