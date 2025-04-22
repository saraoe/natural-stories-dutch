# Analysis of reading times and ERP components

library(eeguana)
library(tidytable)
library(stringr)
library(brms)
library(argparse)

# setwd("paper")
options(mc.cores = parallel::detectCores())
options(brms.backend = "cmdstan")

source("src/summarize_erps.r")
source("src/file_checks.r")
source("src/util.r")

dir.create(file.path(getwd(), "src/brms_models"), showWarnings = TRUE)

## Specify models to run using argparse
parser <- ArgumentParser(description = "Run brms models")
parser$add_argument("--rt",
    type = "logical",
    default = FALSE,
    help = "Which models to run (rt, n400, and p600)"
)
parser$add_argument("--n400",
    type = "logical",
    default = FALSE,
    help = "Which models to run (rt, n400, and p600)"
)
parser$add_argument("--p600",
    type = "logical",
    default = FALSE,
    help = "Which models to run (rt, n400, and p600)"
)

args <- parser$parse_args()
run_rt <- args$rt
run_n400 <- args$n400
run_p600 <- args$p600
print(paste(
    "Running Models: ",
    "rt=", run_rt, ", n400=", run_n400, ", p600=", run_p600,
    sep = ""
))

## Rejection thresholds
# percent of rejected artifacts in one story for the entire story to be rejected
artifact_threshold <- .3
# reject reading times that are below or above (in ms)
rt_threshold <- c(100, 3000)

## Load data
content_words <- c("NOUN", "VERB", "ADJ", "ADV")

## load reading times
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
    )

# check number of words per participant is correct
if (!test_n_words_per_participants(rt_df)) {
    print("Number of words per participant in rt_df not correct!")
    quit()
}

# filter df
rt_df <- rt_df |>
    mutate(rt = reaction_time / 0.001) |> # reading times in ms instead of s
    # filter word where participant 17 was stopped
    filter(!(participant_number == 17 &
        document_id == 1 &
        number_word == 154)) |>
    filter(participant_number != 64) |> # exclude participant 64
    # filter based on reject
    filter(rt > rt_threshold[1] & rt < rt_threshold[2]) |>
    # only include SPR
    filter(reading_type == "SPR") |>
    filter(document_id < 10) # filter out practice texts

# load EEG components
mean_amplitude_df <- read.csv("data/mean_amplitude.csv") |>
    mutate(
        lp_quantile = factor(lp_quantile,
            levels = c("low_lp", "med_lp", "high_lp")
        ),
        zero_freq = as.logical(zero_freq),
        content_word = ifelse(pos %in% content_words, TRUE, FALSE)
    ) |>
    filter(document_id < 10) # filter out practice texts

# check number of words per participant is correct
if (!test_n_words_per_participants(mean_amplitude_df)) {
    print("Number of words per participant in mean_amplitude_df not correct!")
    quit()
}

# filter
mean_amplitude_df <- mean_amplitude_df |>
    # filter word where participant 17 was stopped
    filter(!(participant_number == 17 &
        document_id == 1 &
        number_word == 154)) |>
    filter(participant_number != 64) |> # exclude participant 64
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
m_rt_priors_no_intercept <- m_rt_priors[2:4, ]

m1_rt_formula <- bf(
    rt ~ s_lp + s_freq +
        (s_lp + s_freq || participant_number) +
        (s_lp + s_freq || document_id) +
        (s_lp || word)
)

m2_rt_formula <- bf(
    rt ~ -1 + content_word +
        content_word:s_lp + content_word:s_freq +
        (content_word + content_word:s_lp +
            content_word:s_freq || participant_number) +
        (content_word + content_word:s_lp +
            content_word:s_freq || document_id) +
        (content_word + content_word:s_lp || word)
)

m3_rt_formula <- bf(
    rt ~ s_lp + s_wl + s_freq +
        (s_lp + s_wl + s_freq || participant_number) +
        (s_lp + s_wl + s_freq || document_id) +
        (s_lp || word)
)

