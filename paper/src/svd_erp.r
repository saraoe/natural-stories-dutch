# Singular value decomposition (SVD) to find single-trial event-related potentials (ERPs)
# See https://github.com/mdnunez/mcntoolbox/blob/master/nunez_etal2017_mathpsych/EEG_R/svderp.R

library(eeguana)
library(tidytable)


svd_erp <- function(epochs){
    erps <- epochs |>
        eeg_group_by(.sample) |>
        eeg_summarize(across_ch(mean, na.rm = TRUE)) |>
        signal_tbl() |>
        select(-.id, -.sample) |>
        as.matrix()

    svdouts <- svd(erps)
    weights <- svdouts$v[,1]


    epochs_signal <- epochs |>
        signal_tbl() |>
        select(-.id, -.sample) |>
        as.matrix()

    sterp = data.frame(
        ".value" = epochs_signal %*% weights,
        "segment" = signal_tbl(epochs)$.id,
        ".sample" = signal_tbl(epochs)$.sample
    ) |>
    mutate(".time" = as_time(.sample, .unit = "s"))

    return(sterp)
}


# testing function
# setwd("paper")
# eeg_file <- list.files("data/spr/", full.names=TRUE, pattern=".bdf$")[1]
# raw_eeg <- eeguana::read_edf(eeg_file)

# svd_epochs <- eeguana::eeg_segment(
#     raw_eeg, 
#     .description %in% c(101, 102), 
#     .lim = c(-0.2, 1.2)
#     ) |>
#     eeguana::eeg_baseline() |>
#     eeg_select(-M1, -M2, -Up, -Down, -Left, -Right) |>
#     svd_erp()
