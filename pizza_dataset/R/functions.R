# Function to calculate odd and even columns in SUS
subtraction_func <- function(data) {
  # Loop through each element of the data frame
  for (i in 1:nrow(data)) {
    for (j in 1:ncol(data)) {
      # Check if the column is numeric
      if (is.numeric(data[, j])) {
        if (j %% 2 == 1) { # Odd entry
          data[i, j] <- data[i, j] - 1
        } else { # Even entry
          data[i, j] <- 5 - data[i, j]
        }
      }
    }
  }
  return(data)
}


process_sus_data <- function(survey, condition) {
  SUStemp <- data.frame()

  # Loop through each row in the data frame
  for (i in 1:nrow(survey)) {
    # Find the index of the condition value in the current row
    cond_index <- which(survey[i, ] == condition)

    # Check if a "Cond1" value was found in the row
    if (length(cond_index) > 0) {
      # Extract the next survey cells after the "Cond1" value in the current row
      selected_data <- survey[i, (cond_index + 7):(cond_index + 16)]

      # Set column names of selected_data to match the original data frame
      colnames(selected_data) <- paste0("SUS", 1:10)

      SUStemp <- rbind(SUStemp, selected_data)
    }
  }
  return(SUStemp)
}

process_tlx_data <- function(survey, condition) {
  tlxtemp <- data.frame()

  # Loop through each row in the data frame
  for (i in 1:nrow(survey)) {
    # Find the index of the condition value in the current row
    cond_index <- which(survey[i, ] == condition)

    # Check if a "condition" value was found in the row
    if (length(cond_index) > 0) {
      # Extract the next survey cells after the "condition" value in the current row
      selected_data <- survey[i, (cond_index + 1):(cond_index + 6)]

      # Add the participant ID to the selected_data
      selected_data$ID <- survey$QPID[i]

      # Set column names of selected_data to match the original data frame
      colnames(selected_data) <- c(assignNames(), "ParticipantID")

      tlxtemp <- rbind(tlxtemp, selected_data)
    }
  }

  return(tlxtemp)
}

assignNames <- function() {
  c1 <- "ment"
  c2 <- "phys"
  c3 <- "temp"
  c4 <- "perf"
  c5 <- "effort"
  c6 <- "frust"

  tlxnames <- c(c1, c2, c3, c4, c5, c6)
  return(tlxnames)
}

process_ranking_data <- function(my_data) {
  tempdata <- my_data
  tempdata <- tempdata %>%
    remove_rownames() %>%
    column_to_rownames(var = "QPID")
  tempdata <- tempdata[, 95:99] # check which columns are ranks
  tempdata$Touch <- NA
  tempdata$EV <- NA
  tempdata$PoV <- NA
  tempdata$EP <- NA
  tempdata$PoPi <- NA

  # Loop through every row
  for (row in 1:nrow(tempdata)) {
    # Loop through every column in the current row
    for (col in 1:6) {
      # Do something with the current cell
      switch(tempdata[row, col],
        "Touch" = {
          # Code to execute if condition is "ED"
          tempdata$touch[row] <- 6 - col
        },
        "EV" = {
          # Code to execute if condition is "EH"
          tempdata$EV[row] <- 6 - col
        },
        "PoV" = {
          # Code to execute if condition is "TD"
          tempdata$PoV[row] <- 6 - col
        },
        "EP" = {
          # Code to execute if condition is "TH"
          tempdata$EP[row] <- 6 - col
        },
        "PoPi" = {
          # Code to execute if condition is "VD"
          tempdata$PoPi[row] <- 6 - col
        },
        {
          # Code to execute if no match is found
          print(tempdata[row, col])
        }
      )
    }
  }
  return(tempdata)
}

