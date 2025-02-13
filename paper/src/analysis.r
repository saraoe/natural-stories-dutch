# Analysis of reading times and ERP components

library(eeguana)
library(tidytable)
library(stringr)
library(brms)

# setwd("paper")
options(mc.cores = parallel::detectCores())
options(brms.backend = "cmdstan")

source("src/summarize_erps.r")
source("src/util.r")

dir.create(file.path(getwd(), "src/brms_models"), showWarnings = TRUE)

## Specify models to run
run_rt <- TRUE
run_n400 <- TRUE
run_p600 <- TRUE

## Rejection thresholds
# percent of rejected artifacts in one story for the entire story to be rejected
artifact_threshold <- .3
# reject reading times that are below or above (in ms)
rt_threshold <- c(100, 3000)

## Load data
content_words <- c("NOUN", "VERB", "ADJ", "ADV")

stim <- read.csv("../data/words_corpus.csv") |>
    mutate(zero_freq = as.logical(zero_freq))

rt_df <- list.files("data/spr",
    full.names = TRUE,
    pattern = "rt_.*\\.csv$"
) |>
    lapply(read_multiple_sessions_csv) |>
    bind_rows() |>
    mutate( # remove fancy quotations
        word = str_replace_all(word, "\\p{quotation mark}", "'")
    ) |>
    select(-X, -participant_id, -participant_subfix) |>
    left_join(stim,
        by = c("story_name", "document_id", "word_n", "paragraph_n", "word")
    ) |>
    mutate(
        lp_quantile = case_when(
            lp >= quantile(lp, na.rm = TRUE)[4] ~ "high_lp",
            lp <= quantile(lp, na.rm = TRUE)[2] ~ "low_lp",
            (lp > quantile(lp, na.rm = TRUE)[2] &
                lp < quantile(lp, na.rm = TRUE)[4]) ~ "med_lp"
        )
    ) |>
    mutate(
        lp_quantile = factor(lp_quantile,
            levels = c("low_lp", "med_lp", "high_lp")
        ),
        content_word = ifelse(pos %in% content_words, TRUE, FALSE)
    ) |>
    mutate(rt = reaction_time / 0.001) |> # reading times in ms instead of s
    # filter word where participant 17 was stopped
    filter(!(participant_number == 17 &
        document_id == 1 &
        number_word == 154)) |>
    # filter based on reject
    filter(rt > rt_threshold[1] & rt < rt_threshold[2]) |>
    # only include SPR
    filter(reading_type == "SPR") |>
    filter(document_id < 10) # filter out practice texts

mean_amplitude_df <- read.csv("data/mean_amplitude.csv") |>
    mutate(
        lp_quantile = factor(lp_quantile,
            levels = c("low_lp", "med_lp", "high_lp")
        ),
        zero_freq = as.logical(zero_freq),
        content_word = ifelse(pos %in% content_words, TRUE, FALSE)
    ) |>
    filter(document_id < 10) |> # filter out practice texts
    # reject based on artifact threshold
    group_by(participant_number, document_id) |>
    mutate(
        "rejected_epochs" = (sum(is.na(n400)) / n())
    ) |>
    filter(rejected_epochs < artifact_threshold) |>
    ungroup() |>
    # filter based on reject rt
    mutate(rt = reaction_time / 0.001) |> # reading times in ms instead of s
    filter(rt > rt_threshold[1] & rt < rt_threshold[2])


### Models ###

## Reading times
m_rt_priors <- c(
    prior(normal(5.5, 1), class = Intercept),
    prior(normal(0, .1), class = b),
    prior(normal(.5, .1), class = sigma),
    prior(normal(0, .5), class = sd)
)

m1_rt_formula <- bf(
    rt ~ s_lp + s_wl + s_freq +
        (s_lp + s_wl + s_freq || participant_number) +
        (s_lp + s_wl + s_freq || document_id) +
        (s_lp || word)
)

if (run_rt) {
    m <- brm(m1_rt_formula,
        family = lognormal(),
        prior = m_rt_priors,
        data = rt_df |> filter(reading_type == "SPR"),
        chains = 4,
        control = list(adapt_delta = 0.9),
        file = "src/brms_models/rt_m1"
    )
    print(summary(m))
}


## N400
m_n400_priors <- c(
    prior(normal(0, 20), class = Intercept),
    prior(normal(0, 10), class = b),
    prior(normal(10, 20), class = sigma),
    prior(normal(0, 10), class = sd)
)

m1_n400_formula <- bf(
    n400 ~ s_lp + s_wl + s_freq +
        (s_lp + s_wl + s_freq || participant_number) +
        (s_lp + s_wl + s_freq || document_id) +
        (s_lp || word)
)

m2_n400_formula <- bf(
    n400 ~ (s_lp + s_wl + s_freq) * content_word +
        ((s_lp + s_wl + s_freq) * content_word || participant_number) +
        ((s_lp + s_wl + s_freq) * content_word || document_id) +
        (s_lp * content_word || word)
)

if (run_n400) {
    reading_conds <- c("RSVP", "SPR")
    for (reading_cond in reading_conds) {
        for (i in seq_len(2)) {
            if (i == 1) {
                formula <- m1_n400_formula
            } else if (i == 2) {
                formula <- m2_n400_formula
            }

            m <- brm(formula,
                family = gaussian(),
                prior = m_n400_priors,
                data = mean_amplitude_df |>
                    filter(reading_type == reading_cond),
                chains = 4,
                control = list(adapt_delta = 0.9),
                seed = 246,
                file = paste(
                    "src/brms_models/n400_", reading_cond, "_m", i,
                    sep = ""
                )
            )
            print(summary(m))
        }
    }
}

## P600
m_p600_priors <- m_n400_priors

m1_p600_formula <- bf(
    p600 ~ s_lp + s_wl + s_freq +
        (s_lp + s_wl + s_freq || participant_number) +
        (s_lp + s_wl + s_freq || document_id) +
        (s_lp || word)
)

m2_p600_formula <- bf(
    p600 ~ (s_lp + s_wl + s_freq) * content_word +
        ((s_lp + s_wl + s_freq) * content_word || participant_number) +
        ((s_lp + s_wl + s_freq) * content_word || document_id) +
        (s_lp * content_word || word)
)

if (run_p600) {
    reading_conds <- c("RSVP", "SPR")
    for (reading_cond in reading_conds) {
        for (i in seq_len(2)) {
            if (i == 1) {
                formula <- m1_p600_formula
            } else if (i == 2) {
                formula <- m2_p600_formula
            }

            m <- brm(formula,
                family = gaussian(),
                prior = m_p600_priors,
                data = mean_amplitude_df |>
                    filter(reading_type == reading_cond),
                chains = 4,
                control = list(adapt_delta = 0.9),
                seed = 246,
                file = paste(
                    "src/brms_models/p600_", reading_cond, "_m", i,
                    sep = ""
                )
            )
            print(summary(m))
        }
    }
}
