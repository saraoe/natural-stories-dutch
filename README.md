# Corpus for SPR-EEG study

We are building a corpus of Dutch stories for a self-paced reading (SPR) EEG study inspired by the English corpus described in Futrell et al. (2021). The corpus will contain 10 texts of different genres (e.g. fairy tales, technical texts, novels). The texts are chosen to have a high degree of overall fluency and comprehensibility. Additionally, they contain a high rate of rare or hard-to-process [syntactic constructions](#syntactic-features) that they either included originally or have been edited in after selection (however, still maintaining the original meaning and fluency of the texts), thus, allowing for a throurough study of reading and sentence processing in Dutch.

### Texts in corpus
| Number | Title | Author| Type |
| --- | --- | --- | --- | 
| 1 | Mijn Heer Zak met Rijst | --- | Fairy tale |
| 2 | Waarom de reuzen in Limburg zijn uitgestorven | --- | Fairy tale |
| 3 | De eerste opiumoorlog | --- | History |
| 4 | Aspasia | --- | History |
| 5 | De zilveren schaatsen | --- | Novel |
| 6 | Carrie | --- | Synopsis roman |
| 7 | Permafrost | --- | Technical text |
| 8 | Nomadisch pastoralisme | --- | Technical text |
| 9 | Kieming | --- | Technical text |
| 10 | Vleermuizen | --- | Technical text |

## Syntactic features

*Rare words*

By identifiying rare words, we can subtitute these for pseudowords and not distrub the fluency of the text. As such, the corpus makes it possible to study the influence of psedowords on sentence processing in a natural text.

*Idioms and Metaphors*

e.g.

*Ambiguity*

There are different kinds of ambiguity - see Futrell et al. (2021) for examples. 

## Dependencies
To install python packages pip install requirements.
```
pip install -r requirements.txt
```

## References
- Futrell, R., Gibson, E., Tily, H.J. et al. The Natural Stories corpus: a reading-time corpus of English texts containing rare syntactic constructions. *Lang Resources & Evaluation 55*, 63–77 (2021). https://doi.org/10.1007/s10579-020-09503-7