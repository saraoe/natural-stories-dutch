# Functions for calculating mean ERPs from individual ERPs

filter_erps <- function(erps, reading_cond) {
    filt_erps <- erps |>
        filter(reading_type == reading_cond) |>
        filter(!is.na(lp_quantile)) |>
        filter(!(document_id %in% c(11, 12))) |> # exclude practice texts
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

read_filt_erps <- function(erp_folder, filename, reject_df, overwrite = FALSE) {
    if (overwrite || !file.exists(filename)) {
        print(paste("Making and writing file:", filename))
        erp_files <- list.files(
            "data/erps/",
            full.names = TRUE,
            pattern = ".csv$"
        )

        for (erp_file in erp_files) {
            print(erp_file)

            erps <- read.csv(erp_file) |>
                select(-X) |>
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
    } else {
        erp_df_ <- read.csv(filename) |>
            select(-X)
    }

    return(erp_df_)
}


erp_files <- list.files(
    "data/erps/",
    full.names = TRUE,
    pattern = ".csv$"
)

for (erp_file in erp_files) {
    print(erp_file)
    df <- read.csv(erp_file) |>
        select(-X) |>
        rename(".value_content_words" = .value_action_words)

    write.csv(df, file = erp_file)
}
