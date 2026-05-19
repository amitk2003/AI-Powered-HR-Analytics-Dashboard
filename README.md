# 🤖 AI-Powered HR Analytics Dashboard

An end-to-end, full-stack HR analytics platform built to analyze workforce trends, employee attrition, hiring funnel performance, and engagement metrics — powered by **Python**, **FastAPI**, **Scikit-learn**, **Pandas**, **NumPy**, **SQLAlchemy**, and an interactive **Chart.js** frontend.

---

## 📸 Dashboard Preview

| Overview | Attrition Analysis | AI Insights |
|---|---|---|
| KPI cards, headcount trend, hiring vs attrition | Dept-wise attrition, ML risk table | ROC curve, feature importance, NLP sentiment |

---

## 🧰 Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Backend API** | FastAPI + Uvicorn | REST endpoints serving all analytics data |
| **Data Processing** | Pandas, NumPy | ETL, aggregations, feature engineering |
| **Machine Learning** | Scikit-learn | Random Forest + Logistic Regression attrition model |
| **Database** | SQLAlchemy + SQLite | SQL queries with CTEs & window functions (PostgreSQL-compatible) |
| **NLP** | Custom lexicon engine | Employee feedback sentiment analysis |
| **Frontend** | HTML5, CSS3, Chart.js | Interactive dashboard with 20+ charts |
| **Serving** | FastAPI StaticFiles | Single server for API + frontend |

---

## 📁 Project Structure

```
Hr_analytics/
│
├── index.html              # Dashboard frontend
├── style.css               # Dark glassmorphism UI styles
├── app.js                  # Chart.js — fetches data from FastAPI /api/*
│
└── backend/
    ├── main.py             # FastAPI app — all API routes
    ├── data.py             # Pandas + NumPy data processing & analytics
    ├── ml_model.py         # Scikit-learn ML pipeline (RF + LR)
    ├── nlp.py              # NLP sentiment analysis engine
    ├── database.py         # SQLAlchemy ORM + SQL query helpers
    ├── hr_data.csv         # Auto-generated synthetic HR dataset (1,470 rows)
    ├── hrdb.sqlite         # SQLite database (auto-created on first run)
    └── requirements.txt    # Python dependencies
```

---

## 🚀 Getting Started

### 1. Clone / Open the Project

```bash
cd "C:\Users\amitk\OneDrive\Desktop\Hr_analytics"
```

### 2. Install Python Dependencies

```bash
pip install -r backend/requirements.txt
```

### 3. Start the FastAPI Backend

```bash
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

On startup the server will automatically:
- ✅ Generate `hr_data.csv` (1,470 synthetic employee records)
- ✅ Initialize the SQLite database and populate tables
- ✅ Train the **Random Forest** and **Logistic Regression** models

### 4. Open the Dashboard

Visit **[http://localhost:8000](http://localhost:8000)** in your browser.

> Interactive API docs available at **[http://localhost:8000/docs](http://localhost:8000/docs)**

---

## 📊 Dashboard Pages & KPIs

| Page | Metrics Covered |
|---|---|
| **Overview** | Total Headcount, Attrition Rate, Offer Acceptance, Satisfaction, Burnout Risk, Avg CTC |
| **Attrition Analysis** | Dept-wise attrition %, tenure bands, exit reasons, ML risk-scored employee table |
| **Hiring Funnel** | Application → Screened → Interview → Offer → Joined, source effectiveness, time-to-hire |
| **Engagement** | eNPS score, satisfaction by dept, burnout heatmap, NLP sentiment, feedback cards |
| **Compensation** | Salary min/avg/max by dept, pay band distribution, promotion counts, CTC growth |
| **Diversity & Inclusion** | Gender ratio (overall + by dept), age distribution, employment type, D&I index |
| **AI Insights** | ROC curve (RF vs LR), feature importance, NLP monthly sentiment, executive narrative |

---

## 🤖 Machine Learning

### Models Trained (Scikit-learn)

| Model | Accuracy | Precision | Recall | F1 | AUC-ROC |
|---|---|---|---|---|---|
| **Random Forest** | ~66% | ~63% | ~36% | ~46% | ~0.66 |
| **Logistic Regression** | ~68% | ~65% | ~42% | ~51% | ~0.67 |

> Metrics are computed live on each server start against a 25% test split of the dataset.

### Features Used for Attrition Prediction

```
Age, Tenure, Salary, Satisfaction, WorkLifeBalance,
Overtime, Performance, ManagerRating, LastHikePct,
PromotionGap, Distance, Education
```

### Attrition Risk Scoring (`/api/attrition/risk-employees`)
Active employees are scored by the trained Random Forest model and ranked by predicted attrition probability. The top 20 are surfaced in the dashboard risk table.

---

## 🗃️ Dataset

**File:** `backend/hr_data.csv`  
**Rows:** 1,470 synthetic employee records (IBM HR Attrition Dataset inspired)  
**Auto-generated** using NumPy on first run — no manual download required.

### Columns

| Column | Type | Description |
|---|---|---|
| `EmployeeID` | int | Unique employee identifier |
| `Age` | int | Employee age (22–57) |
| `Gender` | str | Male / Female |
| `Department` | str | Engineering, Sales, HR, Finance, Marketing, Operations |
| `Tenure` | int | Months at company |
| `Salary` | float | Annual CTC in ₹ Lakhs |
| `Satisfaction` | float | Self-reported satisfaction score (1–10) |
| `WorkLifeBalance` | int | Rating 1–4 |
| `Overtime` | int | 1 = works overtime, 0 = no |
| `Performance` | int | Rating 1–4 |
| `ManagerRating` | float | Manager effectiveness score (2–5) |
| `LastHikePct` | float | Last salary hike % |
| `PromotionGap` | int | Years since last promotion |
| `Distance` | int | Commute distance (km) |
| `Education` | int | Education level 1–5 |
| `HireSource` | str | LinkedIn / Referral / Job Board / Campus / Agency / Direct |
| `EmploymentType` | str | Full-Time / Part-Time / Contract / Intern |
| `Sentiment` | str | NLP-derived: Positive / Neutral / Negative |
| `Attrition` | int | Target label: 1 = left, 0 = active |

---

## 🗄️ SQL Queries (SQLAlchemy)

The `database.py` module demonstrates production-grade SQL patterns:

```sql
-- CTE + Window Function: Risk-ranked active employees
WITH risk_scored AS (
    SELECT EmployeeID, Department, Tenure, Satisfaction,
           (10 - Satisfaction) * 0.25 + Overtime * 1.5 + ... AS risk_score,
           ROW_NUMBER() OVER (ORDER BY risk_score DESC) AS rank
    FROM employees WHERE Attrition = 0
)
SELECT * FROM risk_scored WHERE rank <= 20;

