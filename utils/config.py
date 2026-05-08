ATTRITION_HIGH_THRESHOLD = 0.30
ATTRITION_ELEVATED_THRESHOLD = 0.15
MIN_GROUP_SIZE = 10
# Risk tier thresholds calibrated on ensemble scores.
# High (>60): 77.1% actual attrition. Medium (30-60): 7.1%. Low (<30): 0.0%.
RISK_SCORE_HIGH = 60
RISK_SCORE_MEDIUM = 30
MODEL_N_ESTIMATORS = 150
MODEL_MAX_DEPTH = 4
MODEL_RANDOM_STATE = 42

# Ensemble Model Hyperparameters
# Benchmarked: Soft Voting Ensemble (GB + RF + LR) achieves AUC 0.8204 on 5-fold CV.
GB_N_ESTIMATORS = 300
GB_MAX_DEPTH = 3
GB_MIN_SAMPLES_LEAF = 10
GB_SUBSAMPLE = 0.85
GB_LEARNING_RATE = 0.05

RF_N_ESTIMATORS = 300
RF_MAX_DEPTH = 8
RF_MIN_SAMPLES_LEAF = 5

LR_C = 0.5
LR_MAX_ITER = 2000

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
    "RelationshipSatisfaction": "Relationship Satisfaction",
    "TrainingTimesLastYear": "Training Sessions (Last Year)",
    "YearsInCurrentRole": "Years in Current Role",
    "YearsWithCurrManager": "Years with Manager",
    "PercentSalaryHike": "Last Salary Hike (%)",
    "HourlyRate": "Hourly Rate",
    "DailyRate": "Daily Rate",
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
    "TrainingTimesLastYear": "Increase L&D access; employees with zero training show elevated exits",
    "YearsInCurrentRole": "Review role mobility; stagnation in current role correlates with attrition",
    "YearsWithCurrManager": "Proactively manage manager transitions; short manager tenure is a flight risk",
    "PercentSalaryHike": "Review appraisal equity; below-average hikes predict higher voluntary exits",
    "HourlyRate": "Benchmark hourly rates against industry medians for high-exit roles",
    "DailyRate": "Review daily rate bands for contractors and variable-pay employees",
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