process_log <- function(filename) {
  fileN <- filename
  probandenCode <- gsub(".csv", "", filename)
  probandenCode <- gsub("Data/Participant", "", probandenCode) # nolint

  logData <- read.csv(fileN, header = TRUE, sep = ";")
  logData <- logData[logData$selectCondition != "", ]

  logData$condition <- paste(substr(logData$selectCondition, 1, 2), substr(logData$activateCondition, 1, 2), sep = "")

  # Split logData into subsets based on the condition
  split_data <- split(logData, logData$condition)

  tempLog <- data.frame()

  # Process each subset of data separately
  for (name in names(split_data)) {
    codeT <- probandenCode
    conditionT <- name
    # message("condition" , conditionT)
    time_totalT <- calcTotalTime(split_data[[name]])
    # message("time_totalT: ", time_totalT)
    wrongOrderT <- calcWrongOrder(split_data[[name]])
    # message("wrongOrderT: ", wrongOrderT)
    dismissedT <- calcDismissed(split_data[[name]])
    # message("dismissedT: ", dismissedT)
    expiredT <- calcExpired(split_data[[name]])
    # message("expiredT: ", expiredT)
    orderAcceptance <- calcAcceptedOrderTime(split_data[[name]])
    timePerCustomerT <- calcPerCustomer(split_data[[name]])

    new_row <- c(
      code = codeT,
      condition = conditionT,
      time_total = time_totalT,
      wrongOrder = wrongOrderT,
      expired = expiredT,
      orderAcTime = orderAcceptance,
      timePerCustomer = timePerCustomerT
    )


    tempLog <- rbind(tempLog, new_row)
  }

  return(tempLog)
}

