# ----------------Customer Expirations---------------------------------------

# ASSUMPTION CHECK
table(bigLog$interactionMethod, bigLog$list)

my_comparisons <- list(c("E", "T"), c("T", "V"), c("E", "V"))
# Plot the data
ggboxplot(bigLog,
    x = "interactionMethod", y = "expired", fill = "list") +
    # scale_y_continuous(limits = c(0, 120), trans = "sqrt") +
    scale_x_discrete(labels = c("Gaze", "Touch", "Voice")) +
    labs(
        x = "Interaction Method", y = "Number of expired customers",
        fill = "List Type"
    ) +
    stat_compare_means(
        comparisons = my_comparisons,
        map_signif_level = TRUE, test = "aov", label = "p.signif"
    ) +
    scale_fill_d3(labels = c("World", "Hand")) +
    theme(text = element_text(size = 26))



model <- aov(expired ~ interactionMethod * list, data = bigLog)
# Check for Homogeneity of Variance
leveneTest(expired ~ interactionMethod * list, data = bigLog) # this is not significant, so we can assume homogeneity of variance

# Check for Normality\
plot(model, 2) # This looks like a normal distribution
test <- rosnerTest(bigLog$expired, k = 3) # this also checks, its normal 
test
# Print ANOVA results
res.aov <- anova_test(data = bigLog, dv = expired, wid = code, within = interactionMethod) #new one way repeated measures, also sign
get_anova_table(res.aov)
# Calculate the mean of wrongOrder for each level of interactionMethod
mean_values <- aggregate(expired ~ interactionMethod, bigLog, mean)

# Print the mean values
print(mean_values)

# Perform the post hoc test
posthoc_results <- bigLog %>%
  pairwise_t_test(expired ~ interactionMethod, p.adjust.method = "bonferroni")

# Print the results
print(posthoc_results) # Nothing significant


