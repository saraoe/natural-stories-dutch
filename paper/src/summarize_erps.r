# Functions for calculating mean ERPs from individual ERPs
library(tidytable)

# setwd("paper")

## define functions
filter_erps <- function(erps, reading_cond) {
    filt_erps <- erps |>
        filter(reading_type == reading_cond) |>
        group_by(.time, .key, lp_quantile) |>
        summarize(
            ".value" = mean(.value),
            ".value_content_words" = mean(.value_content_words)
        ) |>
        mutate("reading_type" = reading_cond)
    return(filt_erps)
}

update_erp_df <- function(cur_df, new_df) {
    new_df <- new_df |>
        rename(
            "value_new" = .value,
            "value_cw_new" = .value_content_words
        ) |>
        mutate("n_subjects_new" = 1)

    updated_df <- cur_df |>
        left_join(new_df) |>
        rowwise() |>
        mutate(
            ".value" = sum(.value, value_new, na.rm = TRUE),
            ".value_content_words" = sum(
                .value_content_words,
                value_cw_new,
                na.rm = TRUE
            ),
            "n_subjects" = sum(n_subjects, n_subjects_new, na.rm = TRUE)
        ) |>
        select(-value_new, -value_cw_new, -n_subjects_new)

    return(updated_df)
}

summarize_erps <- function(erp_folder, filename, reject_df) {
    print(paste("Making and writing file:", filename))
    erp_files <- list.files(
        erp_folder,
        full.names = TRUE,
        pattern = ".csv$"
    )

    for (erp_file in erp_files) {
        print(erp_file)

        erps <- read.csv(erp_file) |>
            select(-X) |>
            filter(document_id < 10) |> # remove pratice texts
            filter(!is.na(lp_quantile)) |> # remove words with out lp value
            left_join(reject_df,
                by = c("participant_number", "document_id")
            ) |>
            filter(!reject)

        erp_lp_spr <- filter_erps(erps, reading_cond = "SPR")
        erp_lp_rsvp <- filter_erps(erps, reading_cond = "RSVP")
        tmp_erp <- rbind(erp_lp_spr, erp_lp_rsvp)

        # save for return
        if (exists("erp_df_")) {
            erp_df_ <- update_erp_df(erp_df_, tmp_erp)
        } else {
            erp_df_ <- tmp_erp |>
                mutate("n_subjects" = 1)
        }
    }
    # calculate mean over all participants
    erp_df_ <- erp_df_ |>
        mutate(
            ".value" = .value / n_subjects,
            ".value_content_words" = .value_content_words / n_subjects
        )

    # save global erp file
    write.csv(erp_df_, filename)
}


### Run function

# create reject_df
artifact_threshold <- .3

reject_df <- read.csv("data/mean_amplitude.csv") |>
    filter(document_id < 10) |> # exclude practice texts
    filter(!is.na(lp_quantile)) |>
    group_by(participant_number, document_id) |>
    summarize(
        "reject" = ifelse(
            # if proportion of rejected epochs are under the threshold
            (sum(is.na(n400)) / n()) < artifact_threshold,
            FALSE, TRUE
        )
    ) |>
    mutate(
        "reject" = ifelse(
            # reject document 1 from participant 17 (error while reading)
            # and remove participant 64 (problems during data collection)
            ((participant_number == 17 & document_id == 1) |
                participant_number == 64),
            TRUE, reject
        )
    )



summarize_erps(
    erp_folder = "data/erps/",
    filename = "data/erp_lp.csv",
    reject_df = reject_df
)
