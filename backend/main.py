"""
main.py — FastAPI application
Serves all analytics endpoints consumed by the frontend dashboard.
"""

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import uvicorn

from data import (
    load_df, kpi_overview, headcount_by_dept, attrition_by_dept,
    tenure_bands, salary_stats_by_dept, sentiment_distribution,
    hiring_source_dist, gender_by_dept, age_distribution,
    burnout_by_dept, satisfaction_by_dept, promotion_by_dept,
    employment_type_dist
)
from ml_model import train_models, predict_risk, get_models
from nlp import analyze_feedback, top_themes
from database import init_db, sql_attrition_by_dept, sql_top_risk_employees, sql_hiring_funnel, sql_salary_percentiles

# ── APP SETUP ─────────────────────────────────
app = FastAPI(
    title="HR Analytics API",
    description="AI-Powered HR Analytics — FastAPI + Pandas + Scikit-learn",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Frontend directory (one level up from backend/)
FRONTEND_DIR = Path(__file__).parent.parent

# ── STARTUP: load data, train models ─────────
@app.on_event("startup")
async def startup():
    df = load_df()
    init_db(df)
    train_models(df)
    print(f"[OK] Dataset loaded: {len(df)} rows")
    print("[OK] ML models trained")





# ── OVERVIEW ENDPOINTS ────────────────────────
@app.get("/api/overview/kpis", tags=["Overview"])
def overview_kpis():
    """Top-level KPIs: headcount, attrition, satisfaction, burnout, salary."""
    df = load_df()
    return kpi_overview(df)


@app.get("/api/overview/headcount-by-dept", tags=["Overview"])
def overview_headcount(dept: str = Query(default="all")):
    df = load_df()
    if dept != "all":
        df = df[df["Department"].str.lower() == dept.lower()]
    return headcount_by_dept(df)


@app.get("/api/overview/hiring-vs-attrition", tags=["Overview"])
def hiring_vs_attrition():
    """Monthly simulated hiring and attrition counts."""
    import numpy as np
    rng = np.random.default_rng(7)
    months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    hires  = rng.integers(45, 95, size=12).tolist()
    exits  = rng.integers(25, 55, size=12).tolist()
    return {"months": months, "hires": hires, "exits": exits}


# ── ATTRITION ENDPOINTS ───────────────────────
@app.get("/api/attrition/by-dept", tags=["Attrition"])
def attr_by_dept():
    """Attrition rate per department — SQL aggregation via SQLAlchemy."""
    return sql_attrition_by_dept()


@app.get("/api/attrition/by-tenure", tags=["Attrition"])
def attr_by_tenure():
    df = load_df()
    return tenure_bands(df)


@app.get("/api/attrition/risk-employees", tags=["Attrition"])
def risk_employees():
    """Top at-risk active employees — ML predicted (Random Forest)."""
    df = load_df()
    return predict_risk(df)


@app.get("/api/attrition/sql-risk-table", tags=["Attrition"])
def sql_risk_table():
    """SQL CTE + window function risk table (pure SQL approach)."""
    return sql_top_risk_employees()


# ── HIRING ENDPOINTS ──────────────────────────
@app.get("/api/hiring/funnel", tags=["Hiring"])
def hiring_funnel():
    """Hiring funnel stages with conversion rates."""
    total = len(load_df())
    stages = [
        {"stage": "Applications",  "count": total * 10},
        {"stage": "Screened",      "count": total * 3},
        {"stage": "Phone Screen",  "count": total},
        {"stage": "Technical",     "count": int(total * 0.7)},
        {"stage": "Final Round",   "count": int(total * 0.4)},
        {"stage": "Offer Made",    "count": int(total * 0.28)},
        {"stage": "Joined",        "count": total},
    ]
    return stages


@app.get("/api/hiring/sources", tags=["Hiring"])
def hiring_sources():
    df = load_df()
    return hiring_source_dist(df)


@app.get("/api/hiring/offer-acceptance", tags=["Hiring"])
def offer_acceptance():
    """Simulated offer acceptance rate per department."""
    import numpy as np
    rng = np.random.default_rng(3)
    depts = ["Engineering","Sales","HR","Finance","Marketing","Operations"]
    return {d: round(rng.uniform(62, 85), 1) for d in depts}


# ── ENGAGEMENT ENDPOINTS ──────────────────────
@app.get("/api/engagement/satisfaction-by-dept", tags=["Engagement"])
def satisfaction():
    df = load_df()
    return satisfaction_by_dept(df)


@app.get("/api/engagement/burnout-by-dept", tags=["Engagement"])
def burnout():
    df = load_df()
    return burnout_by_dept(df)


@app.get("/api/engagement/sentiment", tags=["Engagement"])
def sentiment():
    df = load_df()
    return sentiment_distribution(df["Sentiment"])


@app.get("/api/engagement/feedback", tags=["Engagement"])
def feedback():
    """NLP-analyzed employee feedback cards."""
    return analyze_feedback()


@app.get("/api/engagement/themes", tags=["Engagement"])
def themes():
    """Top NLP-extracted themes from feedback."""
    return top_themes()


# ── COMPENSATION ENDPOINTS ────────────────────
@app.get("/api/compensation/salary-by-dept", tags=["Compensation"])
def salary_by_dept():
    """Min/avg/max salary by department — SQL query."""
    return sql_salary_percentiles()


@app.get("/api/compensation/promotions", tags=["Compensation"])
def promotions():
    df = load_df()
    return promotion_by_dept(df)


# ── DIVERSITY ENDPOINTS ───────────────────────
@app.get("/api/diversity/gender-by-dept", tags=["Diversity"])
def gender_dept():
    df = load_df()
    return gender_by_dept(df)


@app.get("/api/diversity/age-distribution", tags=["Diversity"])
def age_dist():
    df = load_df()
    return age_distribution(df)


@app.get("/api/diversity/employment-type", tags=["Diversity"])
def emp_type():
    df = load_df()
    return employment_type_dist(df)


# ── AI / ML ENDPOINTS ─────────────────────────
@app.get("/api/ai/model-metrics", tags=["AI"])
def model_metrics():
    """Random Forest + Logistic Regression metrics."""
    m = get_models()
    return {
        "random_forest":     m.get("rf_metrics", {}),
        "logistic_regression": m.get("lr_metrics", {}),
    }


@app.get("/api/ai/roc-curve", tags=["AI"])
def roc_curve_data():
    m = get_models()
    return m.get("roc", {})


@app.get("/api/ai/feature-importance", tags=["AI"])
def feature_importance():
    m = get_models()
    fi = m.get("feature_importance", {})
    return dict(sorted(fi.items(), key=lambda x: x[1], reverse=True))


# ── STATIC FILES (mounted LAST so API routes take priority) ──
# html=True means index.html is served for "/" automatically
app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
