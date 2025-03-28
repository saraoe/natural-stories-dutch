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


svd_erp <- function(epochs, comp = 1, lim = NULL) {
    # epochs in eeguana format
    # comp is the svd component to take the weights from
    #   - comp = 1 explains most variance
    # lim can be used if a smaller time window than
    #   the size of the epochs is to be used. If NULL the
    #   entire segment will be used

    # make lim if not defined
    if (is.null(lim)) {
        time_sec <- epochs |>
            signal_tbl() |>
            mutate(
                .time = as_time(.sample, .unit = "s")
            ) |>
            pull(.time)
        lim <- c(
            min(time_sec), max(time_sec)
        )
    } else {
        # test lim
        if (!is.numeric(lim) || length(lim) != 2) {
            stop("lim must be a numeric vector of length 2")
        }
    }

    ## cal average epoch (within defined lim)
    erps <- epochs |>
        eeg_mutate(.time = as_time(.sample, .unit = "s")) |>
        eeg_filter(.time |> between(lim[1], lim[2])) |>
        eeg_group_by(.sample) |>
        eeg_summarize(across_ch(mean, na.rm = TRUE)) |>
        signal_tbl() |>
        select(-.id, -.sample) |>
        as.matrix()

    # svd weights
    svdouts <- svd(erps)
    weights <- svdouts$v[, comp]

    # apply weights to entire epoch (regardless of lim)
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
    rt_df <- read_rt_participant(n)

    # test
    if (!test_n_words(rt_df)) {
        print("Number of words in every story does not match!")
        next
    }

    # create sterps
    svd_epochs <- epochs |>
        eeg_filter(!document_id %in% c(11, 12)) |> # remove practice texts
        eeg_select(-VEOG, -HEOG) |>
        svd_erp(lim = c(.08, .12)) |>
        left_join(
            rt_df |>
                select(segment, document_id, participant_number, number_word),
            by = "segment"
        ) |>
        filter(!document_id %in% exclude_docs)

    number <- ifelse(n < 10, paste("0", n, sep = ""), as.character(n))
    write.csv(svd_epochs, paste("data/sterps/sterp_p1_", number, ".csv", sep = ""))

    # print time
    end_time <- Sys.time()
    print(paste("Time for participant", n, ":", end_time - start_time))
}
