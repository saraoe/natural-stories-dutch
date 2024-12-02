# Log probability of stimuli

setwd("paper")

# libraries
# library(remotes)
# remotes::install_github("bnicenboim/pangoling@dev")
library(pangoling)
library(tidytable)
library(stringr)

# Model name (hugging face)
models <- c(
    "GroNLP/gpt2-medium-dutch-embeddings",
    "GroNLP/gpt2-small-dutch",
    "yhavinga/gpt2-large-dutch",
    "yhavinga/gpt-neo-125M-dutch"
)

# read csv
stim <- read.csv(
    list.files(
        "data/spr/",
        pattern = "rt_.*_1_.*\\.csv",
        full.names = TRUE
    )[1]
) |>
    select(story_name, document_id, word, word_n, paragraph_n) |>
    mutate(
        word = str_replace_all(word, "\\p{quotation mark}", "'")
    ) |> # remove fancy quotations
    arrange(document_id, paragraph_n, word_n)


# log probability and length of words
for (model_name in models) {
    print(model_name)
    causal_preload(model_name)
    stim <- stim |>
        mutate(lp = causal_lp(word,
            by = document_id,
            model = model_name,
            batch_size = 10
        ))

    stim <- stim |>
        rename_with(
            ~ paste(., model_name, sep = "_"), "lp"
        )
}

# calculate average lp
stim <- stim |>
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
    ) |>
    group_by(document_id) |>
    mutate(
        s_lp1 = lag(s_lp),
        s_lp2 = lag(s_lp, 2),
        s_lp3 = lag(s_lp, 3),
        s_wl1 = lag(s_wl),
        s_wl2 = lag(s_wl, 2),
        s_wl3 = lag(s_wl, 3)
    ) |>
    mutate(word = gsub("\"", "", word)) # rm newline token

# add the number of the word within every text
stim$number_word <- c(
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


write.csv(stim, "data/stim.csv")

# plot difference from average lp
stim |>
    pivot_longer(
        cols = starts_with("lp_"),
        names_to = "model_name",
        values_to = "model_lp"
    ) |>
    mutate(
        "diff_lp" = lp - model_lp
    ) |>
    ggplot() +
    geom_histogram(aes(x = diff_lp), binwidth = 0.5) +
    facet_wrap(. ~ model_name) +
    theme_minimal()
