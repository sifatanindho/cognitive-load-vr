# Find the column index where the value equals "Cond1"
cond_col_index <- grep("Condition1", colnames(survey))

# 1 EV
# 2 EPi
# 3 Touch
# 4 PoPi
# 5 PoV

SUS_EV <- process_sus_data(survey, "EV")
SUS_EP <- process_sus_data(survey, "EP")
SUS_Touch <- process_sus_data(survey, "Touch")
SUS_PoPi <- process_sus_data(survey, "PoPi")
SUS_PoV <- process_sus_data(survey, "PoV")

# List of all SUS data frames
#sus_list <- list(SUS_EV, SUS_EP, SUS_Touch, SUS_PoPi, SUS_PoV)

# Function to process each SUS data frame
process_sus <- function(sus_data) {
    sus_data$QPID <- survey$QPID
    sus_data <- sus_data %>%
        remove_rownames() %>%
        column_to_rownames(var = "QPID")
    sus_data <- sus_data %>%
        mutate_all(as.numeric)
    sus_data_p <- subtraction_func(sus_data)
    sus_data_p$score <- rowSums(sus_data_p)
    sus_data_p$score <- sus_data_p$score * 2.5
    return(sus_data_p) # return the processed data frame
}
# Apply the function to each SUS data frame
processed_EV <- process_sus(SUS_EV)
processed_EP <- process_sus(SUS_EP)
processed_Touch <- process_sus(SUS_Touch)
processed_PoPi <- process_sus(SUS_PoPi)
processed_PoV <- process_sus(SUS_PoV)
processed_EV$Condition <- "EV"
processed_EP$Condition <- "EP"
processed_Touch$Condition <- "Touch"
processed_PoPi$Condition <- "PoPi"
processed_PoV$Condition <- "PoV"
processed_EV <- tibble::rownames_to_column(processed_EV, "ID")
processed_EP <- tibble::rownames_to_column(processed_EP, "ID")
processed_Touch <- tibble::rownames_to_column(processed_Touch, "ID")
processed_PoPi <- tibble::rownames_to_column(processed_PoPi, "ID")
processed_PoV <- tibble::rownames_to_column(processed_PoV, "ID")

# Combine all the processed data frames into one
SUStotal <- bind_rows(processed_EV, processed_EP, processed_Touch, processed_PoPi, processed_PoV)

# Rename the score column

SUStotal <- select(SUStotal, ID, Condition, score)






