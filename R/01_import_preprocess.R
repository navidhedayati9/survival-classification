# Import and preprocess ---------------------------------------------------

raw_data_path <- file.path("data", "raw", "DATA-FILEsp2020.csv")
processed_data_path <- file.path("data", "processed", "processed_data.csv")

if (!file.exists(raw_data_path)) {
  stop("Raw data not found at ", raw_data_path, call. = FALSE)
}

column_names <- c(
  "ID", "AGE", "HT", "Sex", "SURVIVE", "SHOCK_TYP", "SBP", "MAP",
  "HR", "DBP", "MCVP", "BSI", "CI", "AT", "MCT", "UO", "PVI",
  "RCI", "HG", "HCT", "RECORD"
)

hospital <- readr::read_csv(
  raw_data_path,
  col_names = column_names,
  show_col_types = FALSE,
  progress = FALSE
)

if (ncol(hospital) != length(column_names)) {
  stop("Expected 21 columns but found ", ncol(hospital), ".", call. = FALSE)
}
if (anyNA(hospital)) {
  warning("The imported data contain ", sum(is.na(hospital)), " missing values.")
}

valid_codes <- list(SURVIVE = c(1, 3), Sex = c(1, 2), RECORD = c(1, 2))
for (variable in names(valid_codes)) {
  unexpected <- setdiff(unique(hospital[[variable]]), valid_codes[[variable]])
  if (length(unexpected) > 0L) {
    stop("Unexpected ", variable, " code(s): ", paste(unexpected, collapse = ", "), call. = FALSE)
  }
}

hospital <- hospital |>
  dplyr::mutate(
    ID = as.character(ID),
    SURVIVE = factor(SURVIVE, levels = c(1, 3), labels = c("Survived", "Died")),
    Sex = factor(Sex, levels = c(1, 2), labels = c("Male", "Female")),
    SHOCK_TYP = factor(
      SHOCK_TYP,
      levels = 2:7,
      labels = c(
        "Non-shock", "Hypovolemic-shock", "Cardiogenic-shock",
        "Bacterial-shock", "Neurogenic-shock", "Other"
      )
    ),
    RECORD = factor(RECORD, levels = c(1, 2), labels = c("Initial", "Final"))
  )

if (anyNA(hospital$SHOCK_TYP)) {
  stop("Unexpected SHOCK_TYP code detected during factor conversion.", call. = FALSE)
}

# Audit the number of initial and final observations available for each patient.
record_counts <- hospital |>
  dplyr::count(ID, RECORD, name = "n_records") |>
  tidyr::complete(ID, RECORD, fill = list(n_records = 0L))

readr::write_csv(hospital, processed_data_path)
readr::write_csv(record_counts, file.path("results", "record_counts.csv"))
