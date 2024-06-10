#!/usr/bin/env
# Preprocessing of EEG data in SPR condition

### Libraries
setwd("paper")
library(eeguana)
library(ggplot2)
library(tidytable)
library(readxl)

# files
eeg_files <- list.files("data/spr/", full.names=TRUE, pattern=".bdf$")[1]
stim <- read.csv("data/stim.csv") |>
        mutate(
            lp_quantile=ifelse(
                lp >= quantile(lp, na.rm=TRUE)[4], "high_lp", 
                ifelse(lp <= quantile(lp, na.rm=TRUE)[2], "low_lp", "med_lp")),
            )
exclude_df <- read_excel("data/exclude.xlsx")

## functions ##
read_rt_csv <- function(filename){
  df <- read.csv(filename)
  df$session <- as.numeric(gsub(".*?([0-9]+)\\.csv$", "\\1", filename))
  return(df)
}

inspect_rejected <- function(epochs, participant_n, rt_df, save_figs=FALSE){
    reject_eyeblinks <- epochs |>
        eeg_group_by(segment) |>
        events_tbl() |>
        filter(grepl("minmax_threshold=150", .description, fixed = TRUE)) |>
        group_by(.id) |>
        summarize(N = n()) |>
        filter(N>=2)

    reject_eyemovements <- epochs |>
        eeg_group_by(segment) |>
        events_tbl() |>
        filter(grepl("step_threshold", .description, fixed = TRUE)) |>
        group_by(.id) |>
        summarize(N = n()) |>
        filter(!(.id %in% reject_eyeblinks$.id))

    reject_ptp <- epochs |>
        eeg_group_by(segment) |>
        events_tbl() |>
        filter(grepl("minmax_threshold=2000", .description, fixed = TRUE)) |>
        group_by(.id) |>
        summarize(N = n()) |>
        filter(N>=3 & !(.id %in% c(reject_eyeblinks$.id, reject_eyemovements$.id)))
    
    n_reject <- nrow(reject_eyeblinks)+nrow(reject_eyemovements)+nrow(reject_ptp)
    print(paste("#Rejected epochs:", n_reject))
    print(paste("%Rejected epochs:", n_reject/nrow(segments_tbl(epochs))))

    epochs <- epochs |>
        eeg_mutate(
            "reject_reason" = ifelse(
                segment %in% reject_eyeblinks$.id, "eyeblink", ifelse(
                    segment %in% reject_eyemovements$.id, "eyemovement", ifelse(
                        segment %in% reject_ptp$.id, "ptp", NA
                    ) 
                )
            )
        ) 

    if (save_figs){
        if (nrow(reject_eyeblinks)>0){
            p_artif_eyeblink <- epochs |>
                eeg_filter(reject_reason == "eyeblink") |>
                eeg_select(VEOG, Fp1, Fp2) |>
                ggplot(aes(x = .time, y = .value, color=.key)) +
                geom_line() +
                facet_wrap(~segment) +
                theme(axis.text.x = element_text(angle = 90)) +
                theme_eeguana()
            ggsave(
                paste("figs/preprocessing/", participant_n, "_artif_eyeblink.png", sep=""),
                plot=p_artif_eyeblink
                )
        }    

        if (nrow(reject_eyemovements)>0){
            p_artif_eyemovement <- epochs |>
                eeg_filter(reject_reason == "eyemovement") |>
                eeg_select(HEOG, VEOG) |>
                ggplot(aes(x = .time, y = .value, color=.key)) +
                geom_line() +
                facet_wrap(~segment) +
                theme(axis.text.x = element_text(angle = 90)) +
                theme_eeguana()
            ggsave(
                paste("figs/preprocessing/", participant_n, "_artif_eyemovement.png", sep=""),
                plot=p_artif_eyemovement
                )
            }

        if (nrow(reject_ptp)>0){
            p_artif_ptp <- epochs |>
                eeg_filter(reject_reason == "ptp") |>
                eeg_select(-HEOG, -VEOG) |>
                ggplot(aes(x = .time, y = .value, color=.key)) +
                geom_line() +
                facet_wrap(~segment) +
                theme(axis.text.x = element_text(angle = 90)) +
                theme_eeguana()
            ggsave(
                paste("figs/preprocessing/", participant_n, "_artif_ptp.png", sep=""),
                plot=p_artif_ptp
                )
            }
    }
    
    rt_df <- rt_df |>
        mutate(
            "reject_reason" = ifelse(
                segment %in% reject_eyeblinks$.id, "eyeblink", ifelse(
                    segment %in% reject_eyemovements$.id, "eyemovement", ifelse(
                        segment %in% reject_ptp$.id, "ptp", NA
                    ) 
                )
            )
        )
    return(rt_df)

}


