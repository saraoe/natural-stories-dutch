#!/bin/bash

cd paper

# resampling EEG data if necessary
if test -f data/spr/TCMR_EEG_22.bdf; then
  if test ! -f data/spr/TCMR_EEG_22.edf; then
    echo ">> Resampling EEG data from participant 22 <<"
    python src/fix_participant_22.py
  fi
fi

# running pipeline
echo ""
echo ">> Running preprocessing.r <<"
Rscript src/preprocessing.r

echo ""
echo ">> Running summarize_eeg.r <<"
Rscript src/summarize_eeg.r

echo ""
echo ">> Running summarize_erps.r <<"
Rscript src/summarize_erps.r

echo ""
echo ">> Running analysis.r <<"
Rscript src/analysis.r  --rt=TRUE --n400=TRUE --p600=TRUE

echo ""
echo ">> DONE <<"