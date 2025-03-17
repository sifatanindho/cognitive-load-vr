library(conflicted)
library(dplyr)
library(readr)
library(stringr)
library(chron)
library(readxl)
library(tidyverse)
library(ggplot2)
library(ggpubr)
library(RColorBrewer)
library(car)
library(EnvStats)
library(ggsci)
library(vtable)
library(rstatix)
setwd("G:\\My Drive\\Uni_Dokumente\\EXP3/Results")
source("R\\functions.R")
survey <- read_excel("surveyEX.xlsx")
# Find all columns in the first row where the value contains "Condition"
# Find all columns where the column name contains "Condition"
condition_columns <- grep("Condition", colnames(survey))

# Define a function to change the values
change_values <- function(x) {
    case_when(
        x == 1 ~ "EV",
        x == 2 ~ "EP",
        x == 3 ~ "Touch",
        x == 4 ~ "PoPi",
        x == 5 ~ "PoV",
        TRUE ~ as.character(x)
    )
}
qpref_columns <- grep("QPref", colnames(survey))

# Change the values of the identified columns
survey <- survey %>%
    mutate_at(vars(qpref_columns), change_values)
# Change the values of the identified columns
survey <- survey %>%
    mutate_at(vars(condition_columns), change_values)

# Remove rows 2 and 3
survey <- survey[-c(1, 2), ]