## Loop over eeg-files ##
for (eeg_file in eeg_files){
    n <- as.numeric(gsub(".*?([0-9]+).*", "\\1", eeg_file))
    exclude_chs <- exclude_df |> filter(participant_number==n & !is.na(ch))
    exclude_docs <- exclude_df |> filter(participant_number==n & !is.na(document_id))
    print(
        paste("Running participant: ", n, sep="")
    )

    ### load files
    raw_eeg <- eeguana::read_edf(eeg_file) |>
        eeg_select(-(exclude_chs$ch))
    rt_df <- list.files("data/spr", full.names=T, pattern=paste("rt_.*_", n, "_.*\\.csv$", sep="")) |>
        lapply(read_rt_csv) |>
        bind_rows() |>
        arrange(trial, paragraph_n, word_n) |>
        select(-X, -participant_id, -participant_subfix) |>
        left_join(stim, by=c("story_name", "document_id", "word_n", "paragraph_n", "word")) |>
        mutate(
            lp_quantile=ifelse(
                lp >= quantile(lp, na.rm = TRUE)[4], "high_lp", 
                ifelse(lp <= quantile(lp, na.rm = TRUE)[2], "low_lp", "med_lp")),
            )
    rt_df$segment <- 1:nrow(rt_df)
    
    ### preprocessing
    # using the 1020 layout
    eeguana::channels_tbl(raw_eeg) <- select(eeguana::channels_tbl(raw_eeg), .channel) |>
        left_join(eeguana::layout_32_1020)  # we need a 64 layout!
    
    # extracting EOG sinal
    raw_eeg <- raw_eeg |> 
        eeguana::eeg_rereference(Down, .ref = Up) |>
        eeguana::eeg_rereference(Right, .ref = Left) |>
        eeguana::eeg_rename(VEOG = Down, HEOG = Right) |>
        eeguana::eeg_select(-Up, -Left)
    
    # re-referencing
    raw_eeg <- eeguana::eeg_rereference(raw_eeg, -VEOG, -HEOG, .ref = c("M1", "M2"))

    # filtering
    raw_filt <- eeguana::eeg_filt_band_pass(raw_eeg, .freq = c(.1, 30))

    # artifact detection
    artif_detect <- raw_filt |>
        eeguana::eeg_artif_minmax(-HEOG, -VEOG,
                    .threshold = 200, 
                    .window = 200, 
                    .unit = "ms") |>
        eeguana::eeg_artif_minmax(VEOG, Fp1, Fp2,
                    .threshold = 150, 
                    .window = 200, 
                    .unit = "ms") |>
        eeguana::eeg_artif_step(HEOG, 
                    .threshold = 50, 
                    .window = 200, 
                    .unit = "ms")

    ### create epochs
    # epoching
    epochs <- eeguana::eeg_segment(artif_detect, 
                        .description %in% c(101, 102), 
                        .lim = c(-0.2, 1.2))

    rt_df <- inspect_rejected(epochs, participant_n=n, rt_df=rt_df, save_figs=TRUE)

    epochs <- epochs |>
        eeguana::eeg_baseline() |>
        eeg_events_to_NA(  # if threhold is exceeded in two channels Fp1, Fp2, and VEOG
        grepl("minmax_threshold=150", .description, fixed = TRUE), .drop_events=TRUE, .n_chs = 2
        ) |>
        eeg_events_to_NA(  # eyemovements detected in HEOG
        grepl("step_threshold", .description, fixed = TRUE), .drop_events=TRUE, .n_chs = 1
        ) |>
        eeg_events_to_NA(  # other signal with a ptp above 150
        grepl("minmax_threshold=200", .description, fixed = TRUE), .drop_events=TRUE, .n_chs = 3) |> 
        eeg_left_join(rt_df, by="segment") |>
        eeg_filter(!document_id %in% exclude_df$document_id)

    ### create csv-files
    # ERPs for plotting
    erp_lp_all <- epochs |>
        eeg_filter(!is.na(lp_quantile)) |>
        eeg_filter(document_id %in% c(11, 12)) |>  # exclude practice texts
        eeg_group_by(.sample, lp_quantile, participant_number) |>
        eeg_summarize(across_ch(mean, na.rm = TRUE)) |> 
        as_tidytable() |>
        mutate("reading_type" = "both")
    
    erp_lp_spr <- epochs |>
        eeg_filter(reading_type=="SPR") |>
        eeg_filter(!is.na(lp_quantile)) |>
        eeg_filter(document_id %in% c(11, 12)) |>  # exclude practice texts
        eeg_group_by(.sample, lp_quantile, participant_number) |>
        eeg_summarize(across_ch(mean, na.rm = TRUE)) |> 
        as_tidytable() |>
        mutate("reading_type" = "SPR")

    erp_lp_rsvp <- epochs |>
        eeg_filter(reading_type=="RSVP") |>
        eeg_filter(!is.na(lp_quantile)) |>
        eeg_filter(document_id %in% c(11, 12)) |>  # exclude practice texts
        eeg_group_by(.sample, lp_quantile, participant_number) |>
        eeg_summarize(across_ch(mean, na.rm = TRUE)) |> 
        as_tidytable() |>
        mutate("reading_type" = "RSVP")
    
    tmp_erp <- rbind(erp_lp_all, erp_lp_spr, erp_lp_rsvp) |>
        select(-.recording)
    
    if (exists("erp_df")) {
        erp_df <- rbind(erp_df, tmp_erp)
    } else {
        erp_df <- tmp_erp
    }

    # mean amplitudes
    amplitude_n400 <- epochs |>
        eeg_filter(between(as_time(.sample, .unit = "s"), .3, .5)) |>
        eeg_group_by(segment, .sample) |>
        eeg_summarize(
            "mean_amplitude_sample" = chs_mean(across(c(
                "Cz", "Pz", "C4", "CP6", "P4", "P3", "CP5", "C3", "P8", "PO3", "PO4", "P7"
            )), na.rm = TRUE)
            ) |> 
            eeg_group_by(segment) |>
            eeg_summarize(
                "mean_amplitude" = mean(mean_amplitude_sample)
            )

    amplitude_n170 <- epochs |>
        eeg_filter(between(as_time(.sample, .unit = "s"), .16, .21)) |>
        eeg_group_by(segment, .sample) |>
        eeg_summarize(
            "mean_amplitude_sample" = chs_mean(across(c(
                "O1", "Oz", "O2"
            )), na.rm = TRUE)
            ) |> 
            eeg_group_by(segment) |>
            eeg_summarize(
                "n170_mean_amplitude" = mean(mean_amplitude_sample)
            ) |>
            eeg_left_join(rt_df, by="segment")
    
    tmp_mean_amplitude <- amplitude_n400 |> 
        as_tidytable() |> rename(n400 = .value) |> select(-.key) |>
        left_join(
            amplitude_n170 |> as_tidytable() |> rename(n170 = .value) |> select(-.key)
            )
    
    if (exists("mean_amplitude_df")) {
        mean_amplitude_df <- rbind(mean_amplitude_df, tmp_mean_amplitude)
    } else {
        mean_amplitude_df <- tmp_mean_amplitude
    }

}

### write csv
write.csv(erp_df, "data/erp_lp.csv")
write.csv(mean_amplitude_df, "data/mean_amplitude.csv")
