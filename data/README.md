# Data

```
├── README.md
├── words_corpus.csv  
├── stories_index.xlsx 
├── SUBTLEX-NL.xlsx    
├── cloze.csv 
└── corpus_descriptives.csv

```

## Words Corpus
The file ``words_corpus.csv`` includes information about the stimuli (words) in the corpus. The file is creates in three different scripts: 
1) ``src/corpus_words.py``, creating a dataframe with all the words and which story they belong to is created.
2) ``src/corpus_words.r``, extracting log probability (lp) of the words from four different GPT models (see table below) from Hugging Face using the package [Pangoling](https://github.com/bnicenboim/pangoling).
3) ``src/stim_pos.py``, getting the part of speech (POS) tags for all the words using SpaCy and the *nl_core_news_sm* model.


The final file includes *word length* (wl), which is the number of characters including punctuation, *word frequency* (zipf_freq - or scaled s_freq), which is the Zipf Frequency of the word from from [SUBTLEX-NL](https://osf.io/3d8cx/) (also see below), and *log-probability* (lp), which an average of all the log-probability scores extracted from the four GPT models.
The prefix *s_* indicates the variable has been scaled, and the subfix *n* (where n is a number) indicates the number of lag. E.g., *s_lp1* is the scaled log probability of the previous word.

Models used for getting the log-probabilities
 Hugging Face Reference | Revision |
--------------------------|-------------|
 GroNLP/gpt2-small-dutch | d0e3f07a6e7cad045c45569bdaa08d318a275456 |
 GroNLP/gpt2-medium-dutch-embeddings | a7ea2d4a0dfc0a36b5fb11b93be9f63bf9cc89fb |
 yhavinga/gpt2-large-dutch | 992e422249fbda8000b5e65fdb86a6fd7a690865 |
| gpt-neo-125M-dutch | yhavinga/gpt-neo-125M-dutch | f7ba70ce7b62fbd1c29fd9012cf7b3b9bf0fd5d |

## Stories Index
Includes sources and information on all the texts in the corpus, along with a summaru of syntactic features annotated manually by two native Dutch speakers. 

## SUBTLEX-NL
Word frequencies from [SUBTLEX-NL](https://osf.io/3d8cx/). The file is called ``SUBTLEX-NL with pos and Zipf cd minimally 2.xlsx`` on the OSF repository and saved as ``SUBTLEX-NL.xlsx`` in this repository. The file was downloaded 10-06-2025.

## Cloze
Contains synthetically created cloze values from the Hugging Face model *bigscience/bloom-560m*. The file is created in ``src/cloze.py`` and uses SpaCy. These metrics were used in deciding which texts to include in the final corpus, thus, texts that are not part of the corpus are included in this file.

## Corpus Descriptives
Automated descriptives of the texts created using the python-packages TextDescriptives. The file is created in ``src/get_descriptives.py``. These metrics were used in deciding which texts to include in the final corpus, thus, texts that are not part of the corpus are included in this file.