# Bagging and random forest -----------------------------------------------

set.seed(analysis_seed)
bagging_model <- ipred::bagging(
  tree_formula,
  data = training_model_data,
  nbagg = 1500,
  coob = TRUE
)
bagging_predictions <- predict(bagging_model, newdata = testing_model_data)
bagging_metrics <- classification_metrics(testing_data$SURVIVE, bagging_predictions) |>
  dplyr::mutate(model = "Bagging", .before = 1)
save_confusion_matrix(testing_data$SURVIVE, bagging_predictions, "bagging_confusion_matrix.csv")

set.seed(analysis_seed)
random_forest_model <- randomForest::randomForest(
  tree_formula,
  data = training_model_data,
  mtry = 4,
  ntree = 1500,
  importance = TRUE
)
random_forest_predictions <- predict(random_forest_model, newdata = testing_model_data)
random_forest_metrics <- classification_metrics(testing_data$SURVIVE, random_forest_predictions) |>
  dplyr::mutate(model = "Random forest", .before = 1)
save_confusion_matrix(testing_data$SURVIVE, random_forest_predictions, "random_forest_confusion_matrix.csv")

rf_importance <- randomForest::importance(random_forest_model) |>
  as.data.frame() |>
  tibble::rownames_to_column("variable")
readr::write_csv(rf_importance, file.path("results", "random_forest_variable_importance.csv"))

png(file.path("figures", "random_forest_variable_importance.png"), width = 1600, height = 1200, res = 200)
randomForest::varImpPlot(random_forest_model, main = "Random forest variable importance")
invisible(dev.off())
