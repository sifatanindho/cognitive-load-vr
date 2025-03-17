source("R\\functions.R")
# Subj Measure
analyze_data(SUStotal, "score", "Condition", "ID")
analyze_data(TLXtotal, "phys", "Condition", "ParticipantID")
analyze_data(bigLog, "time_total", "interactionMethod", "code")
analyze_data(bigLog, "orderAcTime", "interactionMethod", "code")
analyze_data(bigLog, "timePerCustomer", "interactionMethod", "code")
analyze_data(bigLog, "wrongOrder", "interactionMethod", "code")
analyze_data(bigLog, "expired", "interactionMethod", "code")



# res.aov <- anova_test(data = bigLog, dv = orderAcTime, wid = code, within = interactionMethod)
#anova_table <- get_anova_table(res.aov)
#print(anova_table)
#kruskal.test(orderAcTime ~ interactionMethod, data = bigLog)
#pairwise.wilcox.test(bigLog$orderAcTime, bigLog$interactionMethod, p.adjust.method = "bonferroni")
