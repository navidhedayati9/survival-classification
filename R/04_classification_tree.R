# Classification tree -----------------------------------------------------

tree_formula <- SURVIVE ~ .
tree_model_full <- rpart::rpart(
  tree_formula,
  data = training_model_data,
  method = "class",
  control = rpart::rpart.control(cp = 0, xval = 10)
)

cp_table <- as.data.frame(tree_model_full$cptable)
minimum_error_row <- which.min(cp_table$xerror)
one_se_limit <- cp_table$xerror[minimum_error_row] + cp_table$xstd[minimum_error_row]
selected_row <- min(which(cp_table$xerror <= one_se_limit))
selected_cp <- cp_table$CP[selected_row]

tree_model <- rpart::prune(tree_model_full, cp = selected_cp)
tree_predictions <- predict(tree_model, newdata = testing_model_data, type = "class")

tree_metrics <- classification_metrics(testing_data$SURVIVE, tree_predictions) |>
  dplyr::mutate(model = "Classification tree", .before = 1)

readr::write_csv(cp_table, file.path("results", "classification_tree_cp_table.csv"))
readr::write_csv(
  tibble::enframe(tree_model$variable.importance, name = "variable", value = "importance"),
  file.path("results", "classification_tree_variable_importance.csv")
)
save_confusion_matrix(testing_data$SURVIVE, tree_predictions, "classification_tree_confusion_matrix.csv")

png(file.path("figures", "classification_tree.png"), width = 1800, height = 1200, res = 200)
plot(tree_model, margin = 0.1)
text(tree_model, use.n = TRUE, cex = 0.8)
invisible(dev.off())
