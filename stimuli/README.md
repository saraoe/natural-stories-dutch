# Linguistic Stimuli

We are building a corpus of Dutch text for a self-paced reading (SPR) EEG study inspired by the English corpus described in Futrell et al. (2021). The corpus contains 8 texts of different genres (e.g. fairy tales, technical texts, novels). The texts are chosen to have a high degree of overall fluency and comprehensibility. Additionally, texts that contain a high rate of specific syntactic features (i.e., idioms, ambiguity, metaphors, and rare words) are prioritized. Thus, allowing for a throurough study of reading and sentence processing in Dutch.

The texts were chosen and read through by two native speakers. The texts were manually annotated for syntactic features (see ``data/stories_index.xlsx``) and automatically derived descriptives were also extracted (see ``src/get_descriptives.py``).

### Texts in corpus

|  | Title | Author | Type of text | Source | Retrieval |
|----|-------|--------|--------------|--------|-----------|
| 1 | Mijn Heer Zak met Rijst | F. Hadland Davis | Fairy tale | [Gutenberg][a] | 06-10-2023 |
| 2 | Waarom de reuzen in Limburg zijn uitgestorven | Josef Cohen | Fairy Tale | [Gutenberg][b] | 10-10-2023 |
| 3 | Aspasia | Wikipedia | History | [Wikipedia][c] | 10-10-2023 |
| 4 | De zilveren schaatsen | P. J. Andriessen & Mary Mapes Dodge | Novel | [Gutenberg][d] | 09-10-2023 |
| 5 | Permafrost | Wikipedia | Technical text | [Wikipedia][e] | 08-10-2023 |
| 6 | Nomadisch pastoralisme | Wikipedia | Technical text | [Wikipedia][f] | 09-10-2023 |
| 7 | Vleermuizen | Wikipedia | Technical text | [Wikipedia][g] | 09-10-2023 |
| 8 | Violetta[^1] | Wikipedia | Synopsis show | [Wikipedia][h] | 21-11-2023 |

[^1]: Original text is in English. The experimental text was translated by two native Dutch speakers.

[a]: https://www.gutenberg.org/cache/epub/16043/pg16043-images.html#xd0e1307  
[b]: https://www.gutenberg.org/cache/epub/3455/pg3455-images.html#d0e5089  
[c]: https://nl.wikipedia.org/wiki/Aspasia  
[d]: https://www.gutenberg.org/cache/epub/60777/pg60777-images.html  
[e]: https://nl.wikipedia.org/wiki/Permafrost  
[f]: https://nl.wikipedia.org/wiki/Nomadisch_pastoralisme  
[g]: https://nl.wikipedia.org/wiki/Vleermuizen  
[h]: https://en.wikipedia.org/wiki/Violetta_(TV_series)

## Dependencies
To install python packages pip install requirements.
```
pip install -r requirements.txt
```

## References
- Futrell, R., Gibson, E., Tily, H.J. et al. The Natural Stories corpus: a reading-time corpus of English texts containing rare syntactic constructions. *Lang Resources & Evaluation 55*, 63–77 (2021). https://doi.org/10.1007/s10579-020-09503-7