# Palo Alto Networks Workforce Attrition Intelligence

A production-ready Streamlit analytics platform for workforce attrition pattern analysis, predictive retention risk scoring, financial impact modeling, and HR action planning.

This project is built as a company-style HR leadership product for Palo Alto Networks workforce data. It converts employee records into executive KPIs, diagnostic analytics, machine-learning risk tiers, survival curves, scenario simulations, ROI estimates, and evidence-backed retention recommendations.

## Business Objective

Employee attrition affects delivery capacity, hiring cost, institutional knowledge, manager continuity, and workforce planning. This dashboard helps HR and business leaders answer:

- Which departments, job roles, and cohorts have the highest attrition exposure?
- Which demographic, tenure, workload, compensation, and satisfaction patterns are linked with exits?
- Which employee profiles show elevated predictive attrition risk?
- How does attrition translate into business cost?
- Which retention interventions should be prioritized first?
- How would risk change if employee profile factors were adjusted?

## Application Modules

| Module | Purpose |
|---|---|
| Overview | Workforce baseline, attrition KPIs, estimated annual cost, retention mix, department rates, benchmark context, and satisfaction gap interpretation |
| Department & Role | Department alerts, role hotspots, benchmark lines, role heatmaps, treemap, and department-to-role-to-outcome flow |
| Demographics | Age, gender, marital status, education, intersectional matrix, pay equity, and tenure by education |
| Tenure & Workload | Tenure buckets, overtime, travel, training gap, manager tenure, promotion bands, distance risk, and protective factors |
| Risk Score | Soft Voting Ensemble risk scoring, calibrated tiers, performance curves, feature importance, individual explainer, population contributions, and threshold sensitivity |
| Compensation | Income bands, salary hike, stock options, internal pay equity map, salary scatter, and stock option savings simulation |
| Executive Summary | Leadership briefing, benchmark comparison, priority actions, PDF report export, and navigation hub |
| Cohort Analysis | Custom two-dimensional cohort matrices, chi-square validation, Cramer's V effect size, tenure cohort trends, and CSV export |
| What-If Simulator | Interactive employee profile simulator with live attrition risk gauge, top drivers, interventions, and company-average comparison |
| Survival Analysis | Kaplan-Meier survival curves by department, overtime, and job level, plus hazard-rate spike detection |
| Retention ROI | Cost of attrition calculator, savings scenarios, program ROI, break-even recommendation, and department cost breakdown |
| Action Plan | Auto-generated P1/P2/P3 HR recommendations with evidence citations and CSV/PDF exports |

## Key Capabilities

- Multi-page Streamlit product with persistent sidebar and topbar navigation
- Global workforce filters with reset, department, role, tenure, overtime, travel, gender, education field, job level, and attrition-only filtering
- Plotly-based interactive charts with a professional executive theme
- Cached data loading, feature engineering, and model training
- Soft Voting Ensemble model using Gradient Boosting, Random Forest, and Logistic Regression
- Model performance diagnostics: ROC, Precision-Recall, calibration, confusion matrix, and threshold sensitivity
- Individual and population-level risk driver explainability
- Kaplan-Meier survival analysis and tenure hazard charts
- Cost of attrition and retention ROI calculators
- Auto-generated HR action plan with evidence citations
- CSV downloads and PDF report exports
- Statistical guardrails with chi-square tests, confidence intervals, and Cramer's V effect size

## Dataset

The application expects the dataset file in the project root:

```text
Palo_Alto_Networks.csv
```

Dataset profile:

- Records: 1,470 employees
- Columns: 31 source columns, expanded with engineered fields
- Target column: `Attrition`
- Target encoding: `1 = Left`, `0 = Stayed`
- Missing values: none
- Key domains: demographics, department, role, tenure, workload, compensation, satisfaction, performance, travel, and promotion history

The data loader creates business-ready fields such as:

