#!/usr/bin/env
# Preprocessing of SPR EEG data

### Libraries
library(eeguana)
library(ggplot2)
library(tidytable)
library(readxl)
library(stringr)

# setwd("paper")
source("src/svd_erp.r")
source("src/file_checks.r")
source("src/util.r")

# single trial erps
do_sterp <- FALSE
sterp_filename <- "data/sterp.csv"

# files
eeg_files <- list.files("data/spr/", full.names = TRUE, pattern = "df$")
<<<<<<< HEAD
stim <- read.csv("data/stim.csv") |>
    mutate("zero_freq" = as.logical(zero_freq)) |>
=======
stim <- read.csv("../data/words_corpus.csv") |>
    select(-X) |>
>>>>>>> 3ef51f6f63a4459b202de4521680eed53fc6fafa
    mutate(
        lp_quantile = case_when(
            lp >= quantile(lp, na.rm = TRUE)[4] ~ "high_lp",
            lp <= quantile(lp, na.rm = TRUE)[2] ~ "low_lp",
            (lp > quantile(lp, na.rm = TRUE)[2] &
                lp < quantile(lp, na.rm = TRUE)[4]) ~ "med_lp"
        ),
    )
exclude_df <- read_excel("data/exclude.xlsx")

# create out folder
dir.create(file.path(getwd(), "data/epochs"), showWarnings = TRUE)
dir.create(file.path(getwd(), "figs"), showWarnings = TRUE)
dir.create(file.path(getwd(), "figs/preprocessing"), showWarnings = TRUE)

## functions ##
inspect_rejected <- function(epochs, participant_n, rt_df, save_figs = FALSE) {
    reject_eyeblinks <- epochs |>
        eeg_select(Fp1, Fp2, VEOG) |>
        events_tbl() |>
        filter(!is.na(.channel)) |>
        filter(
            (any(grepl("direction=below", .description, fixed = TRUE)) &
                any(grepl("direction=above", .description, fixed = TRUE))),
            .by = .id
        ) |>
        group_by(.id) |>
        summarize(N = n()) |>
        pull(.id)

    reject_eyemovements <- epochs |>
        events_tbl() |>
        filter(grepl("step_threshold", .description, fixed = TRUE)) |>
        group_by(.id) |>
        summarize(N = n()) |>
        filter(!(.id %in% reject_eyeblinks)) |>
        pull(.id)

    reject_ptp_200 <- epochs |>
        events_tbl() |>
        filter(grepl("minmax_threshold=200", .description, fixed = TRUE)) |>
        group_by(.id) |>
        summarize(N = n()) |>
        filter(
            N >= 3 &
                !(.id %in% c(reject_eyeblinks, reject_eyemovements))
        ) |>
        pull(.id)

    reject_ptp_400 <- epochs |>
        events_tbl() |>
        filter(grepl("minmax_threshold=400", .description, fixed = TRUE)) |>
        group_by(.id) |>
        summarize(N = n()) |>
        filter(
            !(.id %in% c(
                reject_eyeblinks,
                reject_eyemovements,
                reject_ptp_200
            ))
        ) |>
        pull(.id)

    reject_ptp <- c(reject_ptp_200, reject_ptp_400)

    n_reject <- (length(reject_eyeblinks) +
        length(reject_eyemovements) +
        length(reject_ptp))
    print(paste("#Rejected epochs:", n_reject))
    print(paste("%Rejected epochs:", n_reject / nrow(segments_tbl(epochs))))

    epochs <- epochs |>
        eeg_mutate(
            "reject_reason" = case_when(
                segment %in% reject_eyeblinks ~ "eyeblink",
                segment %in% reject_eyemovements ~ "eyemovement",
                segment %in% reject_ptp ~ "ptp",
                .default = NA
            )
        )

    if (save_figs) {
        if (length(reject_eyeblinks) > 0) {
            p_artif_eyeblink <- epochs |>
                eeg_filter(reject_reason == "eyeblink") |>
                eeg_select(VEOG, Fp1, Fp2) |>
                eeg_filter(segment %in% unique(reject_eyeblinks)[1:200]) |> # only plot 200
                ggplot(aes(x = .time, y = .value, color = .key)) +
                geom_line() +
                facet_wrap(~segment) +
                theme(axis.text.x = element_text(angle = 90)) +
                theme_eeguana()
            ggsave(
                paste("figs/preprocessing/", participant_n, "_artif_eyeblink.png", sep = ""),
                plot = p_artif_eyeblink,
                width = 10, height = 20
            )
        }

        if (length(reject_eyemovements) > 0) {
            p_artif_eyemovement <- epochs |>
                eeg_filter(reject_reason == "eyemovement") |>
                eeg_select(HEOG, VEOG) |>
                eeg_filter(segment %in% unique(reject_eyemovements)[1:200]) |> # only plot 200
                ggplot(aes(x = .time, y = .value, color = .key)) +
                geom_line() +
                facet_wrap(~segment) +
                theme(axis.text.x = element_text(angle = 90)) +
                theme_eeguana()
            ggsave(
                paste("figs/preprocessing/", participant_n, "_artif_eyemovement.png", sep = ""),
                plot = p_artif_eyemovement,
                width = 10, height = 20
            )
        }

        if (length(reject_ptp) > 0) {
            p_artif_ptp <- epochs |>
                eeg_filter(reject_reason == "ptp") |>
                eeg_select(-HEOG, -VEOG) |>
                eeg_filter(segment %in% unique(reject_ptp)[1:200]) |> # only plot 200
                ggplot(aes(x = .time, y = .value, color = .key)) +
                geom_line() +
                facet_wrap(~segment) +
                theme(axis.text.x = element_text(angle = 90)) +
                theme_eeguana()
            ggsave(
                paste("figs/preprocessing/", participant_n, "_artif_ptp.png", sep = ""),
                plot = p_artif_ptp,
                width = 10, height = 20
            )
        }
    }

    rt_df <- rt_df |>
        mutate(
            "reject_reason" = case_when(
                segment %in% reject_eyeblinks ~ "eyeblink",
                segment %in% reject_eyemovements ~ "eyemovement",
                segment %in% reject_ptp ~ "ptp",
                .default = NA
            )
        )
    return(rt_df)
}


