### Util functions ###

read_multiple_sessions_csv <- function(filename) {
    df <- read.csv(filename)
    df$session <- as.numeric(gsub(".*?([0-9]+)\\.csv$", "\\1", filename))
    return(df)
}
