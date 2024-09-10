# Check of EEG files before preprocessing


test_n_triggers <- function(raw_eeg) {
  n_triggers <- c(
    "1" = 1,
    "2" = 1,
    "3" = 1,
    "4" = 1,
    "5" = 1,
    "6" = 1,
    "7" = 1,
    "8" = 1,
    "11" = 1,
    "12" = 1,
    "101" = 2457, # ueven words
    "102" = 2501, # even words
    "103" = 83, # paragraph
    "201" = 1, # beginning of experiment
    "202" = 10, # pause
    "203" = 10 # questions
  )

  check_df <- raw_eeg |>
    events_tbl() |>
    group_by(.description) |>
    summarize(
      n = n(),
      correct_n = n_triggers[as.character(.description)]
    ) |>
    mutate(
      check = (n == correct_n)
    )
  return(all(check_df$check))
}

test_n_words <- function(rt_df, n_words) {
  n_words <- c(
    "1" = 600,
    "2" = 594,
    "3" = 600,
    "4" = 598,
    "5" = 597,
    "6" = 597,
    "7" = 600,
    "8" = 600,
    "11" = 98,
    "12" = 74
  )

  check_df <- rt_df |>
    group_by(document_id, story_name) |>
    summarize(N = n()) |>
    mutate(
      doc_id = as.character(document_id),
      check = (N == n_words[doc_id])
    )
  return(all(check_df$check))
}

test_order_stories <- function(rt_df, raw_eeg) {
  story_events <- raw_eeg |>
    events_tbl() |>
    filter(.description < 20)

  return(all(unique(rt_df$document_id) == story_events$.description))
}



fix_trigger_description <- function(raw_eeg, participant_number) {
  if (participant_number == 7) {
    # remove second 5 trigger (because file was restarted)
    idx <- which(events_tbl(raw_eeg)$.description == 5)[2]
    events_tbl(raw_eeg) <- events_tbl(raw_eeg)[-idx, ]

    # change second 201 to 202 (because file was restarted)
    idx <- which(events_tbl(raw_eeg)$.description == 201)[2]
    events_tbl(raw_eeg)[idx] <- 202
  }

  return(raw_eeg)
}