if (run_rt) {
    print(">>> Reading Time Model <<<")
    for (i in seq_len(3)) {
        print(
            paste("Model formula", i)
        )

        if (i == 1) {
            formula <- m1_rt_formula
            prior <- m_rt_priors
        } else if (i == 2) {
            formula <- m2_rt_formula
            prior <- m_rt_priors_no_intercept
        } else if (i == 3) {
            formula <- m3_rt_formula
            prior <- m_rt_priors
        }

        m <- brm(formula,
            family = lognormal(),
            prior = m_rt_priors,
            data = rt_df |> filter(reading_type == "SPR"),
            chains = 4,
            sample_prior = TRUE,
            control = list(adapt_delta = 0.9999),
            seed = 246,
            file = paste("src/brms_models/rt_SPR_m", i, sep = "")
        )
        print(summary(m))
    }
}


## N400 SPR
m_n400_priors <- c(
    prior(normal(0, 20), class = Intercept),
    prior(normal(0, 10), class = b),
    prior(normal(10, 20), class = sigma),
    prior(normal(0, 10), class = sd)
)
m_n400_priors_no_intercept <- m_n400_priors[2:4, ]

m1_n400_formula <- bf(
    n400 ~ s_lp + s_freq +
        (s_lp + s_freq || participant_number) +
        (s_lp + s_freq || document_id) +
        (s_lp || word)
)

m2_n400_formula <- bf(
    n400 ~ -1 + content_word +
        content_word:s_lp + content_word:s_freq +
        (content_word + content_word:s_lp +
            content_word:s_freq || participant_number) +
        (content_word + content_word:s_lp +
            content_word:s_freq || document_id) +
        (content_word + content_word:s_lp || word)
)

m3_n400_formula <- bf(
    n400 ~ s_lp + s_wl + s_freq +
        (s_lp + s_wl + s_freq || participant_number) +
        (s_lp + s_wl + s_freq || document_id) +
        (s_lp || word)
)

if (run_n400) {
    print(">>> N400 SPR Models <<<")
    for (i in seq_len(3)) {
        print(
            paste("Model formula", i)
        )

        if (i == 1) {
            formula <- m1_n400_formula
            priors <- m_n400_priors
        } else if (i == 2) {
            formula <- m2_n400_formula
            priors <- m_n400_priors_no_intercept
        } else if (i == 3) {
            formula <- m3_n400_formula
            priors <- m_n400_priors
        }

        m <- brm(formula,
            family = gaussian(),
            prior = priors,
            data = mean_amplitude_df |>
                filter(reading_type == "SPR"),
            chains = 4,
            sample_prior = TRUE,
            control = list(adapt_delta = 0.9999),
            seed = 246,
            file = paste(
                "src/brms_models/n400_SPR_m", i,
                sep = ""
            )
        )
        print(summary(m))
    }
}


## N400 RSVP (formulas without document id random effects)
m1_n400_rsvp_formula <- bf(
    n400 ~ s_lp + s_freq +
        (s_lp + s_freq || participant_number) +
        (s_lp || word)
)

m2_n400_rsvp_formula <- bf(
    n400 ~ -1 + content_word +
        content_word:s_lp + content_word:s_freq +
        (content_word + content_word:s_lp +
            content_word:s_freq || participant_number) +
        (content_word + content_word:s_lp || word)
)

m3_n400_rsvp_formula <- bf(
    n400 ~ s_lp + s_wl + s_freq +
        (s_lp + s_wl + s_freq || participant_number) +
        (s_lp || word)
)

