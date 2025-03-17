source("R\\functions.R")
# Process the TLX data for each condition
tlx_EV <- process_tlx_data(survey, "EV")
tlx_EV <- mutate_if(tlx_EV, is.character, as.numeric)
tlx_EV <- tlx_EV %>% mutate_at(vars(-ParticipantID), ~ . * 5)  # Exclude the 'ID' column
tlx_EV$tlxScore <- rowSums(select(tlx_EV, -ParticipantID))  # Exclude the 'ID' column
tlx_EV <- tlx_EV %>% mutate(tlxScore = tlxScore / 6)
#tlx_EV$ID <- survey$QPID
# For "EP" condition
tlx_EP <- process_tlx_data(survey, "EP")
tlx_EP <- mutate_if(tlx_EP, is.character, as.numeric)
tlx_EP <- tlx_EP %>% mutate_at(vars(-ParticipantID), ~ . * 5)  # Exclude the 'ParticipantID' column
tlx_EP$tlxScore <- rowSums(select(tlx_EP, -ParticipantID))  # Exclude the 'ParticipantID' column
tlx_EP <- tlx_EP %>% mutate(tlxScore = tlxScore / 6)

# For "Touch" condition
tlx_Touch <- process_tlx_data(survey, "Touch")
tlx_Touch <- mutate_if(tlx_Touch, is.character, as.numeric)
tlx_Touch <- tlx_Touch %>% mutate_at(vars(-ParticipantID), ~ . * 5)  # Exclude the 'ParticipantID' column
tlx_Touch$tlxScore <- rowSums(select(tlx_Touch, -ParticipantID))  # Exclude the 'ParticipantID' column
tlx_Touch <- tlx_Touch %>% mutate(tlxScore = tlxScore / 6)

# For "PoV" condition
tlx_PoV <- process_tlx_data(survey, "PoV")
tlx_PoV <- mutate_if(tlx_PoV, is.character, as.numeric)
tlx_PoV <- tlx_PoV %>% mutate_at(vars(-ParticipantID), ~ . * 5)  # Exclude the 'ParticipantID' column
tlx_PoV$tlxScore <- rowSums(select(tlx_PoV, -ParticipantID))  # Exclude the 'ParticipantID' column
tlx_PoV <- tlx_PoV %>% mutate(tlxScore = tlxScore / 6)

# For "PoPi" condition
tlx_PoPi <- process_tlx_data(survey, "PoPi")
tlx_PoPi <- mutate_if(tlx_PoPi, is.character, as.numeric)
tlx_PoPi <- tlx_PoPi %>% mutate_at(vars(-ParticipantID), ~ . * 5)  # Exclude the 'ParticipantID' column
tlx_PoPi$tlxScore <- rowSums(select(tlx_PoPi, -ParticipantID))  # Exclude the 'ParticipantID' column
tlx_PoPi <- tlx_PoPi %>% mutate(tlxScore = tlxScore / 6)

tlx_EV$Condition <- "EV"
tlx_EP$Condition <- "EP"
tlx_Touch$Condition <- "Touch"
tlx_PoPi$Condition <- "PoPi"
tlx_PoV$Condition <- "PoV"

# Combine all the condition data frames into one
TLXtotal <- bind_rows(tlx_EV, tlx_EP, tlx_Touch, tlx_PoPi, tlx_PoV)

# Select the total score column and add a new column to indicate the condition
tlx_EV_score <- tlx_EV %>% select(ParticipantID, Score = tlxScore) %>% mutate(Condition = "EV")
tlx_EP_score <- tlx_EP %>% select(ParticipantID, Score = tlxScore) %>% mutate(Condition = "EP")
tlx_Touch_score <- tlx_Touch %>% select(ParticipantID, Score = tlxScore) %>% mutate(Condition = "Touch")
tlx_PoPi_score <- tlx_PoPi %>% select(ParticipantID, Score = tlxScore) %>% mutate(Condition = "PoPi")
tlx_PoV_score <- tlx_PoV %>% select(ParticipantID, Score = tlxScore) %>% mutate(Condition = "PoV")

# Combine all the score data frames into one
TLXtotal_scores <- bind_rows(tlx_EV_score, tlx_EP_score, tlx_Touch_score, tlx_PoPi_score, tlx_PoV_score)

