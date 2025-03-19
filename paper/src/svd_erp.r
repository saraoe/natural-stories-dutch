# Singular value decomposition (SVD) to find single-trial event-related potentials (ERPs)
# See https://github.com/mdnunez/mcntoolbox/blob/master/nunez_etal2017_mathpsych/EEG_R/svderp.R

library(eeguana)
library(tidytable)
library(readxl)
library(stringr)

setwd("paper")
source("src/file_checks.r")
source("src/util.r")

dir.create(file.path(getwd(), "data/sterps"), showWarnings = TRUE)


svd_erp <- function(epochs, comp = 1) {
    # epochs in eeguana format
    # comp is the svd component to take the weights from
    #   - comp = 1 explains most variance
    erps <- epochs |>
        eeg_group_by(.sample) |>
        eeg_summarize(across_ch(mean, na.rm = TRUE)) |>
        signal_tbl() |>
        select(-.id, -.sample) |>
        as.matrix()

    svdouts <- svd(erps)
    weights <- svdouts$v[, comp]


    epochs_signal <- epochs |>
        signal_tbl() |>
        select(-.id, -.sample) |>
        as.matrix()

    sterp <- data.frame(
        ".value" = epochs_signal %*% weights,
        "segment" = signal_tbl(epochs)$.id,
        ".sample" = signal_tbl(epochs)$.sample
    ) |>
        mutate(".time" = as_time(.sample, .unit = "s"))

    return(sterp)
}


# files
epoch_files <- list.files("data/epochs/", full.names = TRUE, pattern = "rds$")
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

## loop over epochs
for (epoch_file in epoch_files) {
    start_time <- Sys.time()
    n <- as.numeric(gsub(".*?([0-9]+).*", "\\1", epoch_file))
    exclude_docs <- exclude_df |>
        filter(participant_number == n & !is.na(document_id)) |>
        pull(document_id)
    print(
        paste("Running participant: ", n, sep = "")
    )

    # load files
    epochs <- readRDS(epoch_file)
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

    # test
    if (!test_n_words(rt_df)) {
        print("Number of words in every story does not match!")
        next
    }

    # create sterps
    svd_epochs <- epochs |>
        eeg_filter(!document_id %in% c(11, 12)) |> # remove practice texts
        eeg_select(-VEOG, -HEOG) |>
        svd_erp() |>
        left_join(
            rt_df |>
                select(segment, document_id, participant_number, number_word),
            by = "segment"
        ) |>
        filter(!document_id %in% exclude_docs)

    number <- ifelse(n < 10, paste("0", n, sep = ""), as.character(n))
    write.csv(svd_epochs, paste("data/sterps/sterp", number, ".csv", sep = ""))

    # print time
    end_time <- Sys.time()
    print(paste("Time for participant", n, ":", end_time - start_time))
}
