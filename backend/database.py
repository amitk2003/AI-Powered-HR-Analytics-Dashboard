"""
database.py — SQLAlchemy layer (SQLite, PostgreSQL-compatible)
Stores the HR dataset and exposes SQL query helpers using SQLAlchemy Core.
Switch DATABASE_URL to a PostgreSQL DSN to connect to a real Postgres instance.
"""

import os
from pathlib import Path
from sqlalchemy import (
    create_engine, text, Table, Column, MetaData,
    Integer, Float, String, Boolean
)
import pandas as pd

# ── CONFIG ────────────────────────────────────
# For PostgreSQL: "postgresql+psycopg2://user:pass@localhost:5432/hrdb"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{Path(__file__).parent / 'hrdb.sqlite'}")

engine   = create_engine(DATABASE_URL, echo=False, future=True)
metadata = MetaData()

employees_table = Table(
    "employees", metadata,
    Column("EmployeeID",     Integer, primary_key=True),
    Column("Age",            Integer),
    Column("Gender",         String),
    Column("Department",     String),
    Column("Tenure",         Integer),
    Column("Salary",         Float),
    Column("Satisfaction",   Float),
    Column("WorkLifeBalance",Integer),
    Column("Overtime",       Integer),
    Column("Performance",    Integer),
    Column("ManagerRating",  Float),
    Column("LastHikePct",    Float),
    Column("PromotionGap",   Integer),
    Column("Distance",       Integer),
    Column("Education",      Integer),
    Column("HireSource",     String),
    Column("EmploymentType", String),
    Column("Sentiment",      String),
    Column("Attrition",      Integer),
)


def init_db(df: pd.DataFrame) -> None:
    """Create tables and populate from DataFrame (idempotent)."""
    metadata.create_all(bind=engine, checkfirst=True)
    with engine.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM employees")).scalar()
        if count == 0:
            df.to_sql("employees", conn, if_exists="append", index=False)
            conn.commit()


def sql_attrition_by_dept() -> list[dict]:
    """
    SQL: Attrition rate per department using GROUP BY + AVG
    (Demonstrates SQL aggregation & joins pattern)
    """
    query = text("""
        SELECT
            Department,
            COUNT(*)                                       AS total,
            SUM(Attrition)                                 AS exits,
            ROUND(AVG(CAST(Attrition AS FLOAT)) * 100, 1) AS attrition_rate,
            ROUND(AVG(Satisfaction), 2)                    AS avg_satisfaction,
            ROUND(AVG(Salary), 1)                          AS avg_salary
        FROM employees
        GROUP BY Department
        ORDER BY attrition_rate DESC
    """)
    with engine.connect() as conn:
        rows = conn.execute(query).mappings().all()
    return [dict(r) for r in rows]


def sql_top_risk_employees(limit: int = 20) -> list[dict]:
    """
    SQL: High-risk employees using CTE + window function pattern
    Employees with low satisfaction, overtime, and short tenure.
    """
    query = text(f"""
        WITH risk_scored AS (
            SELECT
                EmployeeID,
                Department,
                Tenure,
                Salary,
                Satisfaction,
                Overtime,
                PromotionGap,
                (
                    (10 - Satisfaction) * 0.25
                    + Overtime         * 1.5
                    + CASE WHEN Tenure < 24 THEN 1.0 ELSE 0.0 END
                    + CASE WHEN PromotionGap > 4 THEN 0.6 ELSE 0.0 END
                ) AS risk_score,
                ROW_NUMBER() OVER (ORDER BY (
                    (10 - Satisfaction) * 0.25
                    + Overtime * 1.5
                    + CASE WHEN Tenure < 24 THEN 1.0 ELSE 0.0 END
                    + CASE WHEN PromotionGap > 4 THEN 0.6 ELSE 0.0 END
                ) DESC) AS rank
            FROM employees
            WHERE Attrition = 0
        )
        SELECT * FROM risk_scored WHERE rank <= {limit}
        ORDER BY risk_score DESC
    """)
    with engine.connect() as conn:
        rows = conn.execute(query).mappings().all()
    return [dict(r) for r in rows]


def sql_hiring_funnel() -> list[dict]:
    """Simulate hiring funnel stages from HireSource distribution."""
    query = text("""
        SELECT HireSource, COUNT(*) AS hires
        FROM employees
        GROUP BY HireSource
        ORDER BY hires DESC
    """)
    with engine.connect() as conn:
        rows = conn.execute(query).mappings().all()
    return [dict(r) for r in rows]


def sql_salary_percentiles() -> list[dict]:
    """Salary stats per department."""
    query = text("""
        SELECT
            Department,
            ROUND(MIN(Salary), 1) AS min_salary,
            ROUND(AVG(Salary), 1) AS avg_salary,
            ROUND(MAX(Salary), 1) AS max_salary
        FROM employees
        WHERE Attrition = 0
        GROUP BY Department
        ORDER BY avg_salary DESC
    """)
    with engine.connect() as conn:
        rows = conn.execute(query).mappings().all()
    return [dict(r) for r in rows]
