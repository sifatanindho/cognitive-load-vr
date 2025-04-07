res.aov <- anova_test(data = bigLog, dv = time_total, wid = code, within = interactionMethod) # new one way repeated measures, also sign
get_anova_table(res.aov)

source("R\\functions.R")

analyze_data(bigLog, "time_total", "interactionMethod", "code")

mean_values <- aggregate(time_total ~ interactionMethod, bigLog, mean)
sd_values <- aggregate(time_total ~ interactionMethod, bigLog, sd)
results <- cbind(mean_values, sd_values$time_total)
colnames(results) <- c("Condition", "Mean", "SD")
print(knitr::kable(results, format = "latex", digits = 2, caption = "Frustration Scale"))
# Print the results
print(results)


# Perform the post hoc test
posthoc_results <- bigLog %>%
  pairwise_t_test(time_total ~ interactionMethod, p.adjust.method = "bonferroni")

# Print the results
print(posthoc_results) # nothing significant
