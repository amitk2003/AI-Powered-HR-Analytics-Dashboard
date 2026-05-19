"""
ml_model.py — Scikit-learn ML pipeline
- Random Forest Classifier  (primary model)
- Logistic Regression       (comparison model)
- Feature importance, ROC curve data, attrition risk scores
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_curve, auc
)

FEATURES = [
    "Age", "Tenure", "Salary", "Satisfaction", "WorkLifeBalance",
    "Overtime", "Performance", "ManagerRating", "LastHikePct",
    "PromotionGap", "Distance", "Education"
]

_models: dict = {}


def _prepare(df: pd.DataFrame):
    X = df[FEATURES].copy()
    y = df["Attrition"].values
    return X, y


def train_models(df: pd.DataFrame) -> dict:
    global _models
    X, y = _prepare(df)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_sc = scaler.fit_transform(X_train)
    X_test_sc  = scaler.transform(X_test)

    # Random Forest
    rf = RandomForestClassifier(n_estimators=200, max_depth=8, random_state=42)
    rf.fit(X_train, y_train)
    rf_pred  = rf.predict(X_test)
    rf_prob  = rf.predict_proba(X_test)[:, 1]
    rf_fpr, rf_tpr, _ = roc_curve(y_test, rf_prob)
    rf_auc = round(auc(rf_fpr, rf_tpr), 3)

    # Logistic Regression
    lr = LogisticRegression(max_iter=1000, random_state=42)
    lr.fit(X_train_sc, y_train)
    lr_pred = lr.predict(X_test_sc)
    lr_prob = lr.predict_proba(X_test_sc)[:, 1]
    lr_fpr, lr_tpr, _ = roc_curve(y_test, lr_prob)
    lr_auc = round(auc(lr_fpr, lr_tpr), 3)

    _models = {
        "rf": rf, "lr": lr, "scaler": scaler,
        "features": FEATURES,
        "rf_metrics": {
            "accuracy":  round(accuracy_score(y_test, rf_pred) * 100, 1),
            "precision": round(precision_score(y_test, rf_pred) * 100, 1),
            "recall":    round(recall_score(y_test, rf_pred) * 100, 1),
            "f1":        round(f1_score(y_test, rf_pred) * 100, 1),
            "auc":       rf_auc,
        },
        "lr_metrics": {
            "accuracy":  round(accuracy_score(y_test, lr_pred) * 100, 1),
            "precision": round(precision_score(y_test, lr_pred) * 100, 1),
            "recall":    round(recall_score(y_test, lr_pred) * 100, 1),
            "f1":        round(f1_score(y_test, lr_pred) * 100, 1),
            "auc":       lr_auc,
        },
        "roc": {
            "rf":  {"fpr": rf_fpr.round(3).tolist(), "tpr": rf_tpr.round(3).tolist(), "auc": rf_auc},
            "lr":  {"fpr": lr_fpr.round(3).tolist(), "tpr": lr_tpr.round(3).tolist(), "auc": lr_auc},
        },
        "feature_importance": dict(zip(
            FEATURES,
            rf.feature_importances_.round(4).tolist()
        )),
    }
    return _models


def get_models():
    return _models


def predict_risk(df: pd.DataFrame) -> list[dict]:
    """Return top-20 high-risk employees with their predicted attrition probability."""
    if not _models:
        return []
    rf    = _models["rf"]
    X, _  = _prepare(df)
    probs = rf.predict_proba(X)[:, 1]
    df    = df.copy()
    df["RiskScore"] = (probs * 100).round(1)
    df["RiskLevel"] = pd.cut(
        df["RiskScore"],
        bins=[0, 40, 65, 100],
        labels=["Low", "Medium", "High"]
    )
    top = (
        df[df["Attrition"] == 0]   # active employees only
        .sort_values("RiskScore", ascending=False)
        .head(20)
    )
    return top[[
        "EmployeeID", "Department", "Tenure", "Satisfaction",
        "RiskScore", "RiskLevel"
    ]].to_dict(orient="records")