-- GROUP BY aggregation: Attrition rate per department
SELECT Department, COUNT(*) AS total, SUM(Attrition) AS exits,
       ROUND(AVG(CAST(Attrition AS FLOAT)) * 100, 1) AS attrition_rate
FROM employees GROUP BY Department ORDER BY attrition_rate DESC;
```

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/overview/kpis` | Headcount, attrition, salary, satisfaction KPIs |
| GET | `/api/overview/headcount-by-dept` | Active headcount per department |
| GET | `/api/overview/hiring-vs-attrition` | Monthly hires vs exits |
| GET | `/api/attrition/by-dept` | Attrition rate per dept (SQL) |
| GET | `/api/attrition/by-tenure` | Attrition by tenure band |
| GET | `/api/attrition/risk-employees` | ML-scored top-risk employees |
| GET | `/api/hiring/funnel` | Hiring funnel stage counts |
| GET | `/api/hiring/sources` | Hire source distribution |
| GET | `/api/engagement/satisfaction-by-dept` | Avg satisfaction per dept |
| GET | `/api/engagement/burnout-by-dept` | Overtime/burnout % per dept |
| GET | `/api/engagement/feedback` | NLP-analyzed feedback cards |
| GET | `/api/compensation/salary-by-dept` | Min/avg/max salary (SQL) |
| GET | `/api/compensation/promotions` | Promotion counts per dept |
| GET | `/api/diversity/gender-by-dept` | Gender split per dept |
| GET | `/api/diversity/age-distribution` | Age band distribution |
| GET | `/api/ai/model-metrics` | RF + LR accuracy, F1, AUC |
| GET | `/api/ai/roc-curve` | ROC curve data for both models |
| GET | `/api/ai/feature-importance` | RF feature importances |

Full interactive docs: **http://localhost:8000/docs**

---

## 🐘 Switching to PostgreSQL

The app is PostgreSQL-compatible via SQLAlchemy. Set the environment variable:

```bash
# Windows PowerShell
$env:DATABASE_URL = "postgresql+psycopg2://user:password@localhost:5432/hrdb"

# Or add to backend/.env
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/hrdb
```

Then restart the server — SQLAlchemy will auto-create tables in PostgreSQL.

---

## 📦 Requirements

```
fastapi
uvicorn
pandas
numpy
scikit-learn
sqlalchemy
aiofiles
python-multipart
```

Install: `pip install -r backend/requirements.txt`

---

## 👤 Author

**Amit Kumar** — HR Analytics Platform  
Built with Python · FastAPI · Scikit-learn · Pandas · SQLAlchemy · Chart.js
