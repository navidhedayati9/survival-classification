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
OUTPUT = REPORT_DIR / "Survival_Classification_Professional_Report.pdf"
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

    performance = pd.read_csv(ROOT / "results" / "model_performance.csv").sort_values("accuracy")
    canvas = PILImage.new("RGB", (1700, 900), "white")
    draw = ImageDraw.Draw(canvas)
    draw.text((850, 40), "Model performance on held-out patients", font=bold, fill="#222222", anchor="ma")
    x0, x1 = 500, 1520
    for tick in range(0, 101, 20):
        x = x0 + (x1-x0)*tick/100
        draw.line((x, 130, x, 760), fill="#E4E4E4", width=2)
        draw.text((x, 780), str(tick), font=small, fill="#444444", anchor="ma")
    for i, row in enumerate(performance.itertuples()):
        yy = 180 + i*145
        value = row.accuracy*100
        draw.text((x0-25, yy+35), row.model, font=font, fill="#222222", anchor="rm")
        draw.rectangle((x0, yy, x0+(x1-x0)*value/100, yy+70), fill="#377EB8")
        draw.text((x0+(x1-x0)*value/100+15, yy+35), f"{value:.1f}%", font=font, fill="#222222", anchor="lm")
    draw.text(((x0+x1)//2, 840), "Test accuracy (%)", font=font, fill="#222222", anchor="ma")
    canvas.save(REPORT_FIGURES / "model_performance.png")

    importance = pd.read_csv(ROOT / "results" / "random_forest_variable_importance.csv")
    importance = importance.nlargest(10, "MeanDecreaseAccuracy").sort_values("MeanDecreaseAccuracy")
    canvas = PILImage.new("RGB", (1700, 1100), "white")
    draw = ImageDraw.Draw(canvas)
    draw.text((850, 35), "Random forest variable importance", font=bold, fill="#222222", anchor="ma")
    x0, x1 = 430, 1510
    maximum = 40
    for tick in range(0, maximum+1, 10):
        x = x0 + (x1-x0)*tick/maximum
        draw.line((x, 115, x, 980), fill="#E4E4E4", width=2)
        draw.text((x, 995), str(tick), font=small, fill="#444444", anchor="ma")
    for i, row in enumerate(importance.itertuples()):
        yy = 135 + i*82
        value = row.MeanDecreaseAccuracy
        draw.text((x0-25, yy+25), row.variable, font=font, fill="#222222", anchor="rm")
        draw.rectangle((x0, yy, x0+(x1-x0)*value/maximum, yy+50), fill="#6A9A3B")
        draw.text((x0+(x1-x0)*value/maximum+12, yy+25), f"{value:.1f}", font=small, fill="#222222", anchor="lm")
    draw.text(((x0+x1)//2, 1055), "Mean decrease in accuracy", font=font, fill="#222222", anchor="ma")
    canvas.save(REPORT_FIGURES / "random_forest_importance.png")


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
    Paragraph("Statistical modeling and patient-level predictive evaluation", styles["Subtitle"]),
    Paragraph("Navid Hedayati", styles["Subtitle"]),
    Paragraph("July 21, 2026", styles["Subtitle"]),
    Spacer(1, 0.25 * inch),
    section("1", "Executive Summary"),
    p("These data were collected from 112 critically ill patients in Southern California. Two observations were recorded for each patient: an initial measurement at admission and a final measurement shortly before discharge or death. Each observation contains demographic information, shock type, physiological measurements, the measurement occasion, and the survival outcome. The objective of this report is to determine which available variables are associated with survival and to compare statistical and machine-learning methods for classifying patients as survived or died."),
    p("The validated data contain 224 complete observations from 112 patients, with one admission record and one final record for every patient. Because repeated observations from the same patient are statistically related, model evaluation is conducted at the patient level: both records from any patient are assigned to the same partition. Patient ID is retained only for data management and is excluded from modeling. This design evaluates whether a fitted model can generalize to patients who were not represented during training."),
    p("Separate logistic regressions identify systolic blood pressure, mean arterial pressure, diastolic blood pressure, mean central venous pressure, urinary output, height, sex, shock type, body surface index, cardiac index, appearance time, mean circulation time, hemoglobin, and hematocrit as associated with survival at the 5 percent level. Age, heart rate, plasma volume index, red cell index, and record occasion are not significant at that level. Strong correlations among blood-pressure measurements and between several other physiological measurements motivate a compact logistic formula containing systolic blood pressure, mean central venous pressure, urinary output, hemoglobin, shock type, and the interaction between systolic blood pressure and urinary output."),
    p("On the patient-level held-out test set, the classification tree achieves the highest accuracy, 76.1 percent, and the highest specificity, 95.8 percent. Random forest has the highest sensitivity for identifying patients who died, 63.6 percent. Logistic regression and bagging each achieve 69.6 percent accuracy. The results demonstrate an important tradeoff: the model that most reliably recognizes survivors is not the model that detects the greatest proportion of deaths. Because the dataset is small and the estimates come from a single holdout partition, differences among methods should be interpreted cautiously rather than as a definitive model ranking."),
    section("2", "Introduction"),
    p("How accurately can routinely collected physiological measurements distinguish patients who survived from those who died? Which measurements are most strongly associated with the outcome? These questions are important because a useful prediction method should identify patients at risk while remaining interpretable and reliable for patients not used to construct the model."),
    p("The response variable, <i>SURVIVE</i>, has two categories: Survived and Died. This report considers four classifiers: logistic regression, a pruned classification tree, bagging, and random forest. Logistic regression provides interpretable odds ratios. The classification tree provides a compact set of decision rules. Bagging and random forest combine many trees to obtain more flexible prediction functions."),
    p("The primary analysis has two goals. The inferential goal is to describe associations between the recorded predictors and the odds of death. The predictive goal is to compare how four classification methods perform on held-out patients. These goals are related but distinct: a variable can be statistically associated with the outcome without materially improving prediction, and a flexible prediction model can perform well without yielding a simple clinical interpretation."),
    p("The analysis is educational and retrospective. It is not a validated clinical decision-support system. Final measurements occur close to discharge or death and may contain information that would not be available at the time an early intervention decision must be made. Accordingly, the reported performance describes classification using the available dataset; it should not be interpreted as prospective admission-time performance."),
    PageBreak(),
    section("3", "Exploratory Data Analysis"),
    p("The dataset contains 21 variables and 224 complete records. There are 112 unique patients: 69 survived and 43 died. There are 58 male patients and 54 female patients. Among the male patients, 41 survived and 17 died; among the female patients, 28 survived and 26 died. Every patient has one initial and one final record. No missing values were detected after import, and the expected category codes and patient-record structure were validated before analysis."),
    make_table([
        ["Variable", "Mean", "Median", "St. Dev.", "Min", "Max"],
        ["SBP", "108.406", "108.5", "33.905", "26", "182"],
        ["DBP", "56.871", "58.5", "19.929", "10", "108"],
        ["UO", "66.375", "12.0", "125.460", "0", "850"],
        ["HG", "110.067", "108.0", "23.242", "59", "180"],
        ["MCVP", "86.821", "82.0", "54.088", "1", "319"],
        ["AGE", "54.625", "56.5", "16.634", "16", "90"],
        ["HT", "164.188", "165.0", "11.034", "70", "185"],
    ], [1.05*inch, .75*inch, .75*inch, .82*inch, .62*inch, .62*inch], aligns=["LEFT"] + ["RIGHT"]*5),
    Paragraph("Table 1: Summary statistics for selected quantitative variables.", styles["Caption"]),
    p("Survived records have substantially higher average systolic, diastolic, and mean arterial pressures than records from patients who died. Median urinary output is 42 among survived records and 1 among died records. Mean central venous pressure is higher among died records, while hemoglobin is modestly lower. These comparisons describe association rather than causation and do not account for the dependence between the two observations from each patient."),
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
    p("Separate univariate logistic regressions were fitted for each candidate predictor using all 224 observations. At the 5 percent level, systolic blood pressure, mean arterial pressure, diastolic blood pressure, mean central venous pressure, urinary output, body surface index, height, sex, shock type, cardiac index, appearance time, mean circulation time, hemoglobin, and hematocrit are associated with the outcome. Age is close to the threshold but does not meet it (p = 0.061). Heart rate, plasma volume index, red cell index, and record occasion are also not significant."),
    p("The blood-pressure variables are highly correlated, so only systolic pressure is retained in the final logistic model. Hematocrit is excluded in favor of hemoglobin. Appearance time is excluded in favor of mean circulation time, cardiac index is removed because of its relationship with mean circulation time, and body surface index is excluded because of its relationship with height. These choices reduce redundancy and improve coefficient stability. The final logistic specification contains systolic blood pressure, mean central venous pressure, urinary output, hemoglobin, shock type, and the systolic-pressure by urinary-output interaction."),
    subsection("4.1", "Model Selection"),
    p("To evaluate prediction without exposing a model to records belonging to a test patient, the 112 patient identifiers were sampled rather than the 224 individual rows. With random seed 4, 89 patients, representing 178 records, were assigned to training; 23 patients, representing 46 records, were held out for testing. Patient ID was removed from all predictor matrices."),
    p("The logistic regression used the prespecified compact formula. A classification tree was grown on all available predictors other than ID and pruned using the one-standard-error rule based on its cross-validation complexity table. Bagging and random forest models each used 1,500 trees. Random forest considered four predictors at each split. All four classifiers used the same patient-level training and testing partitions."),
    make_table([
        ["Predictor", "Odds ratio", "P-value", "95% confidence interval"],
        ["SBP", "0.952", "<0.001", "0.932 to 0.969"],
        ["MCVP", "1.018", "<0.001", "1.009 to 1.029"],
        ["UO", "0.950", "0.037", "0.901 to 0.993"],
        ["HG", "0.979", "0.055", "0.958 to 1.000"],
        ["Hypovolemic shock vs non-shock", "6.626", "0.018", "1.440 to 34.492"],
        ["Cardiogenic shock vs non-shock", "3.127", "0.152", "0.668 to 15.559"],
        ["Bacterial shock vs non-shock", "3.526", "0.150", "0.649 to 20.776"],
        ["Neurogenic shock vs non-shock", "5.969", "0.030", "1.246 to 32.339"],
        ["Other shock vs non-shock", "4.991", "0.086", "0.804 to 33.195"],
        ["SBP by UO interaction", "1.00035", "0.052", "0.99999 to 1.00073"],
    ], [2.45*inch, .85*inch, .72*inch, 1.55*inch], font_size=7.8, aligns=["LEFT", "RIGHT", "RIGHT", "CENTER"]),
    Paragraph("Table 3: Odds ratios from the training-set logistic regression.", styles["Caption"]),
    p("The wide confidence intervals for shock categories reflect the small numbers of patients in each group. Hemoglobin and the interaction term are slightly above the conventional 5 percent significance threshold in the training model. Consequently, their inclusion should be viewed as adherence to the prespecified model rather than proof of independent statistical significance."),
    figure(FIGURES / "classification_tree.png", 6.35*inch, "Figure 3: Pruned classification tree fitted on the training patients."),
    subsection("4.2", "Predictions"),
    p("Predicted probabilities from logistic regression were converted to Died when the estimated probability exceeded 0.5 and to Survived otherwise. The tree-based methods directly produced class labels. Death was treated as the positive class when sensitivity and specificity were calculated."),
    make_table([
        ["Method", "Accuracy", "Misclass.", "Sensitivity", "Specificity"],
        ["Classification tree", "76.1%", "23.9%", "54.5%", "95.8%"],
        ["Random forest", "71.7%", "28.3%", "63.6%", "79.2%"],
        ["Logistic regression", "69.6%", "30.4%", "50.0%", "87.5%"],
        ["Bagging", "69.6%", "30.4%", "54.5%", "83.3%"],
    ], [1.7*inch, .87*inch, .87*inch, .9*inch, .9*inch], aligns=["LEFT"]+["RIGHT"]*4),
    Paragraph("Table 4: Performance on held-out patients.", styles["Caption"]),
    p("The classification tree correctly classified 35 of 46 test records. Random forest correctly classified 33, while logistic regression and bagging each correctly classified 32. Random forest identified 14 of the 22 death records and therefore had the highest sensitivity. The classification tree correctly identified 23 of the 24 survived records and therefore had the highest specificity."),
    p("Accuracy alone does not fully characterize model performance. The test set contains 24 survived records and 22 death records, so class imbalance is limited, but the consequences of the two error types are not equivalent. False negatives for death represent high-risk observations classified as survived, while false positives for death represent survived observations classified as died. Model selection should therefore reflect the intended use and the relative cost of these errors, not only the overall percentage classified correctly."),
    figure(REPORT_FIGURES / "model_performance.png", 6.25*inch, "Figure 4: Accuracy on the common patient-level held-out test set."),
    subsection("4.3", "Inference"),
    p("Holding the other terms fixed, a one-unit increase in systolic pressure is associated with an estimated 4.8 percent decrease in the odds of death, subject to the interaction with urinary output. A one-unit increase in mean central venous pressure is associated with an estimated 1.8 percent increase in the odds of death. A one-unit increase in urinary output is associated with an estimated 5.0 percent decrease in the odds of death, again subject to the interaction term."),
    p("Compared with the non-shock category, estimated odds of death are substantially higher for several shock categories. The clearest training-set evidence is observed for hypovolemic and neurogenic shock. These estimates have wide intervals and should not be interpreted causally."),
    p("In the random forest, mean arterial pressure has the largest mean decrease in accuracy, followed by urinary output, diastolic pressure, mean central venous pressure, and systolic pressure. The concentration of importance among hemodynamic measurements suggests that circulatory status is central to classification in this dataset. Variable importance is conditional on the fitted model and the available predictors; correlated variables can divide or redistribute importance. It indicates predictive contribution, not clinical effect or causation."),
    PageBreak(),
    figure(REPORT_FIGURES / "random_forest_importance.png", 6.1*inch, "Figure 5: Random-forest variable importance."),
    section("5", "Discussion"),
    p("The findings consistently identify hemodynamic status as the dominant source of predictive information. Mean arterial pressure, systolic pressure, diastolic pressure, urinary output, and mean central venous pressure appear prominently in association tests or tree-based importance measures. This pattern is clinically plausible as a description of the dataset, but the observational design does not establish that changing any measurement would change survival."),
    p("The classification tree offers the simplest decision structure and the highest observed test accuracy. Its strong specificity means that it rarely labels a survived record as died, but its sensitivity of 54.5 percent means that it misses approximately 45 percent of death records. Random forest improves death sensitivity to 63.6 percent at the cost of more false-positive death classifications. Logistic regression remains valuable for interpretation, although its 50.0 percent sensitivity is the lowest of the four models on this partition."),
    p("The data include two time points per patient. This longitudinal structure is respected during train-test partitioning, but the fitted models treat the two records within training as separate observations. A formal longitudinal model or patient-level summary could account more directly for within-patient dependence. More importantly, a clinically deployable prediction question requires a clearly defined prediction time. If the intended decision occurs at admission, only admission-time variables should be used."),
    subsection("5.1", "Limitations"),
    p("The sample contains only 112 patients, which limits statistical power, produces wide confidence intervals, and makes performance sensitive to the particular train-test partition. Univariate screening and variable selection can be unstable in small samples. The current evaluation reports accuracy, sensitivity, and specificity but does not quantify uncertainty, calibration, receiver-operating-characteristic area, or precision-recall performance. No external cohort is available to evaluate transportability."),
    p("The dataset's age, collection protocol, measurement units, and population characteristics are incompletely documented. Final measurements may encode proximity to discharge or death, creating temporal information that would be unavailable for early prediction. For these reasons, the models should be considered exploratory and should not be used for clinical decisions."),
    section("6", "Conclusions"),
    p("Blood-pressure measurements, urinary output, mean central venous pressure, shock type, and several related physiological variables contain substantial information about survival status in this dataset. Higher systolic pressure and urinary output are associated with lower estimated odds of death, while higher mean central venous pressure and several shock categories are associated with higher estimated odds. Confidence intervals, particularly for shock categories, remain wide."),
    p("On held-out patients, the classification tree provides the highest observed accuracy and specificity, while random forest provides the highest sensitivity for death. No method dominates every metric. The appropriate method therefore depends on whether the priority is overall correctness, minimizing false alarms, detecting a larger proportion of deaths, or obtaining interpretable associations."),
    p("Future work should define an admission-time prediction target, restrict predictors accordingly, and use repeated grouped cross-validation or bootstrap validation by patient. Evaluation should include ROC-AUC, precision-recall curves, calibration plots, decision thresholds, and uncertainty intervals. Penalized logistic regression and externally validated models would provide useful next comparisons."),
    section("7", "References"),
    Paragraph("1. James, G., Witten, D., Hastie, T., and Tibshirani, R. <i>An Introduction to Statistical Learning: With Applications in R</i>. Springer.", styles["Reference"]),
    Paragraph("2. Breiman, L. (2001). Random Forests. <i>Machine Learning</i>, 45, 5-32.", styles["Reference"]),
    Paragraph("3. Survival Classification project. R analysis scripts, processed data, figures, and generated result tables, 2026.", styles["Reference"]),
    PageBreak(),
    section("", "Appendix"),
    make_table([
        ["Model", "S->S", "S->D", "D->S", "D->D"],
        ["Logistic regression", "21", "3", "11", "11"],
        ["Classification tree", "23", "1", "10", "12"],
        ["Bagging", "20", "4", "10", "12"],
        ["Random forest", "19", "5", "8", "14"],
    ], [1.85*inch, .75*inch, .75*inch, .75*inch, .75*inch], aligns=["LEFT"]+["RIGHT"]*4),
    Paragraph("Table 5: Confusion matrices on the common test set. S denotes Survived and D denotes Died; the term before the arrow is truth and the term after the arrow is the prediction.", styles["Caption"]),
    make_table([
        ["Rank", "Variable", "Mean decrease in accuracy"],
        ["1", "MAP", "36.23"], ["2", "UO", "29.11"], ["3", "DBP", "25.79"],
        ["4", "MCVP", "22.95"], ["5", "SBP", "22.46"], ["6", "SHOCK_TYP", "13.94"],
        ["7", "MCT", "13.30"], ["8", "HT", "13.01"],
    ], [.65*inch, 1.7*inch, 1.8*inch], aligns=["RIGHT", "LEFT", "RIGHT"]),
    Paragraph("Table 6: Leading random-forest variables.", styles["Caption"]),
    subsection("A.1", "Reproducibility Note"),
    p("The complete workflow can be rerun from the project root with <font name='Courier'>source(&quot;R/run_analysis.R&quot;)</font>. Generated numerical outputs are stored in <font name='Courier'>results/</font>, figures are stored in <font name='Courier'>figures/</font>, and the validated data are stored in <font name='Courier'>data/processed/processed_data.csv</font>. The fixed random seed is 4."),
]

doc.build(story, onFirstPage=footer, onLaterPages=footer)
print(OUTPUT)
