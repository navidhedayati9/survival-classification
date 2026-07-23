# Exploratory analysis ----------------------------------------------------

categorical_summary <- hospital |>
  dplyr::count(SURVIVE, Sex, SHOCK_TYP, name = "n")
readr::write_csv(categorical_summary, file.path("results", "categorical_summary.csv"))

numeric_variables <- c("SBP", "DBP", "MAP", "UO", "HG", "MCVP", "AGE", "HT")
numeric_summary <- hospital |>
  dplyr::group_by(SURVIVE) |>
  dplyr::summarise(
    dplyr::across(
      dplyr::all_of(numeric_variables),
      list(mean = mean, median = median, sd = sd, min = min, max = max),
      .names = "{.col}_{.fn}"
    ),
    .groups = "drop"
  )
readr::write_csv(numeric_summary, file.path("results", "numeric_summary.csv"))

plot_data <- hospital |>
  dplyr::select(SURVIVE, dplyr::all_of(numeric_variables)) |>
  tidyr::pivot_longer(-SURVIVE, names_to = "variable", values_to = "value")

clinical_boxplots <- ggplot2::ggplot(
  plot_data,
  ggplot2::aes(x = SURVIVE, y = value, fill = SURVIVE)
) +
  ggplot2::geom_boxplot(show.legend = FALSE, outlier.alpha = 0.4) +
  ggplot2::facet_wrap(~variable, scales = "free_y", ncol = 3) +
  ggplot2::labs(x = NULL, y = NULL, title = "Clinical measures by survival status") +
  ggplot2::theme_minimal(base_size = 11)

ggplot2::ggsave(
  file.path("figures", "clinical_measures_by_survival.png"),
  clinical_boxplots,
  width = 10,
  height = 8,
  dpi = 300
)

correlation_variables <- c("HT", "SBP", "MAP", "DBP", "MCVP", "BSI", "CI", "AT", "MCT", "UO", "HG", "HCT")
correlation_matrix <- stats::cor(hospital[correlation_variables], use = "pairwise.complete.obs")
readr::write_csv(
  tibble::rownames_to_column(as.data.frame(correlation_matrix), "variable"),
  file.path("results", "correlation_matrix.csv")
)

png(file.path("figures", "predictor_correlations.png"), width = 1800, height = 1600, res = 200)
corrplot::corrplot(correlation_matrix, method = "color", type = "upper", tl.cex = 0.8)
invisible(dev.off())