# This function takes a data frame called dataset as input and calculates the time difference between the first row and the row where the id column is equal to 1337
calcTotalTime <- function(dataset) {
  # Extract the first value of the Time_s column
  time1 <- head(dataset$Time_s, n = 1)

  # Extract the value of the Time_s column where the id column is equal to 1337
  time2 <- dataset$Time_s[dataset$id == 1337]
  # Convert the time1 and time2 values to POSIXct format with the format "%M:%OS"
  t1 <- as.POSIXct(time1, format = "%M:%OS")
  t2 <- as.POSIXct(time2, format = "%M:%OS")
  # Print the formatted time1 and time2 values to the console
  # cat(time1,"\n")
  # cat(time2,"\n")
  # Calculate the time difference between t2 and t1 in seconds
  ttotal <- difftime(t2, t1, units = "secs")
  ttotal <- round(ttotal, 3)
  # Return the time difference as output
  return(ttotal)
}
calcTimeDiff <- function(time1, time2) {
  # Convert the time1 and time2 values to POSIXct format with the format "%M:%OS"
  t1 <- as.POSIXct(time1, format = "%M:%OS")
  t2 <- as.POSIXct(time2, format = "%M:%OS")
  # Print the formatted time1 and time2 values to the console
  # cat(time1,"\n")
  # cat(time2,"\n")
  # Calculate the time difference between t2 and t1 in seconds
  ttotal <- difftime(t2, t1, units = "secs")

  # Return the time difference as output
  return(ttotal)
}
calcWrongOrder <- function(dataset) {
  num_wrong <- sum(dataset$event == "Wrong")
  return(num_wrong)
}
calcDismissed <- function(dataset) {
  num_wrong <- sum(dataset$event == "dismissed")
  return(num_wrong)
}
calcExpired <- function(dataset) {
  num_wrong <- sum(dataset$event == "expired")
  return(num_wrong)
}
calcAcceptedOrderTime <- function(dataset) {
  # temp_df <- subset(dataset, duplicated(dataset$id) | duplicated(dataset$id, fromLast = TRUE))
  dup_ids <- unique(dataset$id[duplicated(dataset$id)])
  temp_df <- subset(dataset, id %in% dup_ids)
  temp_df <- subset(temp_df, event %in% c("sent", "accepted"))
  temp_df <- subset(temp_df, source != "Food Notification")
  temp_df <- temp_df[order(temp_df$id), ]
  temp_df <- temp_df[!duplicated(temp_df[c("event", "id")]), ]

  id_counts <- table(temp_df$id)
  temp_df <- temp_df[temp_df$id %in% names(id_counts[id_counts > 1]), ]
  timeList <- list()
  i <- 0

  # Loop over the data frame in steps of 2 rows
  for (i in seq(1, nrow(temp_df), by = 2)) {
    # Check if there are at least two rows left in the data frame
    if (i + 1 <= nrow(temp_df)) {
      # Extract the first two rows of the data frame
      time_diff <- calcTimeDiff(temp_df$Time_s[i], temp_df$Time_s[i + 1])
      time_diff <- as.numeric(time_diff)
      timeList <- append(timeList, time_diff)
    } else {

    }
  }
  times_mean <- mean(unlist(timeList))
  return(times_mean)
}
calcFoodDismissals <- function(dataset) {
  # @temp_df <- subset(dataset, duplicated(dataset$id) | duplicated(dataset$id, fromLast = TRUE))
  dup_ids <- unique(dataset$id[duplicated(dataset$id)])
  temp_df <- subset(dataset, id %in% dup_ids)
  temp_df <- subset(temp_df, event %in% c("sent", "dismissed"))
  temp_df <- subset(temp_df, source != "Order Notification")
  temp_df <- temp_df[order(temp_df$id, temp_df$Time_s), ]
  temp_df <- temp_df[!duplicated(temp_df[c("event", "id")]), ]

  id_counts <- table(temp_df$id)
  temp_df <- temp_df[temp_df$id %in% names(id_counts[id_counts > 1]), ]

  timeList <- list()
  i <- 0
  if (nrow(temp_df) == 0) {
    return(0)
  } else {
    # Lop over the data frame in steps of 2 rows
    for (i in seq(1, nrow(temp_df), by = 2)) {
      # Check if there are at least two rows left in the data frame
      if (i + 1 <= nrow(temp_df)) {
        # Extract the first two rows of the data frame
        time_diff <- calcTimeDiff(temp_df$Time_s[i], temp_df$Time_s[i + 1])
        # cat(temp_df$Time_s[i], temp_df$Time_s[i + 1], "\n")
        # print(temp_df)
        time_diff <- as.numeric(time_diff)
        timeList <- append(timeList, time_diff)
      } else {

      }
    }
  }
  # print(timeList)
  times_mean <- mean(unlist(timeList))
  return(times_mean)
}
calcPerCustomer <- function(dataset) {
  # @temp_df <- subset(dataset, duplicated(dataset$id) | duplicated(dataset$id, fromLast = TRUE))
  dup_ids <- unique(dataset$id[duplicated(dataset$id)])
  temp_df <- subset(dataset, id %in% dup_ids)
  temp_df <- subset(temp_df, event %in% c("accepted", "complete"))
  temp_df <- subset(temp_df, source != "Food Notification")
  temp_df <- temp_df[order(temp_df$id, temp_df$Time_s), ]
  temp_df <- temp_df[!duplicated(temp_df[c("event", "id")]), ]

  id_counts <- table(temp_df$id)
  temp_df <- temp_df[temp_df$id %in% names(id_counts[id_counts > 1]), ]

  timeList <- list()
  i <- 0
  if (nrow(temp_df) == 0) {
    return(120)
  } else {
    # Lop over the data frame in steps of 2 rows
    for (i in seq(1, nrow(temp_df), by = 2)) {
      # Check if there are at least two rows left in the data frame
      if (i + 1 <= nrow(temp_df)) {
        # Extract the first two rows of the data frame
        time_diff <- calcTimeDiff(temp_df$Time_s[i], temp_df$Time_s[i + 1])
        # cat(temp_df$Time_s[i], temp_df$Time_s[i + 1], "\n")
        # print(temp_df)
        time_diff <- as.numeric(time_diff)
        timeList <- append(timeList, time_diff)
      } else {

      }
    }
  }
  # print(timeList)
  times_mean <- mean(unlist(timeList))
  return(times_mean)
}


