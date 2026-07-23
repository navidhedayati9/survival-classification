# Logistic-regression evaluation -----------------------------------------

model_metrics <- logistic_metrics
readr::write_csv(model_metrics, file.path("results", "model_performance.csv"))
