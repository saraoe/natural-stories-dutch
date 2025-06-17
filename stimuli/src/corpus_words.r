# Proporties of words in corpus
## NB: corpus_words.py must be run before!

set.seed(246)

## libraries
# library(remotes)
# remotes::install_github("bnicenboim/pangoling@dev")
library(pangoling)
library(tidytable)
library(stringr)
library(readxl)


## Load data
corpus_df <- read.csv("data/words_corpus.csv") |>
    mutate( # remove fancy quotations
        word = str_replace_all(word, "\\p{quotation mark}", "'")
    )

# add the number of the word within every text
corpus_df$number_word <- c(
    1:600, # 1
    1:594, # 2
    1:600, # 3
    1:598, # 4
    1:597, # 5
    1:597, # 6
    1:600, # 7
    1:600, # 8
    1:98, # 11
    1:74 # 12
)

## Log probability
# Model name (hugging face)
models <- c(
    "GroNLP/gpt2-medium-dutch-embeddings",
    "GroNLP/gpt2-small-dutch",
    "yhavinga/gpt2-large-dutch",
    "yhavinga/gpt-neo-125M-dutch"
)


# log probability and length of words
for (model_name in models) {
    print(model_name)
    causal_preload(model_name)
    corpus_df <- corpus_df |>
        mutate(lp = causal_words_pred(word,
            by = document_id,
            model = model_name,
            batch_size = 10
        ))

    corpus_df <- corpus_df |>
        rename_with(
            ~ paste(., model_name, sep = "_"), "lp"
        )
}
colnames(corpus_df) <- gsub("/", "_", colnames(corpus_df))
colnames(corpus_df) <- gsub("-", ".", colnames(corpus_df))

## Word frequency
subtlex_freqs <- read_excel("data/SUBTLEX-NL.xlsx") |>
    select(Word, Zipf) |>
    rename(
        "word" = Word,
        "zipf_freq" = "Zipf"
    )

zero_freq_value <- log10(1 / 44.106) + 3 # from OSF description
corpus_df <- corpus_df |>
    left_join(subtlex_freqs) |>
    mutate(
        "zero_freq" = is.na(zipf_freq),
        "zipf_freq" = ifelse(is.na(zipf_freq), zero_freq_value, zipf_freq),
    )


## Average lp and word length
corpus_df <- corpus_df |>
    rowwise() |>
    mutate(
        lp = mean(c_across(starts_with("lp_"))),
        sd_lp = sd(c_across(starts_with("lp_")))
    ) |>
    ungroup() |>
    mutate(
        se_lp = sd_lp / sqrt(length(models)),
        wl = nchar(word),
        s_lp = scale(lp),
        s_wl = scale(wl),
        s_freq = scale(zipf_freq)
    ) |>
    group_by(document_id) |>
    mutate(
        s_lp1 = lag(s_lp),
        s_lp2 = lag(s_lp, 2),
        s_lp3 = lag(s_lp, 3),
        s_wl1 = lag(s_wl),
        s_wl2 = lag(s_wl, 2),
        s_wl3 = lag(s_wl, 3),
        s_freq1 = lag(s_freq),
        s_freq2 = lag(s_freq, 2),
        s_freq3 = lag(s_freq, 3)
    ) |>
    mutate(word = gsub("\"", "", word)) # rm newline token


## Write csv
write.csv(corpus_df, "data/words_corpus.csv")
