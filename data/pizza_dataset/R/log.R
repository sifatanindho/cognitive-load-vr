cols <- c(
  "code",
  "condition",
  "time_total",
  "wrongOrder",
  "expired",
  "orderAcTime",
  # "foodDismissals"
  "timePerCustomer"
)
source("R\\functions.R")
# "foodDismissals"
tempLog <- data.frame(matrix(ncol = length(cols), nrow = 100))
colnames(tempLog) <- cols
bigLog <- data.frame(matrix(ncol = length(cols), nrow = 100))
colnames(bigLog) <- cols
# Get all file names in the HoloLensLogs folder
file_names <- list.files("Data/", full.names = TRUE)

for (file in file_names) {
  log_data <- process_log(file)
  colnames(log_data) <- cols
  bigLog <- rbind(bigLog, log_data)
}


bigLog <- na.omit(bigLog)

# just for descriptive stats ## for total time
new_df <- select(bigLog, code, condition, time_total)
new_df <- pivot_wider(new_df, names_from = condition, values_from = time_total)
new_df$EyPi <- as.numeric(new_df$EyPi)
new_df$EyVo <- as.numeric(new_df$EyVo)
new_df$PoPi <- as.numeric(new_df$PoPi)
new_df$PoVo <- as.numeric(new_df$PoVo)
new_df$ToTo <- as.numeric(new_df$ToTo)
st(new_df, out = "latex", summ = c(
  "mean(x)",
  "median(x)",
  "sd(x)"
)) 

new_df2 <- select(bigLog, code, condition, orderAcTime)
new_df2 <- pivot_wider(new_df2, names_from = condition, values_from = orderAcTime)
new_df2$EyPi <- as.numeric(new_df2$EyPi)
new_df2$EyVo <- as.numeric(new_df2$EyVo)
new_df2$PoPi <- as.numeric(new_df2$PoPi)
new_df2$PoVo <- as.numeric(new_df2$PoVo)
new_df2$ToTo <- as.numeric(new_df2$ToTo)
summary_table <- summary(new_df2)
##print(summary_table)


bigLog <- separate(bigLog, col = condition, into = c("interactionMethod"), sep = 4)
# Convert the orderAcTime column from character to numeric
bigLog$orderAcTime <- as.numeric(bigLog$orderAcTime)
bigLog$time_total <- as.numeric(bigLog$time_total)
bigLog$wrongOrder <- as.numeric(bigLog$wrongOrder)
bigLog$expired <- as.numeric(bigLog$expired)
bigLog$timePerCustomer <- as.numeric(bigLog$timePerCustomer)
















