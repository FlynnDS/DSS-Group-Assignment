# ==============================================================================
# STATISTICAL ANALYSIS - MIXED EFFECTS MODELS
# ==============================================================================
#
# This script generates all statistical tests for the Results section 
# (Section \ref{sec:results}) of the paper.
#
# PAPER MAPPING:
# --------------
# - RQ: Genre × Feature Interaction    → Table \ref{tab:sq1_results} (H1)
# - SQ2: Feature Awareness              → Table \ref{tab:sq2_results} (H2)
# - SQ3: Perception Accuracy            → Table \ref{tab:sq3_results} (H3)
# - SQ4: Musical Sophistication         → Table \ref{tab:sq4_results} (H4)
#
# OUTPUT: statistical_results_clean.txt (redirect stdout when running)
#
# All models use mixed effects with random intercepts for participants:
# lmer(outcome ~ predictors + (1 | participant_id), data = ...)
#
# ==============================================================================

library(lmerTest)
library(emmeans)

rating_data <- read.csv('rating_data_long.csv')
perception_data <- read.csv('perception_data_long.csv')

cat("\n")
cat("========================================================================\n")
cat("RQ: GENRE × FEATURE INTERACTION\n")
cat("========================================================================\n")
cat("PAPER: Sub-Question 1, Table \\ref{tab:sq1_results}\n")
cat("HYPOTHESIS: H1 - Feature similarity compensates for genre mismatch\n")
cat("FIGURE: Figure \\ref{fig:sq1_interaction}\n")
cat("========================================================================\n\n")
model_rq <- lmer(rating ~ same_genre * same_features + (1 | participant_id), 
                 data = rating_data)
summary(model_rq)
cat("\n--- Estimated Marginal Means ---\n")
emm_rq <- emmeans(model_rq, ~ same_genre * same_features)
print(emm_rq)
cat("\n--- Pairwise Comparisons ---\n")
print(pairs(emm_rq))

cat("\n\n")
cat("========================================================================\n")
cat("SQ1: FEATURE COMPENSATION\n")
cat("Can similar features compensate for different genre?\n")
cat("========================================================================\n")
cat("PAPER: Sub-Question 1 (continued from RQ analysis above)\n")
cat("HYPOTHESIS: H1 - Contrast comparing compensation effect\n")
cat("FIGURE: Figure \\ref{fig:sq1_compensation}\n")
cat("========================================================================\n\n")
print(contrast(emm_rq, list("Compensation Effect" = c(-1, 0, 1, 0))))

cat("\n\n")
cat("========================================================================\n")
cat("SQ2: FEATURE AWARENESS (Individual Features)\n")
cat("Do users rate songs higher when they selected that feature?\n")
cat("========================================================================\n")
cat("PAPER: Sub-Question 2, Table \\ref{tab:sq2_results}\n")
cat("HYPOTHESIS: H2 - Users who value features rate matching songs higher\n")
cat("FIGURES: \\ref{fig:sq2_awareness} and \\ref{fig:sq2_individual}\n")
cat("========================================================================\n\n")
rating_similar <- rating_data[rating_data$same_features == 1, ]

for (feat in list(
  list(name = "DANCEABILITY", var = "selected_danceability"),
  list(name = "VALENCE", var = "selected_valence"),
  list(name = "ENERGY", var = "selected_energy"),
  list(name = "ACOUSTICNESS", var = "selected_acousticness")
)) {
  cat("--- ", feat$name, " ---\n", sep = "")
  formula_str <- paste0("rating ~ ", feat$var, " + (1 | participant_id)")
  model <- lmer(as.formula(formula_str), data = rating_similar)
  print(summary(model))
  cat("\nEstimated Marginal Means:\n")
  print(emmeans(model, as.formula(paste0("~ ", feat$var))))
  cat("\n")
}

cat("\n")
cat("========================================================================\n")
cat("SQ3: PERCEPTION ACCURACY BY FEATURE IMPORTANCE\n")
cat("Are users better at recognizing features they find important?\n")
cat("========================================================================\n")
cat("PAPER: Sub-Question 3, Table \\ref{tab:sq3_results}\n")
cat("HYPOTHESIS: H3 - Better recognition for important features\n")
cat("FIGURE: Figure \\ref{fig:sq3_perception}\n")
cat("METHOD: Binned error (0 if actual value within rated bin)\n")
cat("========================================================================\n\n")
cat("--- Overall Effect ---\n")
model_sq3 <- lmer(error ~ feature_is_important + (1 | participant_id), 
                  data = perception_data)
print(summary(model_sq3))
cat("\nEstimated Marginal Means:\n")
print(emmeans(model_sq3, ~ feature_is_important))

cat("\n--- By Individual Feature ---\n")
for (feat in c('danceability', 'valence', 'energy', 'acousticness')) {
  cat("\n", toupper(feat), ":\n", sep = "")
  feat_data <- perception_data[perception_data$feature == feat, ]
  print(summary(lmer(error ~ feature_is_important + (1 | participant_id), data = feat_data)))
}

cat("\n\n")
cat("========================================================================\n")
cat("SQ4: MUSICAL SOPHISTICATION EFFECTS\n")
cat("Do users with higher musical sophistication recognize features better?\n")
cat("========================================================================\n")
cat("PAPER: Sub-Question 4, Table \\ref{tab:sq4_results}\n")
cat("HYPOTHESIS: H4 - Higher MSI → better feature recognition\n")
cat("FIGURE: Figure \\ref{fig:sq4_sophistication}\n")
cat("MEASURES: MSAE (Active Engagement) and MSE (Emotions)\n")
cat("========================================================================\n\n")

cat("--- Overall Effect (MSAE + MSE) ---\n")
print(summary(lmer(error ~ MSAE + MSE + (1 | participant_id), data = perception_data)))

cat("\n--- Active Engagement (MSAE) by Feature ---\n")
for (feat in c('danceability', 'valence', 'energy', 'acousticness')) {
  cat("\n", toupper(feat), ":\n", sep = "")
  feat_data <- perception_data[perception_data$feature == feat, ]
  print(summary(lmer(error ~ MSAE + (1 | participant_id), data = feat_data)))
}

cat("\n--- Emotions (MSE) by Feature ---\n")
for (feat in c('danceability', 'valence', 'energy', 'acousticness')) {
  cat("\n", toupper(feat), ":\n", sep = "")
  feat_data <- perception_data[perception_data$feature == feat, ]
  print(summary(lmer(error ~ MSE + (1 | participant_id), data = feat_data)))
}

cat("\n--- Interaction: Feature Importance × MSAE ---\n")
print(summary(lmer(error ~ feature_is_important * MSAE + (1 | participant_id), data = perception_data)))

cat("\n")
cat("========================================================================\n")
cat("END OF ANALYSIS\n")
cat("========================================================================\n")
