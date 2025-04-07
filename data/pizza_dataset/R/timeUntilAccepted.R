
# ASSUMPTION CHECK
table(bigLog$interactionMethod, bigLog$list)
my_comparisons <- list(c("E", "T"), c("T", "V"), c("E", "V"))
png("accepted.png", width = 2000, height = 2400, res = 200)
ggboxplot(bigLog,
    x = "interactionMethod", y = "orderAcTime", fill = "list"
) +
    scale_x_discrete(labels = c("Gaze", "Touch", "Voice")) +
    labs(
        x = "Interaction Method", y = "Time until order was accepted (s)",
        fill = "List Type"
    ) +
    stat_compare_means(
        comparisons = my_comparisons,
        map_signif_level = TRUE, test = "aov", label = "p.signif", show.legend = F, size = 13
    ) +
    scale_fill_d3(labels = c("World", "Hand")) +
    theme(text = element_text(size = 36)) +
    scale_y_continuous(breaks = seq(0, 200, by = 50), labels = seq(0, 200, by = 50))
dev.off()
model <- aov(orderAcTime ~ interactionMethod * list, data = bigLog)
# Check for Homogeneity of Variance
leveneTest(orderAcTime ~ interactionMethod * list, data = bigLog) # this is not significant, so we can assume homogeneity of variance

# Check for Normality\
plot(model, 2) # This looks like a normal distribution
test <- rosnerTest(bigLog$orderAcTime, k = 3) # this also checks, its normal
test
res.aov <- anova_test(data = bigLog, dv = orderAcTime, wid = code, within = interactionMethod) #new one way repeated measures, also sign
get_anova_table(res.aov)
# Calculate the mean of wrongOrder for each level of interactionMethod
mean_values <- aggregate(orderAcTime ~ interactionMethod, bigLog, mean)

# Print the mean values
print(mean_values)

# Perform the post hoc test
posthoc_results <- bigLog %>%
  pairwise_t_test(orderAcTime ~ interactionMethod, p.adjust.method = "bonferroni")

# Print the results
print(posthoc_results) #touch better than everything except eye Pinch
