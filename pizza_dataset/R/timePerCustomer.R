# ----------------Total time per Customer---------------------------------------


# Print ANOVA results
res.aov <- anova_test(data = bigLog, dv = timePerCustomer, wid = code, within = interactionMethod) #new one way repeated measures, also sign
get_anova_table(res.aov)

mean_values <- aggregate(timePerCustomer ~ interactionMethod, bigLog, mean)
sd_values <- aggregate(timePerCustomer ~ interactionMethod, bigLog, sd)
results <- cbind(mean_values, sd_values$timePerCustomer)
colnames(results) <- c("Condition", "Mean", "SD")
print(knitr::kable(results, format = "latex", digits = 2, caption = "Frustration Scale"))
# Print the results
print(results)


# Perform the post hoc test
posthoc_results <- bigLog %>%
  pairwise_t_test(timePerCustomer ~ interactionMethod, p.adjust.method = "bonferroni")

# Print the results
print(posthoc_results) # nothing significant
