### Util functions ###
library(tidytable)

read_multiple_sessions_csv <- function(filename) {
    df <- read.csv(filename)
    df$session <- as.numeric(gsub(".*?([0-9]+)\\.csv$", "\\1", filename))
    return(df)
}

filter_erps <- function(erps, reading_cond) {
    filt_erps <- erps |>
        filter(reading_type == reading_cond) |>
        filter(!is.na(lp_quantile)) |>
        filter(!(document_id %in% c(11, 12))) |> # exclude practice texts
        group_by(.time, .key, lp_quantile, participant_number) |>
        summarize(
            ".value" = mean(.value),
            ".value_action_words" = mean(.value_action_words)
        ) |>
        mutate("reading_type" = reading_cond)
    return(filt_erps)
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
            if (exists("erp_df")) {
                erp_df <- rbind(erp_df, tmp_erp)
            } else {
                erp_df <- tmp_erp
            }
        }
        # save global erp file
        write.csv(erp_df, filename)
    } else {
        erp_df <- read.csv(filename) |>
            select(-X)
    }

    return(erp_df)
}
