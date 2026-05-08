# Palo Alto Networks Workforce Attrition Intelligence

A production-ready Streamlit analytics platform for identifying workforce attrition patterns, retention risk hotspots, and employee-experience signals across Palo Alto Networks workforce data.

This project is designed as an HR leadership dashboard: it converts raw employee records into executive KPIs, diagnostic segmentation, risk scoring, and action-oriented retention insights.

## Business Objective

Employee attrition affects delivery capacity, hiring cost, team continuity, and workforce planning. This dashboard helps HR and business leaders answer:

- Which departments and job roles have the highest attrition exposure?
- Which demographic, tenure, workload, and compensation patterns are linked with employee exits?
- Where should retention interventions be prioritised?
- Which employees or employee segments show elevated predictive attrition risk?
- How do compensation, overtime, travel, promotion history, and satisfaction scores relate to retention?

## Application Modules

| Module | Purpose |
|---|---|
| Overview | Enterprise workforce baseline, attrition KPIs, retention mix, department rates, satisfaction gap analysis |
| Department & Role | Department-level alerts, role hotspots, heatmaps, exit-flow analysis, benchmark comparison |
| Demographics | Age, gender, marital status, education, and intersectional cohort attrition analysis |
| Tenure & Workload | Overtime, travel, distance-from-home, tenure, manager tenure, and promotion-band analysis |
| Risk Score | Gradient Boosting attrition risk scoring, calibrated risk tiers, model performance, feature importance |
| Compensation | Income bands, salary hike, stock options, pay-equity patterns, and experience-to-income analysis |
| Executive Summary | Leadership-ready summary with KPIs, findings, priority actions, and module navigation |
| Cohort Analysis | Custom two-dimensional cohort matrices with top-risk combinations and validation |

## Key Capabilities

- Multi-page Streamlit interface with persistent sidebar navigation
- Global workforce filters for department, role, tenure, overtime, travel, and gender
- Plotly-based interactive charts and executive-ready visual design
- Cached data pipeline with validation checks and derived HR analytics features
- Attrition risk scoring using scikit-learn Gradient Boosting
- Calibrated risk tiers and model performance reporting
- Statistical testing guardrails for small sample groups
- Downloadable filtered datasets for offline HR analysis
- Company-style UI with executive summary and leadership framing

## Dataset

The application expects the dataset file in the project root:

```text
Palo_Alto_Networks.csv
```

Dataset profile:

- Records: 1,470 employees
- Target column: `Attrition`
- Target encoding: `1 = Left`, `0 = Stayed`
- Missing values: none
- Key domains: demographics, role, department, tenure, workload, compensation, satisfaction, performance, and travel

The data loader creates additional business-ready fields such as:

- `Attrition_Label`
- `AgeGroup`
- `TenureBucket`
- `CareerStage`
- `IncomeBand`
- `DistanceBand`
- `PromotionBand`
- `PerformanceLabel`
- `DeptRole`
- `SatisfactionIndex`
- `WorkloadStress`
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
utils/
  __init__.py
  charts.py
  config.py
  data_loader.py
  kpis.py
  theme.py
.streamlit/
  config.toml
requirements.txt
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

`app.py` redirects directly to the Overview module while keeping Streamlit's standard launch flow.

## Data Accuracy Controls

The project includes pipeline safeguards for reliable HR analytics:

- Defensive `Attrition` normalization to binary integer values
- Ordered `BusinessTravel` category handling
- Correct distance bands based on the dataset maximum
- Promotion-band analysis instead of misleading binary stagnation logic
- Performance labels restricted to observed rating values
- Workload-stress validation checks
- Bounded loyalty score and income-level ratio validation
- Chi-square small-sample warnings
- ML encoding that treats ordinal, binary, and nominal fields appropriately

## Model Summary

The Risk Score module uses a Gradient Boosting classifier to estimate employee attrition probability. The model includes:

- Balanced sample weighting for class imbalance
- Proper encoding for travel, overtime, department, and marital status
- F1-optimised decision threshold
- Calibrated low, medium, and high risk tiers
- Feature importance ranking
- High-risk segment table for retention planning

## Usage Notes

- Keep `Palo_Alto_Networks.csv` in the same directory as `app.py`.
- Do not rename the files inside `pages/`; Streamlit uses the numeric prefixes for page order.
- All visualizations are built with Plotly.
- Data loading uses `st.cache_data`.
- Model training uses `st.cache_resource`.

## Intended Audience

This dashboard is built for:

- HR leadership
- People analytics teams
- Department heads
- Workforce planning teams
- Academic or portfolio reviewers evaluating an enterprise analytics project

