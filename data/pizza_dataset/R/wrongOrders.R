# ----------------Amount of wrong orders---------------------------------------

# ASSUMPTION CHECK
table(bigLog$interactionMethod)

ggboxplot(bigLog,
  x = "interactionMethod", y = "wrongOrder") +
  scale_x_discrete(labels = c("Gaze", "Touch", "Voice")) +
  labs(x = "Interaction Method", y = "Amount of incorrect orders") +
  stat_compare_means(
    comparisons = my_comparisons,
    map_signif_level = TRUE, test = "aov", label = "p.signif"
  ) +
  theme(text = element_text(size = 26))

#model <- aov(wrongOrder ~ interactionMethod + Error(code/interactionMethod), data = bigLog)#old anova

# Check for Homogeneity of Variance
leveneTest(wrongOrder ~ interactionMethod, data = bigLog) # this is not significant, so we can assume homogeneity of variance

# Check for Normality
plot(model, 2) # This is a little normal
test <- rosnerTest(bigLog$wrongOrder, k = 3) 
testf  # 3 outlier detected
res.aov <- anova_test(data = bigLog, dv = wrongOrder, wid = code, within = interactionMethod) #new one way repeated measures, also sign
get_anova_table(res.aov)
# Calculate the mean of wrongOrder for each level of interactionMethod
mean_values <- aggregate(wrongOrder ~ interactionMethod, bigLog, mean)

# Print the mean values
print(mean_values)

# Perform the post hoc test
posthoc_results <- bigLog %>%
  pairwise_t_test(wrongOrder ~ interactionMethod, p.adjust.method = "bonferroni")

# Print the results
print(posthoc_results)
