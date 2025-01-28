#!/usr/bin/env
# Summarize epochs

### Libraries
library(eeguana)
library(ggplot2)
library(tidytable)
library(readxl)
library(stringr)

# setwd("paper")
source("src/util.r")

# save names
erp_folder <- "data/erps"
mean_amplitude_filename <- "data/mean_amplitude.csv"
dir.create(file.path(getwd(), erp_folder), showWarnings = FALSE)

### files
epoch_files <- list.files("data/epochs/", full.names = TRUE, pattern = ".rds$")
stim <- read.csv("../data/words_corpus.csv") |>
    select(-X) |>
    mutate(
        lp_quantile = case_when(
            lp >= quantile(lp, na.rm = TRUE)[4] ~ "high_lp",
            lp <= quantile(lp, na.rm = TRUE)[2] ~ "low_lp",
            (lp > quantile(lp, na.rm = TRUE)[2] &
                lp < quantile(lp, na.rm = TRUE)[4]) ~ "med_lp"
        ),
    )
exclude_df <- read_excel("data/exclude.xlsx")

### functions
get_participant_n <- function(file) {
    return(gsub(".*?([0-9]+).*", "\\1", file))
}

write_erps <- function(epochs, filename) {
    print(">>> ERPs")

    erps_all <- epochs |>
        eeg_group_by(
            .sample, lp_quantile, participant_number, document_id, reading_type
        ) |>
        eeg_summarize(across_ch(mean, na.rm = TRUE)) |>
        as_tidytable() |>
        select(-.recording, -.id)

    erps_content_words <- epochs |>
        eeg_filter(pos %in% c("NOUN", "VERB", "ADJ", "ADV")) |>
        eeg_group_by(
            .sample, lp_quantile, participant_number, document_id, reading_type
        ) |>
        eeg_summarize(across_ch(mean, na.rm = TRUE)) |>
        as_tidytable() |>
        select(-.recording, -.id) |>
        rename(".value_content_words" = .value)

    erps <- erps_all |> left_join(erps_content_words)

    write.csv(erps, file = filename)
}

write_mean_amplitude <- function(epochs, rt_df, exclude_chs, filename) {
    print(">>> mean amplitude")
    n400_chs <- c(
        "Cz", "Pz", "C4", "CP6", "P4", "P3",
        "CP5", "C3", "P8", "PO3", "PO4", "P7"
    )
    n400_chs <- n400_chs[!n400_chs %in% exclude_chs] # exclude
    amplitude_n400 <- epochs |>
        eeg_filter(between(as_time(.sample, .unit = "s"), .3, .5)) |>
        eeg_group_by(segment, .sample) |>
        eeg_summarize(
            "mean_amplitude_sample" = chs_mean(across(
                n400_chs
            ), na.rm = TRUE)
        ) |>
        eeg_group_by(segment) |>
        eeg_summarize(
            "mean_amplitude" = mean(mean_amplitude_sample)
        )

    n170_chs <- c("O1", "Oz", "O2")
    n170_chs <- n170_chs[!n170_chs %in% exclude_chs] # exclude
    amplitude_n170 <- epochs |>
        eeg_filter(between(as_time(.sample, .unit = "s"), .16, .21)) |>
        eeg_group_by(segment, .sample) |>
        eeg_summarize(
            "mean_amplitude_sample" = chs_mean(across(
                n170_chs
            ), na.rm = TRUE)
        ) |>
        eeg_group_by(segment) |>
        eeg_summarize(
            "n170_mean_amplitude" = mean(mean_amplitude_sample)
        ) |>
        eeg_left_join(rt_df, by = "segment")

    tmp_mean_amplitude <- amplitude_n400 |>
        as_tidytable() |>
        rename(n400 = .value) |>
        select(-.key) |>
        left_join(
            amplitude_n170 |>
                as_tidytable() |>
                rename(n170 = .value) |>
                select(-.key)
        )

    write.table(
        tmp_mean_amplitude,
        filename,
        sep = ",",
        col.names = !file.exists(filename),
        row.names = FALSE,
        append = TRUE
    )
}

# skip already summarized participants
erp_files <- list.files(erp_folder, full.names = TRUE, pattern = ".csv$")
if (length(erp_files) > 0) {
    cur_erp_participants <- erp_files |>
        get_participant_n() |>
        as.numeric()
} else {
    cur_erp_participants <- c()
}
if (file.exists(mean_amplitude_filename)) {
    cur_mean_df <- read.csv(mean_amplitude_filename)
    cur_mean_participants <- unique(cur_mean_df$participant_number)
} else {
    cur_mean_participants <- c()
}

## loop through files
for (epoch_file in epoch_files) {
    start_time <- Sys.time()
    char_n <- get_participant_n(epoch_file)
    n <- as.numeric(char_n)
    print(
        paste("Running participant: ", n, sep = "")
    )

    # load data
    exclude_chs <- exclude_df |>
        filter(participant_number == n & !is.na(ch)) |>
        pull(ch)
    epochs <- readRDS(epoch_file) |>
        as_eeg_lst()
    rt_df <- list.files(
        "data/spr",
        full.names = TRUE,
        pattern = paste("rt_.*_", n, "_.*\\.csv$", sep = "")
    ) |>
        lapply(read_multiple_sessions_csv) |>
        bind_rows() |>
        mutate( # remove fancy quotations
            word = str_replace_all(word, "\\p{quotation mark}", "'"),
            trial = ifelse(document_id > 10, trial - 0.5, trial)
        ) |>
        select(-X, -participant_id, -participant_subfix) |>
        left_join(
            stim,
            by = c("story_name", "document_id", "word_n", "paragraph_n", "word")
        ) |>
        arrange(trial, paragraph_n, word_n)
    rt_df$segment <- seq_len(nrow(rt_df))
    reject_reasons <- epochs |>
        segments_tbl() |>
        select(reject_reason, segment)
    rt_df <- rt_df |> left_join(reject_reasons)

    # summarize results
    if (!n %in% cur_erp_participants) {
        write_erps(
            epochs,
            filename = paste(erp_folder, "/erps_", char_n, ".csv", sep = "")
        )
    } else {
        print(paste("Participant", n, "is already in", erp_folder))
    }
    if (!n %in% cur_mean_participants) {
        write_mean_amplitude(
            epochs, rt_df, exclude_chs, mean_amplitude_filename
        )
    } else {
        print(paste("Participant", n, "is already in", mean_amplitude_filename))
    }

    end_time <- Sys.time()
    print(paste("Time for participant", n, ":", end_time - start_time))
}
