# Run the complete analysis from the repository root ----------------------

scripts <- c(
  "00_setup.R",
  "01_import_preprocess.R",
  "02_exploratory_analysis.R",
  "03_logistic_regression.R",
  "04_classification_tree.R",
  "05_ensemble_models.R",
  "06_model_evaluation.R"
)

for (script in scripts) {
  message("Running R/", script)
  source(file.path("R", script), echo = FALSE)
}

message("Analysis complete. See figures/ and results/ for generated outputs.")
