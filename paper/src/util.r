### Util functions ###
library(tidytable)
library(stringr)

read_multiple_sessions_csv <- function(filename) {
    df <- read.csv(filename)
    df$session <- as.numeric(gsub(".*?([0-9]+)\\.csv$", "\\1", filename))
    return(df)
}

read_rt_participant <- function(participant_number, folder = "data/spr") {
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
    return(rt_df)
}