## Loop over eeg-files ##
for (eeg_file in eeg_files) {
    start_time <- Sys.time()
    n <- as.numeric(gsub(".*?([0-9]+).*", "\\1", eeg_file))
    if (n %in% c(23, 24)) { # doesnt have eog channels
        next
    }
    exclude_chs <- exclude_df |>
        filter(participant_number == n & !is.na(ch)) |>
        pull(ch)
    exclude_docs <- exclude_df |>
        filter(participant_number == n & !is.na(document_id)) |>
        pull(document_id)
    print(
        paste("Running participant: ", n, sep = "")
    )

    ### load files
    raw_eeg <- eeguana::read_edf(eeg_file) |>
        eeg_select(-(exclude_chs))
    raw_eeg <- fix_trigger_description(raw_eeg, n)
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

    ### test
    if (!test_n_triggers(raw_eeg)) {
        print("Number of triggers does not match!")
        next
    }
    if (!test_n_words(rt_df)) {
        print("Number of words in every story does not match!")
        next
    }
    if (!test_order_stories(rt_df, raw_eeg)) {
        print("Order of stories in raw_eeg and rt_df does not match!")
        next
    }

    ### preprocessing
    # using the 1020 layout
    eeguana::channels_tbl(raw_eeg) <- select(eeguana::channels_tbl(raw_eeg), .channel) |>
        left_join(eeguana::layout_32_1020) # we need a 64 layout!

    # extracting EOG sinal
    raw_eeg <- raw_eeg |>
        eeguana::eeg_rereference(Down, .ref = Up) |>
        eeguana::eeg_rereference(Right, .ref = Left) |>
        eeguana::eeg_rename(VEOG = Down, HEOG = Right) |>
        eeguana::eeg_select(-Up, -Left)

    # re-referencing
    raw_eeg <- eeguana::eeg_rereference(
        raw_eeg,
        -VEOG, -HEOG,
        .ref = c("M1", "M2")
    ) |>
        eeg_select(-M1, -M2)

    # filtering
    raw_filt <- eeguana::eeg_filt_band_pass(raw_eeg, .freq = c(.1, 30))

    # artifact detection
    artif_detect_error <- FALSE
    tryCatch( # try catch in case there is an error in the data
        expr = {
            artif_detect <- eeg_segment(raw_filt,
                .start = .description < 20,
                .end = .description == 203
            ) |> # artifacts in EEG channels
                eeg_artif_minmax(-HEOG, -VEOG,
                    .threshold = 400,
                    .window = 200,
                    .unit = "ms"
                ) |>
                eeg_artif_minmax(-HEOG, -VEOG,
                    .threshold = 200,
                    .window = 200,
                    .unit = "ms"
                ) |> # eye movements
                eeguana::eeg_artif_step(HEOG,
                    .threshold = 50,
                    .window = 200,
                    .unit = "ms"
                ) |>
                eeg_segment(
                    .description %in% c(101, 102),
                    .lim = c(-0.2, 1.2)
                ) |> # eye blinks
                eeg_artif_peak(Fp1, Fp2,
                    .threshold = 50,
                    .window = 200,
                    .unit = "ms",
                    .direction = "above"
                ) |>
                eeg_artif_peak(VEOG,
                    .threshold = 100,
                    .window = 200,
                    .unit = "ms",
                    .direction = "below"
                )
        },
        error = function(e) {
            print("artifact detection error")
            print(paste("participant number:", n))
            artif_detect_error <<- TRUE
        }
    )
    if (artif_detect_error) {
        next
    }

    ### create epochs
    # epoching
    epochs <- artif_detect |>
        eeg_left_join(rt_df) |>
        eeg_filter(!document_id %in% exclude_docs)

    rt_df <- inspect_rejected(epochs,
        participant_n = n,
        rt_df = rt_df,
        save_figs = TRUE
    )
    eyeblink_segments <- rt_df |>
        filter(reject_reason == "eyeblink") |>
        pull(segment)

    epochs <- epochs |>
        eeguana::eeg_baseline() |>
        eeg_events_to_NA( # if above in one of Fp1 or Fp2 and below in VEOG
            .id %in% eyeblink_segments,
            .drop_events = TRUE, .n_chs = 2
        ) |>
        eeg_events_to_NA( # eyemovements detected in HEOG
            grepl("step_threshold", .description, fixed = TRUE),
            .drop_events = TRUE, .n_chs = 1
        ) |>
        eeg_events_to_NA( # ptp above 200 in all eeg channels
            grepl("minmax_threshold=200", .description, fixed = TRUE),
            .drop_events = TRUE, .n_chs = 3
        ) |>
        eeg_events_to_NA( # ptp above 400 in all eeg channels
            grepl("minmax_threshold=400", .description, fixed = TRUE),
            .drop_events = TRUE, .n_chs = 1
        ) |>
        eeg_left_join(rt_df)

    # save epochs
    number <- ifelse(n < 10, paste("0", n, sep = ""), as.character(n))
    saveRDS(epochs, paste("data/epochs/", number, ".rds", sep = ""))

    if (do_sterp) {
        svd_epochs <- epochs |>
            eeg_filter(!document_id %in% c(11, 12)) |> # remove practice texts
            eeg_select(-VEOG, -HEOG) |>
            svd_erp() |>
            left_join(rt_df, by = "segment") |>
            filter(!document_id %in% exclude_docs)

        write.table(
            svd_epochs,
            erp_filename,
            sep = ",",
            col.names = !file.exists(erp_filename),
            row.names = FALSE,
            append = TRUE
        )
    }

    end_time <- Sys.time()
    print(paste("Time for participant", n, ":", end_time - start_time))
}
