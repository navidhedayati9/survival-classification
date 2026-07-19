# Logistic regression -----------------------------------------------------

candidate_predictors <- setdiff(names(hospital), c("ID", "SURVIVE"))

univariate_results <- purrr::map_dfr(candidate_predictors, function(predictor) {
  model <- stats::glm(
    stats::reformulate(predictor, response = "SURVIVE"),
    data = hospital,
    family = stats::binomial()
  )
  broom::tidy(model) |>
    dplyr::filter(term != "(Intercept)") |>
    dplyr::mutate(predictor = predictor, .before = 1)
})
readr::write_csv(univariate_results, file.path("results", "univariate_logistic_regression.csv"))

# Split by patient ID so repeated records from one patient cannot occur in both sets.
set.seed(analysis_seed)
patient_ids <- unique(hospital$ID)
training_ids <- sample(patient_ids, size = floor(0.8 * length(patient_ids)))
training_data <- dplyr::filter(hospital, ID %in% training_ids)
testing_data <- dplyr::filter(hospital, !ID %in% training_ids)
training_model_data <- dplyr::select(training_data, -ID)
testing_model_data <- dplyr::select(testing_data, -ID)

split_summary <- tibble::tibble(
  split = c("training", "testing"),
  patients = c(dplyr::n_distinct(training_data$ID), dplyr::n_distinct(testing_data$ID)),
  records = c(nrow(training_data), nrow(testing_data))
)
readr::write_csv(split_summary, file.path("results", "train_test_split.csv"))

logistic_formula <- SURVIVE ~ SBP + MCVP + UO + HG + SHOCK_TYP + SBP:UO
logistic_model <- stats::glm(logistic_formula, data = training_data, family = stats::binomial())

logistic_coefficients <- broom::tidy(logistic_model, conf.int = TRUE, exponentiate = TRUE)
readr::write_csv(logistic_coefficients, file.path("results", "logistic_odds_ratios.csv"))

logistic_probabilities <- stats::predict(logistic_model, newdata = testing_data, type = "response")
logistic_predictions <- factor(
  ifelse(logistic_probabilities > 0.5, "Died", "Survived"),
  levels = levels(hospital$SURVIVE)
)

logistic_metrics <- classification_metrics(testing_data$SURVIVE, logistic_predictions) |>
  dplyr::mutate(model = "Logistic regression", .before = 1)
save_confusion_matrix(testing_data$SURVIVE, logistic_predictions, "logistic_confusion_matrix.csv")
