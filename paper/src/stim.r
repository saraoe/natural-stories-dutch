# Log probability of stimuli

setwd("paper")

# libraries
# library(remotes)
# remotes::install_github("bnicenboim/pangoling@dev")
library(pangoling)
library(tidytable)

# read csv
stim <- read.csv(list.files("data/spr/",pattern = "rt_.*_1_.*\\.csv",full.names = TRUE)[1]) |>
    select(story_name, document_id, word, word_n, paragraph_n) |>
    arrange(document_id, paragraph_n, word_n)


# log probability and length of words
causal_preload("gpt2")
stim <- stim  |> 
    mutate(lp = causal_lp(word,
                            .by = document_id,
                            model = "gpt2",
                            batch_size = 10))

stim <- stim |>
    mutate(
        wl = nchar(word),
        s_lp = scale(lp),
        s_lp1 = lag(s_lp),
        s_lp2 = lag(s_lp, 2),
        s_lp3 = lag(s_lp, 3),
        s_wl = scale(wl),
        s_wl1 = lag(s_wl),
        s_wl2 = lag(s_wl, 2),
        s_wl3 = lag(s_wl, 3)
    ) |>
    mutate(word = gsub("\"", "", word))  # rm newline


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
    1:98,  # 11
    1:74   # 12
)


write.csv(stim, "data/stim.csv")
