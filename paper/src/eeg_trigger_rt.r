# Getting reading times from EEG triggers
library(tidytable)
library(eeguana)

print("Making data/rt_eeg_triggers.csv")
# files
eeg_files <- list.files(file.path("data", "spr/"), full.names = TRUE, pattern = "df$")

for (eeg_file in eeg_files) {
    start_time <- Sys.time()
    n <- as.numeric(gsub(".*?([0-9]+).*", "\\1", eeg_file))
    print(n)

    if (str_detect(eeg_file, "TCMR_EEG_22.bdf")) {
        # you need to run the src/fix_partipant_22.ipynb
        print(eeg_file)
        print("Skipping file due to high sampling rate")
        next
    }

    raw_eeg <- read_edf(eeg_file)

    # calculate time to next trigger
    events_df <- events_tbl(raw_eeg) |>
        mutate(
            initial_ms = as_time(.initial, "ms"),
            time_next_trigger = lead(initial_ms) - initial_ms,
            before_questions = ifelse(lead(.description) == 203, 1, 0),
            after_paragraph = ifelse(lag(.description) == 103, 1, 0)
        )

    # include only word events (101 and 102)
    word_events_df <- events_df |>
        filter(.description %in% c(101, 102)) |>
        mutate(
            "rt" = ifelse(before_questions == 1,
                time_next_trigger - 750,
                time_next_trigger - 200
            )
        ) |>
        arrange(.initial) |>
        mutate(
            "participant_number" = n
        )
    word_events_df$segment <- seq_len(nrow(word_events_df))

    # save
    if (exists("rt_triggers_df")) {
        rt_triggers_df <- rbind(rt_triggers_df, word_events_df)
    } else {
        rt_triggers_df <- word_events_df
    }
}

write.csv(rt_triggers_df, file.path("data", "rt_eeg_triggers.csv"))