analyze_data <- function(data, dv, within, wid) {
  print("---------------------------------------")

  data[[within]] <- gsub("EyPi", "GP", data[[within]])
  data[[within]] <- gsub("EyVo", "GS", data[[within]])
  data[[within]] <- gsub("PoPi", "PP", data[[within]])
  data[[within]] <- gsub("PoVo", "PS", data[[within]])
  data[[within]] <- gsub("ToTo", "Touch", data[[within]])

  # FOR RANKING
  data[[within]] <- gsub("EP", "GP", data[[within]])
  data[[within]] <- gsub("EV", "GS", data[[within]])
  data[[within]] <- gsub("PoPi", "PP", data[[within]])
  data[[within]] <- gsub("PoV", "PS", data[[within]])
  data[[within]] <- gsub("touch", "Touch", data[[within]])


  res.aov <- anova_test(data = data, dv = dv, wid = wid, within = within)
  anova_table <- get_anova_table(res.aov)
  # str(anova_table)
  print("ANOVA table:")
  print(anova_table)
  F_value <- anova_table$F[1]
  p_value <- anova_table$p[1]

  # Check if the p value is less than 0.05 (considered significant)
  if (p_value < 0.05) {
    # Construct the output string
    output <- paste("We found a significant effect of \textit{interaction technique} on the ", dv,
      " score ($F(", anova_table$DFn[1], ", ", anova_table$DFd[1], ") = ",
      round(F_value, 3), "$, $p = ", round(p_value, 3), "$).",
      sep = ""
    )

    # Print the output string
    print(output)

    # Perform the post hoc test
    posthoc_results <- TukeyHSD(x = aov(as.formula(paste(dv, "~", within)), data = data))

    # Print the results
    print("Post hoc test results:")
    print(posthoc_results)

    # Print a message for each pairwise comparison
    for (stratum in names(posthoc_results)) {
      print(paste("Stratum:", stratum))

      # Get the results for this stratum
      stratum_results <- posthoc_results[[stratum]]

      # Iterate over the rows of the stratum_results matrix
      for (i in 1:nrow(stratum_results)) {
        # Get the comparison, difference, lower and upper ends of the confidence interval, and p-value
        comparison <- rownames(stratum_results)[i]

        p_value <- stratum_results[i, "p adj"]

        # Check if the p value is less than 0.05 (considered significant)
        if (p_value < 0.05) {
          print(paste(
            "We found a significant difference between", comparison,
            "Adjusted p-value:", round(p_value, 3)
          ))
        } else {
          print(paste(
            "No significant difference for", comparison,
            "Adjusted p-value:", round(p_value, 3)
          ))
        }
      }
    }
  } else {
    # Construct a different output string
    output <- paste("We found no significant effect of \textit{interaction technique} on the ", dv,
      " score ($F(", res.aov$ANOVA$DFn[1], ", ", res.aov$ANOVA$DFd[1], ") = ",
      round(F_value, 3), "$, $p = ", round(p_value, 3), "$).",
      sep = ""
    )

    # Print the output string
    print(output)
  }

  # Calculate mean and SD
  mean_values <- aggregate(data[[dv]] ~ data[[within]], data, mean)
  sd_values <- aggregate(data[[dv]] ~ data[[within]], data, sd)
  median_values <- aggregate(data[[dv]] ~ data[[within]], data, median)
  results <- cbind(mean_values, sd_values[2], median_values[2])
  colnames(results) <- c("Condition", "Mean", "SD", "Median")

  # Print the results
  print(knitr::kable(results, format = "latex", digits = 2, caption = "Results"))
  print(results)
  # Create the plot
 # Create the plot

lower <- results$Mean - results$SD
upper <- results$Mean + results$SD
palette <- brewer.pal(5, "Dark2")

p <- ggplot(results, aes(x = Condition, y = Mean, fill = Condition)) +
  geom_bar(stat = "identity", position = "dodge") +
  geom_errorbar(aes(ymin = lower, ymax = upper), width = 0.35, position = position_dodge(0.9), size = 1.5) +
  labs(x = "Condition", y = "Mean") +
  theme_minimal() +
 theme(axis.text.x = element_text(angle = 45, hjust = 1, size = 18),  # Increase the font size of x-axis text
        axis.text.y = element_text(size = 18),  # Increase the font size of y-axis text
        plot.title = element_text(size = 20),  # Increase the font size of the title
        axis.title = element_text(size = 18)) +  # Increase the font size of axis titles
  scale_fill_manual(values = palette) +
  theme(legend.position = "none")


  ggsave("plot.png", p)
}
