rankingdata <- process_ranking_data(survey)
rankingdata <- rankingdata[, 7:11]
rankingdata <- tibble::rownames_to_column(rankingdata, "ID")
rankingdata_long <- gather(rankingdata, Condition, Score, -ID)
summary(rankingdata)
library(ggsci)
source("R\\functions.R")
analyze_data(rankingdata_long, "Score", "Condition", "ID")