- `Attrition_Label`
- `AgeGroup`
- `TenureBucket`
- `CareerStage`
- `IncomeBand`
- `DistanceBand`
- `PromotionBand`
- `ManagerTenureBand`
- `PerformanceLabel`
- `DeptRole`
- `SatisfactionIndex`
- `WorkloadStress`
- `TrainingGap`
- `LoyaltyScore`
- `RetentionRiskIndex`

## Project Structure

```text
app.py
pages/
  01_Overview.py
  02_Department_Role.py
  03_Demographics.py
  04_Tenure_Workload.py
  05_Risk_Score.py
  06_Compensation.py
  07_Executive_Summary.py
  08_Cohort_Analysis.py
  09_What_If_Simulator.py
  10_Survival_Analysis.py
  11_Retention_ROI.py
  12_Recommendations.py
utils/
  __init__.py
  charts.py
  config.py
  data_loader.py
  kpis.py
  ml.py
  theme.py
requirements.txt
pyproject.toml
Palo_Alto_Networks.csv
```

## Tech Stack

- Python 3.11+
- Streamlit
- Pandas
- NumPy
- Plotly
- scikit-learn
- SciPy
- lifelines
- fpdf2

## Setup

Create and activate a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run Locally

```bash
streamlit run app.py
```

Open the local app:

```text
http://localhost:8501
```

`app.py` redirects directly to the Overview module while preserving Streamlit's normal multi-page app behavior.

## Streamlit Cloud Deployment

Use these settings in Streamlit Community Cloud:

- Repository: your GitHub repository URL
- Branch: `main`
- Main file path: `app.py`
- Python dependencies: `requirements.txt`

Make sure `Palo_Alto_Networks.csv` is committed in the project root before deployment.

## Data Accuracy Controls

The project includes safeguards for reliable HR analytics:

- Defensive `Attrition` normalization to binary integer values
- Ordered `BusinessTravel` category handling
- Correct distance bands based on the dataset maximum
- Promotion-band analysis instead of misleading binary stagnation logic
- Performance labels restricted to observed rating values
- Workload-stress validation checks
- Bounded loyalty score and income-level ratio validation
- Chi-square small-sample warnings
- Wilson confidence intervals for selected rate charts
- Cramer's V effect size for cohort association strength
- Shared ML encoding for risk scoring and what-if simulation

## Model Summary

The Risk Score module uses a Soft Voting Ensemble to estimate attrition probability:

- Gradient Boosting Classifier
- Random Forest Classifier
- Logistic Regression with scaling

Model features include age, income, tenure, total experience, satisfaction scores, job level, overtime, business travel, promotion history, prior employers, distance from home, stock options, department, marital status, training, manager tenure, salary hike, hourly rate, and daily rate.

The model provides:

- Balanced class handling
- F1-optimized threshold
- Low, medium, and high risk tiers
- ROC, Precision-Recall, calibration, and confusion matrix diagnostics
- Feature importance and coefficient views
- Individual profile contribution analysis
- Population-level high-risk driver analysis

## Financial and Business Translation

The upgraded product includes business-facing modules beyond descriptive analytics:

- Estimated annual attrition cost
- Cost per exit calculation
- Department-level attrition cost breakdown
- Retention program ROI and break-even recommendation
- Stock option savings simulation
- Auto-generated HR action plan grouped by P1, P2, and P3 priorities
- Executive PDF report and action-plan export

## Usage Notes

- Keep `Palo_Alto_Networks.csv` in the same directory as `app.py`.
- Do not rename the files inside `pages/`; Streamlit uses the numeric prefixes for sidebar order.
- All charts are built with Plotly.
- Data loading uses `st.cache_data`.
- Model training uses `st.cache_resource`.
- Survival analysis requires `lifelines`.
- PDF export requires `fpdf2`.

## Intended Audience

This dashboard is built for:

- HR leadership
- People analytics teams
- Department heads
- Workforce planning teams
- Business stakeholders evaluating retention investment
- Academic or portfolio reviewers evaluating an enterprise analytics project
