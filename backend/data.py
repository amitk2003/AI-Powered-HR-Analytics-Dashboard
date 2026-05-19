"""
data.py — Pandas + NumPy data processing layer
Generates a realistic synthetic HR dataset (IBM-style) and exposes
computed DataFrames for the FastAPI routes and ML model.
"""

import numpy as np
import pandas as pd
from pathlib import Path

CSV_PATH = Path(__file__).parent / "hr_data.csv"
_df: pd.DataFrame | None = None   # module-level cache


# ──────────────────────────────────────────────
# 1. DATASET GENERATION
# ──────────────────────────────────────────────
def generate_dataset(n: int = 1470, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    depts = ["Engineering", "Sales", "HR", "Finance", "Marketing", "Operations"]
    dept_weights = [0.30, 0.20, 0.07, 0.10, 0.13, 0.20]
    dept_arr = rng.choice(depts, size=n, p=dept_weights)

    age = rng.integers(22, 58, size=n)
    gender = rng.choice(["Male", "Female"], size=n, p=[0.62, 0.38])
    tenure = rng.integers(1, 120, size=n)          # months
    education = rng.choice([1, 2, 3, 4, 5], size=n)

    # Salary band depends on dept + tenure
    base_salary = {
        "Engineering": 22, "Finance": 20, "Sales": 16,
        "Marketing": 17, "HR": 14, "Operations": 15
    }
    salary = np.array([
        round(base_salary[d] + tenure[i] * 0.08 + rng.normal(0, 2), 1)
        for i, d in enumerate(dept_arr)
    ]).clip(8, 70)

    satisfaction = rng.uniform(1, 10, size=n).round(1)
    work_life = rng.integers(1, 5, size=n)
    overtime = rng.choice([0, 1], size=n, p=[0.72, 0.28])
    performance = rng.integers(1, 5, size=n)
    manager_rating = rng.uniform(2, 5, size=n).round(1)
    last_hike_pct = rng.uniform(3, 22, size=n).round(1)
    promotion_gap = rng.integers(0, 8, size=n)     # years since last promotion
    distance = rng.integers(1, 30, size=n)

    # Attrition: logistic blend of risk factors
    risk = (
        (10 - satisfaction) * 0.15
        + overtime * 1.2
        + (tenure < 24).astype(float) * 0.8
        + (promotion_gap > 4).astype(float) * 0.5
        + (work_life < 2).astype(float) * 0.6
        + rng.normal(0, 0.3, size=n)
    )
    prob_attr = 1 / (1 + np.exp(-risk + 2))
    attrition = (rng.random(size=n) < prob_attr).astype(int)

    # Hiring source
    sources = ["LinkedIn", "Referral", "Job Board", "Campus", "Agency", "Direct"]
    source_w = [0.35, 0.28, 0.18, 0.10, 0.06, 0.03]
    hire_source = rng.choice(sources, size=n, p=source_w)

    # Employment type
    emp_type = rng.choice(
        ["Full-Time", "Part-Time", "Contract", "Intern"],
        size=n, p=[0.78, 0.08, 0.10, 0.04]
    )

    # Sentiment (NLP label)
    sentiment_raw = satisfaction + rng.normal(0, 1, size=n)
    sentiment = np.where(sentiment_raw > 6.5, "Positive",
                np.where(sentiment_raw > 4.5, "Neutral", "Negative"))

    df = pd.DataFrame({
        "EmployeeID":    np.arange(1, n + 1),
        "Age":           age,
        "Gender":        gender,
        "Department":    dept_arr,
        "Tenure":        tenure,
        "Salary":        salary,
        "Satisfaction":  satisfaction,
        "WorkLifeBalance": work_life,
        "Overtime":      overtime,
        "Performance":   performance,
        "ManagerRating": manager_rating,
        "LastHikePct":   last_hike_pct,
        "PromotionGap":  promotion_gap,
        "Distance":      distance,
        "Education":     education,
        "HireSource":    hire_source,
        "EmploymentType": emp_type,
        "Sentiment":     sentiment,
        "Attrition":     attrition,
    })
    return df


# ──────────────────────────────────────────────
# 2. LOAD / CACHE
# ──────────────────────────────────────────────
def load_df() -> pd.DataFrame:
    global _df
    if _df is not None:
        return _df
    if CSV_PATH.exists():
        _df = pd.read_csv(CSV_PATH)
    else:
        _df = generate_dataset()
        CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
        _df.to_csv(CSV_PATH, index=False)
    return _df


# ──────────────────────────────────────────────
# 3. COMPUTED ANALYTICS
# ──────────────────────────────────────────────
def kpi_overview(df: pd.DataFrame) -> dict:
    active = df[df["Attrition"] == 0]
    return {
        "headcount":        int(len(active)),
        "attrition_rate":   round(df["Attrition"].mean() * 100, 1),
        "avg_salary":       round(active["Salary"].mean(), 1),
        "avg_satisfaction": round(active["Satisfaction"].mean(), 1),
        "burnout_risk":     round((active["Overtime"] == 1).mean() * 100, 1),
        "gender_ratio_f":   round((active["Gender"] == "Female").mean() * 100, 1),
    }


def headcount_by_dept(df: pd.DataFrame) -> dict:
    active = df[df["Attrition"] == 0]
    counts = active.groupby("Department").size().to_dict()
    return counts


def attrition_by_dept(df: pd.DataFrame) -> dict:
    rates = (
        df.groupby("Department")["Attrition"]
        .mean()
        .mul(100)
        .round(1)
        .to_dict()
    )
    return rates


def tenure_bands(df: pd.DataFrame) -> dict:
    bins = [0, 12, 24, 36, 60, 120, 999]
    labels = ["0-1yr", "1-2yr", "2-3yr", "3-5yr", "5-10yr", "10+yr"]
    df = df.copy()
    df["TenureBand"] = pd.cut(df["Tenure"], bins=bins, labels=labels, right=True)
    rates = (
        df.groupby("TenureBand", observed=True)["Attrition"]
        .mean().mul(100).round(1).to_dict()
    )
    return rates


def salary_stats_by_dept(df: pd.DataFrame) -> dict:
    active = df[df["Attrition"] == 0]
    stats = (
        active.groupby("Department")["Salary"]
        .agg(["min", "mean", "max"])
        .round(1)
        .to_dict(orient="index")
    )
    return stats


def sentiment_distribution(df: pd.DataFrame) -> dict:
    counts = df["Sentiment"].value_counts(normalize=True).mul(100).round(1).to_dict()
    return counts


def hiring_source_dist(df: pd.DataFrame) -> dict:
    counts = df["HireSource"].value_counts().to_dict()
    return counts


def gender_by_dept(df: pd.DataFrame) -> dict:
    active = df[df["Attrition"] == 0]
    result = {}
    for dept, grp in active.groupby("Department"):
        result[dept] = {
            "Male":   round((grp["Gender"] == "Male").mean() * 100, 1),
            "Female": round((grp["Gender"] == "Female").mean() * 100, 1),
        }
    return result


def age_distribution(df: pd.DataFrame) -> dict:
    bins   = [18, 25, 30, 35, 40, 45, 50, 99]
    labels = ["18-24", "25-29", "30-34", "35-39", "40-44", "45-49", "50+"]
    active = df[df["Attrition"] == 0].copy()
    active["AgeBand"] = pd.cut(active["Age"], bins=bins, labels=labels, right=False)
    return active["AgeBand"].value_counts().sort_index().to_dict()


def burnout_by_dept(df: pd.DataFrame) -> dict:
    active = df[df["Attrition"] == 0]
    return (
        active.groupby("Department")["Overtime"]
        .mean().mul(100).round(1).to_dict()
    )


def satisfaction_by_dept(df: pd.DataFrame) -> dict:
    active = df[df["Attrition"] == 0]
    return (
        active.groupby("Department")["Satisfaction"]
        .mean().round(2).to_dict()
    )


def promotion_by_dept(df: pd.DataFrame) -> dict:
    active = df[df["Attrition"] == 0]
    promoted = active[active["PromotionGap"] <= 2]
    return promoted.groupby("Department").size().to_dict()


def employment_type_dist(df: pd.DataFrame) -> dict:
    return df["EmploymentType"].value_counts().to_dict()