outliers <- identify_outliers(TLXtotal_scores, "Score")

leveneTest(Score ~ Condition, data = TLXtotal_scores)
# Check for Homogeneity of Variance
shapiro.test(TLXtotal_scores$Score)

res.aov <- anova_test(data = TLXtotal_scores, dv = Score, wid = ParticipantID, within = Condition) #new one way repeated measures, also sign
get_anova_table(res.aov)
# Calculate mean values
mean_values <- aggregate(Score ~ Condition, TLXtotal_scores, mean)
# Calculate standard deviations
sd_values <- aggregate(Score ~ Condition, TLXtotal_scores, sd)
# Calculate median values
median_values <- aggregate(Score ~ Condition, TLXtotal_scores, median)
# Combine mean_values, sd_values, and median_values into a single data frame
results <- cbind(mean_values$Score, sd_values$Score, median_values$Score)
colnames(results) <- c("Condition", "Mean", "SD", "Median")
print(knitr::kable(results, format = "latex", digits = 2, caption = "Results"))
# Print the results
print(results)

# Anova for subscales-------------------------------------------------------------------------------
res.aovMent <- anova_test(data = TLXtotal, dv = ment, wid = ParticipantID, within = Condition) #new one way repeated measures, also sign
get_anova_table(res.aovMent)
mean_values <- aggregate(ment ~ Condition, TLXtotal, mean)
sd_values <- aggregate(ment ~ Condition, TLXtotal, sd)
median_values <- aggregate(ment ~ Condition, TLXtotal, median)
results <- cbind(mean_values$ment, sd_values$ment, median_values$ment)
colnames(results) <- c("Condition", "Mean", "SD", "Median")
print(knitr::kable(results, format = "latex", digits = 2, caption = "Results"))
# Print the results
print(results)

res.aovPhys <- anova_test(data = TLXtotal, dv = phys, wid = ParticipantID, within = Condition)
get_anova_table(res.aovPhys) #close to sign.
mean_values <- aggregate(phys ~ Condition, TLXtotal, mean)
sd_values <- aggregate(phys ~ Condition, TLXtotal, sd)
median_values <- aggregate(phys ~ Condition, TLXtotal, median)
results <- cbind(mean_values$phys, sd_values$phys, median_values$phys)
colnames(results) <- c("Condition", "Mean", "SD", "Median")
print(knitr::kable(results, format = "latex", digits = 2, caption = "Results"))
# Print the results
print(results)

analyze_data(TLXtotal, "ment", "Condition", "ParticipantID")
posthoc_resultsPhys <- TLXtotal %>%
  pairwise_t_test(phys ~ Condition, p.adjust.method = "bonferroni")
posthoc_resultsPhys <- TukeyHSD(x = aov(as.formula(paste(phys, "~", Condition)), data = TLXtotal))
print(posthoc_resultsPhys)

res.aovPerf <- anova_test(data = TLXtotal, dv = perf, wid = ParticipantID, within = Condition)
get_anova_table(res.aovPerf)

res.aovEff <- anova_test(data = TLXtotal, dv = effort, wid = ParticipantID, within = Condition)
get_anova_table(res.aovEff)

res.aovFru <- anova_test(data = TLXtotal, dv = frust, wid = ParticipantID, within = Condition)
get_anova_table(res.aovFru)## close to significant

mean_values <- aggregate(frust ~ Condition, TLXtotal, mean)
sd_values <- aggregate(frust ~ Condition, TLXtotal, sd)
median_values <- aggregate(frust ~ Condition, TLXtotal, median)
results <- cbind(mean_values$frust, sd_values$frust, median_values$frust)
colnames(results) <- c("Condition", "Mean", "SD", "Median")
print(knitr::kable(results, format = "latex", digits = 2, caption = "Frustration Scale"))
# Print the results
print(results)

res.aovTemp <- anova_test(data = TLXtotal, dv = temp, wid = ParticipantID, within = Condition)
get_anova_table(res.aovTemp)


# Perform the post hoc test
posthoc_results <- TLXtotal_scores %>%
pairwise_t_test(Score ~ Condition, p.adjust.method = "bonferroni")
# Print the results
print(posthoc_results)
























