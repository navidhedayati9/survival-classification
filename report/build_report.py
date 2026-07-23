from pathlib import Path

import pandas as pd
from PIL import Image as PILImage, ImageDraw, ImageFont
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "report"
FIGURES = ROOT / "figures"
OUTPUT = REPORT_DIR / "Survival_Classification_Report.pdf"
REPORT_FIGURES = REPORT_DIR / "figures"


def prepare_report_figures():
    REPORT_FIGURES.mkdir(exist_ok=True)
    data = pd.read_csv(ROOT / "data" / "processed" / "processed_data.csv")
    font_path = "/System/Library/Fonts/Supplemental/Arial.ttf"
    bold_path = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
    font = ImageFont.truetype(font_path, 28)
    small = ImageFont.truetype(font_path, 23)
    bold = ImageFont.truetype(bold_path, 36)
    title_font = ImageFont.truetype(bold_path, 28)
    palette = {"Survived": "#20B8B8", "Died": "#F06F68"}

    canvas = PILImage.new("RGB", (1700, 1200), "white")
    draw = ImageDraw.Draw(canvas)
    draw.text((850, 30), "Clinical measures by survival outcome", font=bold, fill="#222222", anchor="ma")
    specs = [("SBP", "Systolic pressure"), ("UO", "Urinary output"),
             ("HG", "Hemoglobin"), ("MCVP", "Mean central venous pressure")]
    for index, (variable, label) in enumerate(specs):
        col, row = index % 2, index // 2
        left, top = 95 + col * 820, 120 + row * 520
        right, bottom = left + 710, top + 410
        values = data[variable]
        ymin, ymax = float(values.min()), float(values.max())
        span = max(ymax - ymin, 1)
        ymin -= span * .05; ymax += span * .05
        y = lambda v: bottom - (float(v) - ymin) / (ymax - ymin) * (bottom - top)
        draw.line((left, top, left, bottom), fill="#555555", width=3)
        draw.line((left, bottom, right, bottom), fill="#555555", width=3)
        draw.text(((left + right)//2, top - 48), label, font=title_font, fill="#222222", anchor="ma")
        for t in range(5):
            val = ymin + t * (ymax-ymin)/4
            yy = y(val)
            draw.line((left, yy, right, yy), fill="#E5E5E5", width=2)
            draw.text((left-12, yy), f"{val:.0f}", font=small, fill="#444444", anchor="rm")
        for j, outcome in enumerate(["Survived", "Died"]):
            series = data.loc[data["SURVIVE"] == outcome, variable]
            q1, med, q3 = series.quantile([.25, .5, .75])
            low, high = series.min(), series.max()
            x = left + 235 + j * 270
            draw.line((x, y(low), x, y(high)), fill="#444444", width=3)
            draw.line((x-35, y(low), x+35, y(low)), fill="#444444", width=3)
            draw.line((x-35, y(high), x+35, y(high)), fill="#444444", width=3)
            draw.rectangle((x-70, y(q3), x+70, y(q1)), fill=palette[outcome], outline="#444444", width=3)
            draw.line((x-70, y(med), x+70, y(med)), fill="#222222", width=4)
            draw.text((x, bottom+18), outcome, font=small, fill="#333333", anchor="ma")
    canvas.save(REPORT_FIGURES / "clinical_measures.png")

prepare_report_figures()


styles = getSampleStyleSheet()
styles.add(ParagraphStyle(
    name="PaperTitle", parent=styles["Title"], fontName="Times-Bold",
    fontSize=18, leading=22, alignment=TA_CENTER, spaceAfter=12,
))
styles.add(ParagraphStyle(
    name="Subtitle", parent=styles["Normal"], fontName="Times-Roman",
    fontSize=11, leading=14, alignment=TA_CENTER, spaceAfter=5,
))
styles.add(ParagraphStyle(
    name="Section", parent=styles["Heading1"], fontName="Times-Bold",
    fontSize=13, leading=16, spaceBefore=12, spaceAfter=7, keepWithNext=True,
))
styles.add(ParagraphStyle(
    name="Subsection", parent=styles["Heading2"], fontName="Times-Bold",
    fontSize=11.5, leading=14, spaceBefore=10, spaceAfter=6, keepWithNext=True,
))
styles.add(ParagraphStyle(
    name="BodyPaper", parent=styles["BodyText"], fontName="Times-Roman",
    fontSize=10, leading=13.2, alignment=TA_JUSTIFY, spaceAfter=7,
))
styles.add(ParagraphStyle(
    name="Caption", parent=styles["BodyText"], fontName="Times-Roman",
    fontSize=8.5, leading=10.5, alignment=TA_CENTER, spaceBefore=4, spaceAfter=8,
))
styles.add(ParagraphStyle(
    name="Reference", parent=styles["BodyText"], fontName="Times-Roman",
    fontSize=9.5, leading=12, leftIndent=14, firstLineIndent=-14, spaceAfter=5,
))


def p(text):
    return Paragraph(text, styles["BodyPaper"])


def section(number, title):
    return Paragraph(f"{number} {title}", styles["Section"])


def subsection(number, title):
    return Paragraph(f"{number} {title}", styles["Subsection"])


def make_table(data, widths, font_size=8.2, aligns=None):
    table = Table(data, colWidths=widths, repeatRows=1, hAlign="CENTER")
    commands = [
        ("FONTNAME", (0, 0), (-1, 0), "Times-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Times-Roman"),
        ("FONTSIZE", (0, 0), (-1, -1), font_size),
        ("LEADING", (0, 0), (-1, -1), font_size + 2),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E9EDF2")),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#777777")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    if aligns:
        for col, align in enumerate(aligns):
            commands.append(("ALIGN", (col, 1), (col, -1), align))
    table.setStyle(TableStyle(commands))
    return table


def figure(path, width, caption):
    with PILImage.open(path) as source:
        pixel_width, pixel_height = source.size
    img = Image(str(path), width=width, height=width * pixel_height / pixel_width)
    img.hAlign = "CENTER"
    return KeepTogether([img, Paragraph(caption, styles["Caption"])])


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Times-Roman", 8)
    canvas.setFillColor(colors.HexColor("#555555"))
    canvas.drawCentredString(letter[0] / 2, 0.42 * inch, str(doc.page))
    canvas.restoreState()


doc = SimpleDocTemplate(
    str(OUTPUT), pagesize=letter,
    rightMargin=0.72 * inch, leftMargin=0.72 * inch,
    topMargin=0.66 * inch, bottomMargin=0.65 * inch,
    title="Survival Classification in Critically Ill Patients",
    author="Navid Hedayati",
    subject="Professional statistical and predictive analysis of survival classification",
)

story = [
    Spacer(1, 0.35 * inch),
    Paragraph("Survival Classification in Critically Ill Patients", styles["PaperTitle"]),
    Paragraph("Admission-time statistical modeling and predictive evaluation", styles["Subtitle"]),
    Paragraph("Navid Hedayati", styles["Subtitle"]),
    Paragraph("July 23, 2026", styles["Subtitle"]),
    Spacer(1, 0.25 * inch),
    section("1", "Executive Summary"),
    p("These data were collected from 112 critically ill patients in Southern California. Each patient has an initial measurement at admission and a final measurement shortly before discharge or death. Because the research question concerns admission-time prediction, the primary analysis uses only the initial record. The objective is to determine which admission variables are associated with survival, quantify those associations with odds ratios, and evaluate a logistic-regression model for predicting whether patients survived or died."),
    p("The source data contain 224 complete observations. The import process validates one initial and one final record for every patient, after which the analytical dataset is restricted to 112 admission records. Patient ID is retained only for data management and excluded from modeling. With one row per patient and no final measurements, the design avoids within-patient duplication and temporal leakage."),
    p("Separate admission-record logistic regressions identify systolic blood pressure, mean arterial pressure, diastolic blood pressure, mean central venous pressure, urinary output, sex, shock type, and body surface index as associated with survival at the 5 percent level. The compact logistic formula contains systolic blood pressure, mean central venous pressure, urinary output, hemoglobin, shock type, and the interaction between systolic blood pressure and urinary output."),
    p("On the 23-patient held-out test set, logistic regression achieves 73.9 percent accuracy, identifies 63.6 percent of deaths, and correctly identifies 83.3 percent of survivors. Because the dataset is small and the estimates come from one holdout partition, these values should be interpreted cautiously."),
    section("2", "Introduction"),
    p("How accurately can routinely collected physiological measurements distinguish patients who survived from those who died? Which measurements are most strongly associated with the outcome? These questions are important because a useful prediction method should identify patients at risk while remaining interpretable and reliable for patients not used to construct the model."),
    p("The response variable, <i>SURVIVE</i>, has two categories: Survived and Died. Logistic regression is used because it supports both admission-time classification and interpretable estimates of adjusted association. The model treats Died as the positive outcome."),
    p("The primary analysis has two goals. The inferential goal is to describe how admission predictors are associated with the odds of death. The predictive goal is to evaluate how the fitted logistic regression performs on held-out patients. These goals are related but distinct: a statistically significant association does not guarantee useful prediction, and predictive performance does not establish that a predictor causes the outcome."),
    p("The analysis is educational and retrospective. It is not a validated clinical decision-support system. The reported performance uses admission records only, but it remains an internal estimate from a small historical dataset and should not be interpreted as prospective clinical validation."),
    PageBreak(),
    section("3", "Exploratory Data Analysis"),
    p("The source dataset contains 21 variables and 224 complete records. The admission-only analytical dataset contains one record for each of 112 patients: 69 survived and 43 died. There are 58 male patients and 54 female patients. Among the male patients, 41 survived and 17 died; among the female patients, 28 survived and 26 died. No missing values were detected, and the expected category codes and paired source-record structure were validated before filtering."),
    make_table([
        ["Variable", "Mean", "Median", "St. Dev.", "Min", "Max"],
        ["SBP", "106.482", "104.5", "30.719", "26", "171"],
        ["DBP", "58.607", "59.0", "18.606", "10", "108"],
        ["UO", "54.911", "1.0", "112.739", "0", "510"],
        ["HG", "114.786", "112.0", "25.100", "66", "180"],
        ["MCVP", "88.321", "80.0", "56.860", "2", "302"],
        ["AGE", "54.625", "56.5", "16.671", "16", "90"],
        ["HT", "163.741", "165.0", "12.724", "70", "185"],
    ], [1.05*inch, .75*inch, .75*inch, .82*inch, .62*inch, .62*inch], aligns=["LEFT"] + ["RIGHT"]*5),
    Paragraph("Table 1: Summary statistics for selected quantitative variables.", styles["Caption"]),
    p("At admission, survivors have substantially higher average systolic, diastolic, and mean arterial pressures than patients who died. Median urinary output is 12 among survivors and 0 among patients who died. Mean central venous pressure is higher among patients who died, while hemoglobin is modestly lower. These patient-level comparisons describe association rather than causation."),
    make_table([
        ["Shock type", "Survived", "Died"],
        ["Non-shock", "31", "3"], ["Hypovolemic shock", "7", "10"],
        ["Cardiogenic shock", "10", "10"], ["Bacterial shock", "9", "6"],
        ["Neurogenic shock", "9", "7"], ["Other", "3", "7"],
    ], [2.25*inch, 1.0*inch, 1.0*inch], aligns=["LEFT", "RIGHT", "RIGHT"]),
    Paragraph("Table 2: Survival by shock type at the patient level.", styles["Caption"]),
    p("Non-shock patients have the largest number of survivors. Hypovolemic and cardiogenic shock have the largest numbers of deaths. The box plots in Figure 1 show clear separation between outcome groups for several clinical measurements, especially blood pressure and urinary output."),
    PageBreak(),
    figure(REPORT_FIGURES / "clinical_measures.png", 6.35*inch, "Figure 1: Selected clinical measurements by survival outcome."),
    p("The correlation plot in Figure 2 shows that systolic, mean arterial, and diastolic pressure are strongly correlated. Hemoglobin and hematocrit are also strongly correlated, as are appearance time and mean circulation time. These relationships inform the more compact logistic-regression specification."),
    PageBreak(),
    figure(FIGURES / "predictor_correlations.png", 5.9*inch, "Figure 2: Correlations among quantitative predictors."),
    section("4", "Statistical Analyses"),
    p("Separate univariate logistic regressions were fitted using the 112 admission records. At the 5 percent level, systolic blood pressure, mean arterial pressure, diastolic blood pressure, mean central venous pressure, urinary output, body surface index, sex, and shock type are associated with the outcome. The other admission predictors do not meet the 5 percent threshold."),
    p("The blood-pressure variables are highly correlated, so only systolic pressure is retained in the final logistic model. Hematocrit is excluded in favor of hemoglobin. Appearance time is excluded in favor of mean circulation time, cardiac index is removed because of its relationship with mean circulation time, and body surface index is excluded because of its relationship with height. These choices reduce redundancy and improve coefficient stability. The final logistic specification contains systolic blood pressure, mean central venous pressure, urinary output, hemoglobin, shock type, and the systolic-pressure by urinary-output interaction."),
    subsection("4.1", "Model Selection"),
    p("With random seed 4, 89 patients and their admission records were assigned to training; the remaining 23 patients and admission records were held out for testing. Patient ID was removed from all predictor matrices."),
    p("The logistic regression used the prespecified compact formula and a 0.5 probability threshold. The model was fitted on 89 admission records and evaluated once on the 23 held-out admission records."),
    PageBreak(),
    make_table([
        ["Predictor", "Odds ratio", "P-value", "95% confidence interval"],
        ["SBP", "0.972", "0.018", "0.948 to 0.994"],
        ["MCVP", "1.017", "0.006", "1.006 to 1.031"],
        ["UO", "0.971", "0.164", "0.927 to 1.009"],
        ["HG", "0.984", "0.210", "0.959 to 1.008"],
        ["Hypovolemic shock vs non-shock", "8.941", "0.029", "1.369 to 76.299"],
        ["Cardiogenic shock vs non-shock", "5.730", "0.098", "0.770 to 51.911"],
        ["Bacterial shock vs non-shock", "5.732", "0.094", "0.787 to 51.423"],
        ["Neurogenic shock vs non-shock", "7.648", "0.057", "1.014 to 72.562"],
        ["Other shock vs non-shock", "11.511", "0.033", "1.309 to 128.369"],
        ["SBP by UO interaction", "1.00022", "0.181", "0.99988 to 1.00056"],
    ], [2.45*inch, .85*inch, .72*inch, 1.55*inch], font_size=7.8, aligns=["LEFT", "RIGHT", "RIGHT", "CENTER"]),
    Paragraph("Table 3: Odds ratios from the training-set logistic regression.", styles["Caption"]),
    subsection("4.2", "Understanding Odds Ratios"),
    p("Logistic regression models log odds. Odds are the probability of death divided by the probability of survival: <i>odds = p/(1-p)</i>. An odds of 1 corresponds to a 50 percent probability, odds below 1 correspond to probabilities below 50 percent, and odds above 1 correspond to probabilities above 50 percent. Exponentiating a fitted regression coefficient gives an odds ratio, which compares the estimated odds after a predictor changes with the odds before that change."),
    p("An odds ratio equal to 1 indicates no estimated change in odds. An odds ratio below 1 indicates lower estimated odds of death as the predictor increases, while an odds ratio above 1 indicates higher estimated odds. The percentage change in odds is calculated as <i>(OR - 1) x 100</i> percent when OR is above 1, or <i>(1 - OR) x 100</i> percent as a decrease when OR is below 1."),
    p("For a continuous predictor, the reported odds ratio corresponds to a one-unit increase while all other model terms are held fixed. Because SBP participates in an interaction, its tabled odds ratio of 0.972 applies specifically when UO equals zero. At UO equal to zero, a one-unit increase in systolic pressure corresponds to approximately 2.8 percent lower estimated odds of death. A ten-unit comparison is obtained by raising 0.972 to the tenth power, giving approximately 0.76, or about 24 percent lower odds at that UO value."),
    p("For a categorical predictor, the odds ratio compares a category with its reference category. Non-shock is the reference for shock type. The hypovolemic-shock odds ratio of 8.94 means that, for patients with otherwise equal modeled predictors, the estimated odds of death are about 8.9 times those for the non-shock group. This estimate is imprecise: its confidence interval extends from approximately 1.37 to 76.30 because the category contains few patients."),
    p("Odds ratios are not risk ratios and are not percentage-point changes in probability. For example, doubling odds from 0.25 to 0.50 changes probability from 20 percent to 33 percent, not from 20 percent to 40 percent. The probability implication of an odds ratio depends on the patient's starting probability and the other predictors in the model."),
    p("The 95 percent confidence interval describes uncertainty in the estimated odds ratio. An interval containing 1 is compatible with no adjusted association at the 5 percent significance level. Wide intervals indicate limited precision. The p-value addresses evidence against a zero coefficient; it does not measure clinical importance, predictive usefulness, or the probability that the model is correct."),
    p("The SBP-by-UO interaction requires special care. It means the SBP association changes with urinary output and the urinary-output association changes with SBP. Consequently, the SBP odds ratio in Table 3 is the SBP association when UO equals zero, and the UO odds ratio is the UO association when SBP equals zero. Neither main-effect odds ratio is a constant effect across all patients. Using the fitted coefficients, the conditional one-unit SBP odds ratio is approximately 0.972 at UO 0, 0.983 at UO 50, and 0.994 at UO 100. These examples illustrate how the estimated SBP association becomes weaker as UO increases; they do not establish a biological mechanism."),
    p("Finally, all odds ratios are conditional associations from an observational dataset. Holding modeled variables constant does not eliminate unmeasured confounding, and an association does not establish that changing a predictor would change survival."),
    p("The wide confidence intervals for shock categories reflect the small numbers of patients in each group. Urinary output, hemoglobin, and the interaction term do not meet the conventional 5 percent significance threshold in the training model. Their inclusion follows the prespecified compact formula rather than establishing independent significance."),
    subsection("4.3", "Predictions"),
    p("Predicted probabilities from logistic regression were converted to Died when the estimated probability exceeded 0.5 and to Survived otherwise. Death was treated as the positive class when sensitivity and specificity were calculated."),
    make_table([
        ["Method", "Accuracy", "Misclass.", "Sensitivity", "Specificity"],
        ["Logistic regression", "73.9%", "26.1%", "63.6%", "83.3%"],
    ], [1.7*inch, .87*inch, .87*inch, .9*inch, .9*inch], aligns=["LEFT"]+["RIGHT"]*4),
    Paragraph("Table 4: Performance on held-out patients.", styles["Caption"]),
    p("Logistic regression correctly classified 17 of 23 test patients, including 7 of 11 deaths and 10 of 12 survivors."),
    p("Accuracy alone does not fully characterize model performance. The test set contains 12 survivors and 11 patients who died, so class imbalance is limited, but the consequences of the two error types are not equivalent. False negatives for death represent high-risk patients classified as survived, while false positives represent survivors classified as died."),
    subsection("4.4", "Inference"),
    p("Holding the other terms fixed, a one-unit increase in systolic pressure is associated with an estimated 2.8 percent decrease in the odds of death, subject to the interaction with urinary output. A one-unit increase in mean central venous pressure is associated with an estimated 1.7 percent increase in the odds of death. The urinary-output main effect does not reach the 5 percent significance threshold in this training model."),
    p("Compared with the non-shock category, estimated odds of death are substantially higher for several shock categories. The clearest training-set evidence by the reported Wald p-values is observed for hypovolemic shock and the Other category. These estimates have wide intervals and should not be interpreted causally. Small differences between confidence-interval and p-value conclusions can occur because the report uses profile-likelihood confidence intervals and Wald p-values."),
    section("5", "Discussion"),
    p("The findings consistently identify hemodynamic status as an important source of admission-time information. Higher systolic pressure is associated with lower estimated odds of death, while higher mean central venous pressure is associated with higher estimated odds. Several shock categories also have substantially elevated estimated odds relative to non-shock patients. This pattern is clinically plausible as a description of the dataset, but it is not evidence of causation."),
    p("The logistic regression correctly classifies 73.9 percent of held-out patients, but it misses 4 of the 11 deaths. Its coefficient estimates and odds ratios provide interpretability that accuracy alone cannot supply. At the same time, wide shock-type intervals and the interaction term demonstrate why individual coefficients must be interpreted with uncertainty and in the context of the full model."),
    p("The source data include two time points per patient, but the primary analysis deliberately uses admission records only. Final records remain available for a separate longitudinal or change-score analysis and must not be introduced into admission-time prediction."),
    subsection("5.1", "Limitations"),
    p("The sample contains only 112 patients, which limits statistical power, produces wide confidence intervals, and makes performance sensitive to the particular train-test partition. Univariate screening and variable selection can be unstable in small samples. The current evaluation reports accuracy, sensitivity, and specificity but does not quantify uncertainty, calibration, receiver-operating-characteristic area, or precision-recall performance. No external cohort is available to evaluate transportability."),
    p("The dataset's age, collection protocol, measurement units, and population characteristics are incompletely documented. Although temporal leakage has been removed from the primary analysis, these limitations mean the models remain exploratory and should not be used for clinical decisions."),
    section("6", "Conclusions"),
    p("Blood-pressure measurements, urinary output, mean central venous pressure, shock type, and several related physiological variables contain substantial information about survival status in this dataset. Higher systolic pressure and urinary output are associated with lower estimated odds of death, while higher mean central venous pressure and several shock categories are associated with higher estimated odds. Confidence intervals, particularly for shock categories, remain wide."),
    p("On held-out patients, logistic regression achieves 73.9 percent accuracy, 63.6 percent sensitivity for death, and 83.3 percent specificity. These estimates are provisional because they are based on only 23 test patients."),
    p("Future work should use repeated stratified cross-validation or bootstrap validation. Evaluation should include ROC-AUC, precision-recall curves, calibration plots, decision thresholds, and uncertainty intervals. Penalized logistic regression and external validation would provide useful next comparisons."),
    section("7", "References"),
    Paragraph("1. James, G., Witten, D., Hastie, T., and Tibshirani, R. <i>An Introduction to Statistical Learning: With Applications in R</i>. Springer.", styles["Reference"]),
    Paragraph("2. Survival Classification project. R analysis scripts, processed data, figures, and generated result tables, 2026.", styles["Reference"]),
    PageBreak(),
    section("", "Appendix"),
    make_table([
        ["Model", "S->S", "S->D", "D->S", "D->D"],
        ["Logistic regression", "10", "2", "4", "7"],
    ], [1.85*inch, .75*inch, .75*inch, .75*inch, .75*inch], aligns=["LEFT"]+["RIGHT"]*4),
    Paragraph("Table 5: Logistic-regression confusion matrix on the test set. S denotes Survived and D denotes Died; the term before the arrow is truth and the term after the arrow is the prediction.", styles["Caption"]),
    subsection("A.1", "Reproducibility Note"),
    p("The complete workflow can be rerun from the project root with <font name='Courier'>source(&quot;R/run_analysis.R&quot;)</font>. Generated numerical outputs are stored in <font name='Courier'>results/</font>, figures are stored in <font name='Courier'>figures/</font>, and the validated data are stored in <font name='Courier'>data/processed/processed_data.csv</font>. The fixed random seed is 4."),
]

doc.build(story, onFirstPage=footer, onLaterPages=footer)
print(OUTPUT)
