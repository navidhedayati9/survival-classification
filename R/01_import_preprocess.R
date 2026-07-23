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

hospital_all_records <- readr::read_csv(
  raw_data_path,
  col_names = column_names,
  show_col_types = FALSE,
  progress = FALSE
)

if (ncol(hospital_all_records) != length(column_names)) {
  stop("Expected 21 columns but found ", ncol(hospital_all_records), ".", call. = FALSE)
}
if (anyNA(hospital_all_records)) {
  warning("The imported data contain ", sum(is.na(hospital_all_records)), " missing values.")
}

valid_codes <- list(SURVIVE = c(1, 3), Sex = c(1, 2), RECORD = c(1, 2))
for (variable in names(valid_codes)) {
  unexpected <- setdiff(unique(hospital_all_records[[variable]]), valid_codes[[variable]])
  if (length(unexpected) > 0L) {
    stop("Unexpected ", variable, " code(s): ", paste(unexpected, collapse = ", "), call. = FALSE)
  }
}

hospital_all_records <- hospital_all_records |>
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

if (anyNA(hospital_all_records$SHOCK_TYP)) {
  stop("Unexpected SHOCK_TYP code detected during factor conversion.", call. = FALSE)
}

# Audit the number of initial and final observations available for each patient.
record_counts <- hospital_all_records |>
  dplyr::count(ID, RECORD, name = "n_records") |>
  tidyr::complete(ID, RECORD, fill = list(n_records = 0L))

invalid_record_pairs <- record_counts |>
  dplyr::filter(n_records != 1L)
if (nrow(invalid_record_pairs) > 0L) {
  stop("Every patient must have exactly one Initial and one Final record.", call. = FALSE)
}

# The primary research question concerns information available at admission.
# Retain one Initial record per patient and remove the now-constant occasion field.
hospital <- hospital_all_records |>
  dplyr::filter(RECORD == "Initial") |>
  dplyr::select(-RECORD)

if (nrow(hospital) != dplyr::n_distinct(hospital$ID)) {
  stop("The admission dataset must contain exactly one row per patient.", call. = FALSE)
}

readr::write_csv(hospital, processed_data_path)
readr::write_csv(record_counts, file.path("results", "record_counts.csv"))