if (run_n400) {
    print(">>> N400 RSVP Models <<<")
    for (i in seq_len(3)) {
        print(
            paste("Model formula", i)
        )

        if (i == 1) {
            formula <- m1_n400_rsvp_formula
            priors <- m_n400_priors
        } else if (i == 2) {
            formula <- m2_n400_rsvp_formula
            priors <- m_n400_priors_no_intercept
        } else if (i == 3) {
            formula <- m3_n400_rsvp_formula
            priors <- m_n400_priors
        }

        m <- brm(formula,
            family = gaussian(),
            prior = priors,
            data = mean_amplitude_df |>
                filter(reading_type == "RSVP"),
            chains = 4,
            sample_prior = TRUE,
            control = list(adapt_delta = 0.9999),
            seed = 246,
            file = paste(
                "src/brms_models/n400_RSVP_m", i,
                sep = ""
            )
        )
        print(summary(m))
    }
}


## P600 SPR
m_p600_priors <- m_n400_priors
m_p600_priors_no_intercept <- m_n400_priors_no_intercept

m1_p600_formula <- bf(
    p600 ~ s_lp + s_freq +
        (s_lp + s_freq || participant_number) +
        (s_lp + s_freq || document_id) +
        (s_lp || word)
)

m2_p600_formula <- bf(
    p600 ~ -1 + content_word +
        content_word:s_lp + content_word:s_freq +
        (content_word + content_word:s_lp +
            content_word:s_freq || participant_number) +
        (content_word + content_word:s_lp +
            content_word:s_freq || document_id) +
        (content_word + content_word:s_lp || word)
)

m3_p600_formula <- bf(
    p600 ~ s_lp + s_wl + s_freq +
        (s_lp + s_wl + s_freq || participant_number) +
        (s_lp + s_wl + s_freq || document_id) +
        (s_lp || word)
)


if (run_p600) {
    print(">>> P600 SPR Models <<<")
    for (i in seq_len(3)) {
        print(
            paste("Model formula", i)
        )

        if (i == 1) {
            formula <- m1_p600_formula
            priors <- m_p600_priors
        } else if (i == 2) {
            formula <- m2_p600_formula
            priors <- m_p600_priors_no_intercept
        } else if (i == 3) {
            formula <- m3_p600_formula
            priors <- m_p600_priors
        }

        m <- brm(formula,
            family = gaussian(),
            prior = priors,
            data = mean_amplitude_df |>
                filter(reading_type == "SPR"),
            chains = 4,
            sample_prior = TRUE,
            control = list(adapt_delta = 0.9999),
            seed = 246,
            file = paste(
                "src/brms_models/p600_SPR_m", i,
                sep = ""
            )
        )
        print(summary(m))
    }
}


## P600 RSVP (formulas without document id random effects)
m1_p600_rsvp_formula <- bf(
    p600 ~ s_lp + s_freq +
        (s_lp + s_freq || participant_number) +
        (s_lp || word)
)

m2_p600_rsvp_formula <- bf(
    p600 ~ -1 + content_word +
        content_word:s_lp + content_word:s_freq +
        (content_word + content_word:s_lp +
            content_word:s_freq || participant_number) +
        (content_word + content_word:s_lp || word)
)

m3_p600_rsvp_formula <- bf(
    p600 ~ s_lp + s_wl + s_freq +
        (s_lp + s_wl + s_freq || participant_number) +
        (s_lp || word)
)

if (run_p600) {
    print(">>> p600 RSVP Models <<<")
    for (i in seq_len(3)) {
        print(
            paste("Model formula", i)
        )

        if (i == 1) {
            formula <- m1_p600_rsvp_formula
            priors <- m_p600_priors
        } else if (i == 2) {
            formula <- m2_p600_rsvp_formula
            priors <- m_p600_priors_no_intercept
        } else if (i == 3) {
            formula <- m3_p600_rsvp_formula
            priors <- m_p600_priors
        }

        m <- brm(formula,
            family = gaussian(),
            prior = priors,
            data = mean_amplitude_df |>
                filter(reading_type == "RSVP"),
            chains = 4,
            sample_prior = TRUE,
            control = list(adapt_delta = 0.9999),
            seed = 246,
            file = paste(
                "src/brms_models/p600_RSVP_m", i,
                sep = ""
            )
        )
        print(summary(m))
    }
}
