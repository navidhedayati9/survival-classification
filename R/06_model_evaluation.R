# Model comparison --------------------------------------------------------

model_metrics <- dplyr::bind_rows(
  logistic_metrics,
  tree_metrics,
  bagging_metrics,
  random_forest_metrics
) |>
  dplyr::arrange(dplyr::desc(accuracy))

readr::write_csv(model_metrics, file.path("results", "model_performance.csv"))

performance_plot <- ggplot2::ggplot(
  model_metrics,
  ggplot2::aes(x = stats::reorder(model, accuracy), y = accuracy, fill = model)
) +
  ggplot2::geom_col(show.legend = FALSE) +
  ggplot2::coord_flip() +
  ggplot2::scale_y_continuous(labels = scales::percent_format(accuracy = 1), limits = c(0, 1)) +
  ggplot2::labs(x = NULL, y = "Test accuracy", title = "Out-of-sample model performance") +
  ggplot2::theme_minimal(base_size = 11)

ggplot2::ggsave(
  file.path("figures", "model_performance.png"),
  performance_plot,
  width = 8,
  height = 5,
  dpi = 300
)
