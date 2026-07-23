# Project setup -----------------------------------------------------------

required_packages <- c(
  "broom", "corrplot", "dplyr", "ggplot2", "purrr",
  "readr", "tibble", "tidyr"
)

missing_packages <- required_packages[
  !vapply(required_packages, requireNamespace, logical(1), quietly = TRUE)
]

if (length(missing_packages) > 0L) {
  stop(
    "Install the required packages before running the analysis: ",
    paste(missing_packages, collapse = ", "),
    call. = FALSE
  )
}

dir.create("data/processed", recursive = TRUE, showWarnings = FALSE)
dir.create("figures", recursive = TRUE, showWarnings = FALSE)
dir.create("results", recursive = TRUE, showWarnings = FALSE)

analysis_seed <- 4L

classification_metrics <- function(truth, estimate, positive = "Died") {
  truth <- factor(truth, levels = c("Survived", "Died"))
  estimate <- factor(estimate, levels = levels(truth))
  confusion <- table(truth = truth, estimate = estimate)

  tp <- confusion[positive, positive]
  fn <- sum(confusion[positive, ]) - tp
  fp <- sum(confusion[, positive]) - tp
  tn <- sum(confusion) - tp - fn - fp

  tibble::tibble(
    accuracy = (tp + tn) / sum(confusion),
    misclassification_rate = (fp + fn) / sum(confusion),
    sensitivity = if ((tp + fn) == 0) NA_real_ else tp / (tp + fn),
    specificity = if ((tn + fp) == 0) NA_real_ else tn / (tn + fp)
  )
}

save_confusion_matrix <- function(truth, estimate, filename) {
  confusion <- as.data.frame(table(truth = truth, estimate = estimate))
  readr::write_csv(confusion, file.path("results", filename))
  invisible(confusion)
}
