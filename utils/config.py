ATTRITION_HIGH_THRESHOLD = 0.30
ATTRITION_ELEVATED_THRESHOLD = 0.15
MIN_GROUP_SIZE = 10
RISK_SCORE_HIGH = 60
# Risk tier thresholds were calibrated against actual attrition rates in each band.
# High (>60): near-certain historical attrition signal.
# Medium (28-60): elevated monitoring band.
# Low (<28): effectively retained population.
# Recalibrate annually as new cohorts accumulate.
RISK_SCORE_MEDIUM = 28
MODEL_N_ESTIMATORS = 150
MODEL_MAX_DEPTH = 4
MODEL_RANDOM_STATE = 42

TRAVEL_ORDER = ["Non-Travel", "Travel_Rarely", "Travel_Frequently"]

# Only ratings 3 and 4 exist in this dataset.
# Do not add labels for 1 or 2; they create empty categories.
PERFORMANCE_RATING_LABELS = {
    3: "Excellent",
    4: "Outstanding",
}

EDUCATION_LABELS = {
    1: "Below College",
    2: "College",
    3: "Bachelor",
    4: "Master",
    5: "Doctor",
}

JOB_LEVEL_LABELS = {
    1: "Entry",
    2: "Junior",
    3: "Mid",
    4: "Senior",
    5: "Principal",
}

AGE_BINS = [17, 25, 35, 45, 55, 100]
AGE_LABELS = ["18-25", "26-35", "36-45", "46-55", "55+"]

TENURE_BINS = [-1, 1, 3, 5, 10, 100]
TENURE_LABELS = ["0-1 yr", "1-3 yrs", "3-5 yrs", "5-10 yrs", "10+ yrs"]

CAREER_BINS = [-1, 5, 15, 100]
CAREER_LABELS = ["Early (0-5 yrs)", "Mid (6-15 yrs)", "Senior (15+ yrs)"]

INCOME_BINS = [0, 3000, 6000, 10000, 100_000]
INCOME_LABELS = ["Low (<$3K)", "Mid ($3-6K)", "High ($6-10K)", "Very High (>$10K)"]

DISTANCE_BINS = [0, 5, 15, 30]
DISTANCE_LABELS = ["<5 km", "5-14 km", "15-29 km"]

PROMOTION_STAGNATION_BINS = [-1, 0, 2, 5, 100]
PROMOTION_STAGNATION_LABELS = ["Just Promoted (0 yrs)", "1-2 yrs", "3-5 yrs", "5+ yrs"]

SATISFACTION_COLS = [
    "JobSatisfaction",
    "EnvironmentSatisfaction",
    "WorkLifeBalance",
    "RelationshipSatisfaction",
    "JobInvolvement",
]

SATISFACTION_LABELS = {
    "JobSatisfaction": "Job Satisfaction",
    "EnvironmentSatisfaction": "Environment",
    "WorkLifeBalance": "Work-Life Balance",
    "RelationshipSatisfaction": "Relationships",
    "JobInvolvement": "Job Involvement",
}

ML_FEATURE_LABELS = {
    "Age": "Age",
    "MonthlyIncome": "Monthly Income",
    "YearsAtCompany": "Tenure (Years)",
    "TotalWorkingYears": "Total Experience",
    "JobSatisfaction": "Job Satisfaction",
    "EnvironmentSatisfaction": "Environment Satisfaction",
    "WorkLifeBalance": "Work-Life Balance",
    "JobInvolvement": "Job Involvement",
    "JobLevel": "Job Level",
    "OverTime": "Works Overtime",
    "BusinessTravel": "Travel Frequency",
    "YearsSinceLastPromotion": "Years Since Promotion",
    "NumCompaniesWorked": "Prior Employers",
    "DistanceFromHome": "Distance from Home",
    "StockOptionLevel": "Stock Option Level",
    "Department": "Department",
    "MaritalStatus": "Marital Status",
}

INTERVENTION_MAP = {
    "OverTime": "Review workload distribution and enforce overtime caps",
    "BusinessTravel": "Introduce remote-work flexibility or travel stipends",
    "YearsSinceLastPromotion": "Accelerate promotion pipeline for stagnant employees",
    "MonthlyIncome": "Conduct salary band review for below-market roles",
    "StockOptionLevel": "Expand equity refresh program to Level 0 employees",
    "JobSatisfaction": "Deploy role redesign or job crafting workshops",
    "EnvironmentSatisfaction": "Audit physical and remote working conditions",
    "WorkLifeBalance": "Introduce mandatory PTO and flexible scheduling",
    "NumCompaniesWorked": "Strengthen onboarding and 90-day retention program",
    "DistanceFromHome": "Expand relocation support or remote-work policy",
}

DATASET_NOTES = {
    "StockOptionLevel": (
        "Attrition is non-monotonic: Level 0 and Level 3 both exceed Levels 1 and 2. "
        "Do not present stock options as a simple linear retention relationship."
    ),
    "YearsSinceLastPromotion": (
        "Recently promoted employees (0 yrs) show the highest attrition, not the lowest. "
        "Use granular promotion bands instead of a binary stagnant/not-stagnant flag."
    ),
    "PerformanceRating": (
        "Only ratings 3 (Excellent) and 4 (Outstanding) exist in this dataset."
    ),
    "DistanceFromHome": (
        "Maximum value is 29. A 30+ km distance band is always empty; use three bands."
    ),
}
