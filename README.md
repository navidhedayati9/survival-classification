# Survival Classification in Critically Ill Patients

This project examines whether routinely collected physiological measurements can distinguish patients who survived from those who died. It modernizes a statistical analysis originally completed in 2020 by organizing the code into a reproducible R workflow, correcting the raw-data import, and preventing patient-level leakage during model evaluation.

> **Important:** This is an educational portfolio project, not a validated clinical decision-support tool. Its results must not be used to guide patient care.

## Current report

**[View the current admission-only logistic-regression report](report/Survival_Classification_Report.pdf).**

This is the repository's single authoritative report. It uses only measurements available at admission and supersedes the earlier analysis that combined initial and final records. Older report versions are intentionally excluded from the current repository tree to avoid ambiguity; they remain available through the file's [Git history](https://github.com/navidhedayati9/survival-classification/commits/main/report/Survival_Classification_Report.pdf).

## Research questions

1. Which demographic and physiological variables are associated with patient survival?
2. How accurately can logistic regression distinguish survival outcomes?
3. Which predictors contribute most strongly to the fitted logistic model?
4. How should the fitted odds ratios be interpreted clinically and statistically?

## Data

The source dataset contains **224 observations from 112 critically ill patients**. Each patient has two records:

- `Initial`: measurements recorded on admission.
- `Final`: measurements recorded shortly before discharge or death.

The outcome, `SURVIVE`, has two classes: `Survived` and `Died`. The raw CSV intentionally has no header row; column names are assigned during import. The original 2020 analysis read the first observation as a header and therefore retained only 223 records. The revised workflow imports and validates all 224 records, then restricts the primary analysis to the **112 initial/admission records** so that no post-admission information enters the models.

### Data dictionary

| Variable | Type | Description |
|---|---|---|
| `ID` | Identifier | Patient identifier; connects the initial and final records for one patient |
| `AGE` | Numeric | Patient age in years |
| `HT` | Numeric | Patient height in centimeters |
| `Sex` | Categorical | Male or Female |
| `SURVIVE` | Binary outcome | Survived or Died |
| `SHOCK_TYP` | Categorical | Non-shock, hypovolemic, cardiogenic, bacterial, neurogenic, or other shock type |
| `SBP` | Numeric | Systolic blood pressure |
| `MAP` | Numeric | Mean arterial pressure |
| `HR` | Numeric | Heart rate |
| `DBP` | Numeric | Diastolic blood pressure |
| `MCVP` | Numeric | Mean central venous pressure |
| `BSI` | Numeric | Body surface index |
| `CI` | Numeric | Cardiac index |
| `AT` | Numeric | Appearance time |
| `MCT` | Numeric | Mean circulation time |
| `UO` | Numeric | Urinary output |
| `PVI` | Numeric | Plasma volume index |
| `RCI` | Numeric | Red cell index |
| `HG` | Numeric | Hemoglobin measurement |
| `HCT` | Numeric | Hematocrit measurement |
| `RECORD` | Categorical | Measurement occasion: Initial or Final |

Measurement units beyond those explicitly documented in the original report should be confirmed from the source data documentation before clinical interpretation.

## Methodology

The analysis proceeds in four stages:

1. **Import and validation**
   - Assign the 21 expected column names to the headerless CSV.
   - Verify the column count, category codes, and missing values.
   - Convert outcome and categorical predictors to labeled factors.
2. **Exploratory analysis**
   - Produce grouped descriptive statistics and box plots.
   - Examine correlations among quantitative predictors.
3. **Statistical modeling**
   - Restrict the analytical dataset to one initial record per patient.
   - Fit separate univariate logistic regressions for candidate predictors.
   - Fit a multivariable logistic regression using `SBP`, `MCVP`, `UO`, `HG`, `SHOCK_TYP`, and the `SBP:UO` interaction retained from the original methodology.
   - Report estimated odds ratios and confidence intervals.
4. **Evaluation**
   - Report accuracy, misclassification rate, sensitivity, and specificity on held-out patients.
   - Save the confusion matrix, odds ratios, and model summary as reproducible output files.

## Admission-time validation

The primary research question asks whether information available at admission can predict survival. Final measurements occur shortly before discharge or death and therefore contain future information that would not be available at the prediction time.

The revised analysis therefore:

- validates that every patient has one initial and one final source record;
- retains only the 112 initial records for modeling;
- samples unique patient IDs using a fixed seed (`set.seed(4)`);
- uses 89 patients (89 admission records) for training and 23 patients (23 admission records) for testing;
- excludes `ID` and the now-constant `RECORD` field from the predictor set.

This design estimates admission-time performance without temporal or patient-level leakage, although repeated stratified resampling would provide a more stable estimate than one holdout split.

## Findings

Performance on the patient-level held-out test set was:

| Model | Accuracy | Sensitivity | Specificity |
|---|---:|---:|---:|
| Logistic regression | 73.9% | 63.6% | 83.3% |

Logistic regression correctly classified 17 of the 23 held-out patients: 10 of 12 survivors and 7 of 11 patients who died. Because the test set is small, these values should be treated as a preliminary internal estimate rather than definitive clinical performance.

### Interpreting odds ratios

Logistic regression models the odds of the positive outcome, which is `Died` in this project. Exponentiating a regression coefficient produces an odds ratio:

- An odds ratio of `1` means no estimated change in the odds of death.
- An odds ratio below `1` means higher predictor values are associated with lower odds of death.
- An odds ratio above `1` means higher predictor values are associated with higher odds of death.

For a continuous predictor, the odds ratio applies to a one-unit increase while holding the other model terms constant. For example, the SBP odds ratio of approximately `0.972` corresponds to about a 2.8% decrease in the estimated odds of death per one-unit increase in SBP, subject to the `SBP:UO` interaction. For a categorical predictor, the odds ratio compares one category with the stated reference category. For example, shock-type odds ratios compare each shock category with `Non-shock`.

Odds and probabilities are not the same. A 2.8% change in odds is not necessarily a 2.8 percentage-point change in probability; the probability change depends on the patient's starting risk and other predictor values. Confidence intervals describe estimation uncertainty. Intervals containing `1` indicate that the data do not establish an odds-ratio difference from 1 at the corresponding confidence level.

The `SBP:UO` interaction means that the SBP association depends on urinary output and the urinary-output association depends on SBP. Consequently, the SBP and UO main-effect odds ratios should not be interpreted as constant effects across all values of the other variable.

The sample is small, so these values should be treated as estimates from one split rather than definitive evidence of clinical performance.

## Repository structure

```text
survival-classification/
├── data/
│   ├── raw/                         # Original source data
│   └── processed/                   # Validated, labeled analysis data
├── R/
│   ├── 00_setup.R                   # Dependencies, folders, helper functions
│   ├── 01_import_preprocess.R       # Import, validation, factor conversion
│   ├── 02_exploratory_analysis.R    # Summaries, plots, correlations
│   ├── 03_logistic_regression.R     # Split, univariate and final logistic models
│   ├── 06_model_evaluation.R        # Held-out logistic-regression metrics
│   └── run_analysis.R               # Complete execution pipeline
├── figures/                         # Generated visualizations
├── results/                         # Generated tables and metrics
├── report/                          # Current report, builder, and report figures
├── README.md
└── survival-classification.Rproj
```

## Reproducing the analysis

### Requirements

- A current version of R
- RStudio is optional but recommended
- The following R packages:

```r
install.packages(c(
  "broom",
  "corrplot",
  "dplyr",
  "ggplot2",
  "purrr",
  "readr",
  "tibble",
  "tidyr"
))
```

### Instructions

1. Clone the repository.
2. Open `survival-classification.Rproj`, or set the repository root as the working directory.
3. Confirm that the source file exists at `data/raw/DATA-FILEsp2020.csv`.
4. Run the complete workflow:

```r
source("R/run_analysis.R")
```

The pipeline recreates `data/processed/processed_data.csv` and writes analysis artifacts to `figures/` and `results/`. It stops with an informative message if required packages or source data are missing.

For exact package-version reproducibility, a future improvement is to initialize [`renv`](https://rstudio.github.io/renv/) and commit its lockfile.

## Limitations

- **Small sample:** The dataset contains only 112 patients, limiting precision and model complexity.
- **Single holdout split:** Results may vary with a different patient partition. Grouped repeated cross-validation or bootstrap validation is preferable.
- **Admission-only scope:** The primary analysis excludes final measurements to prevent temporal leakage; those records may be used separately for longitudinal or change analyses.
- **No external validation:** Performance has not been tested on patients from another hospital, region, or time period.
- **Historical data and limited provenance:** The age, collection protocol, population characteristics, and complete measurement units require further documentation.
- **Feature-selection uncertainty:** Univariate significance and correlation-based screening can be unstable in small samples and do not guarantee optimal predictive performance.
- **Class-specific performance:** Sensitivity for patients who died remains modest; accuracy alone is not sufficient for a clinically consequential task.
- **No causal interpretation:** Odds ratios describe adjusted associations and do not establish that a predictor causes survival or death.

## Next steps

- Use repeated grouped cross-validation by patient.
- Add ROC-AUC, precision-recall, calibration, and uncertainty estimates.
- Compare penalized logistic regression with the current model.
- Create a Quarto report that distinguishes the original 2020 analysis from the corrected workflow.
- Add an `renv.lock` file and fuller dataset provenance documentation.

## Author

Navid Hedayati
