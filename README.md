# Palo Alto Networks Workforce Attrition Dashboard

A production-ready multi-page Streamlit analytics application for workforce attrition pattern analysis at Palo Alto Networks.

The dashboard helps HR leaders identify attrition hotspots across departments, job roles, demographics, tenure, workload, compensation, and predictive risk segments.

## Features

- Executive landing dashboard with key workforce attrition KPIs
- Attrition overview with retention ratio, department rates, income distribution, and satisfaction radar
- Department and job-role analysis with filters and heatmaps
- Demographic attrition explorer for age, gender, education, marital status, and education field
- Tenure and workload analysis with overtime, travel, promotion stagnation, and distance-from-home trends
- Machine-learning attrition risk scoring using Gradient Boosting
- Compensation analysis covering income bands, salary hikes, stock options, and experience-to-income patterns

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
utils/
  __init__.py
  charts.py
  data_loader.py
  kpis.py
  theme.py
requirements.txt
Palo_Alto_Networks.csv
```

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
streamlit run app.py
```

Then open:

```text
http://localhost:8501
```

## Dataset

The application expects `Palo_Alto_Networks.csv` in the same directory as `app.py`.

The target column is `Attrition`, where:

- `1` means the employee left
- `0` means the employee stayed

## Tech Stack

- Streamlit
- Pandas
- NumPy
- Plotly
- scikit-learn

## Notes

All visualizations use Plotly. Data loading is cached with `st.cache_data`, and the risk model is cached with `st.cache_resource`.
