"""
nlp.py — Lightweight NLP sentiment analysis
Uses a VADER-style lexicon approach (no heavy dependencies).
For production, swap with transformers or spaCy.
"""

import re
from collections import Counter

# Simple sentiment word lists
POSITIVE_WORDS = {
    "great", "excellent", "happy", "amazing", "good", "wonderful", "love",
    "enjoy", "positive", "supportive", "transparent", "growth", "flexible",
    "valued", "motivated", "innovative", "collaborative", "invested", "clear",
    "balance", "rewarding", "appreciated", "inclusive", "trust", "proud"
}
NEGATIVE_WORDS = {
    "bad", "poor", "stress", "burnout", "toxic", "unfair", "unhappy", "quit",
    "overload", "pressure", "micromanage", "unrealistic", "frustrated",
    "underpaid", "ignored", "no growth", "lack", "overtime", "exhausted",
    "boring", "hostile", "confusing", "difficult", "problem", "issue"
}

SAMPLE_FEEDBACK = [
    ("Engineering",  "The new flex-work policy has significantly improved my work-life balance. Management is supportive and transparent."),
    ("Sales",        "Targets feel unrealistic this quarter. The pressure is causing stress and team friction. Need urgent review."),
    ("HR",           "Learning programs are excellent. I feel invested in and see a clear career path ahead. Loving the culture."),
    ("Marketing",    "Team dynamics are okay. Could use better cross-functional collaboration tools and streamlined processes."),
    ("Finance",      "Leadership is transparent and communicative. I feel valued and heard in meetings. Overall great experience."),
    ("Operations",   "Overtime is becoming the norm. Burnout is real — we need more headcount. Work-life balance is poor."),
    ("Engineering",  "Great team culture and challenging projects. Could improve documentation and onboarding for new hires."),
    ("Sales",        "Commission structure is unclear and often frustrating. Management should listen more to field teams."),
    ("HR",           "The L&D budget has doubled — amazing investment. Feeling motivated and aligned with company goals."),
    ("Marketing",    "Creative freedom is great, but deadlines are stressful. Better resource planning would be appreciated."),
    ("Finance",      "Processes are well-structured. Work is stable and rewarding. Salary could be more competitive though."),
    ("Operations",   "Loved the new safety training. Management could improve communication on project changes and priorities."),
]


def _score_text(text: str) -> str:
    words = set(re.findall(r'\b\w+\b', text.lower()))
    pos   = len(words & POSITIVE_WORDS)
    neg   = len(words & NEGATIVE_WORDS)
    if pos > neg:
        return "Positive"
    elif neg > pos:
        return "Negative"
    return "Neutral"


def analyze_feedback() -> list[dict]:
    results = []
    for dept, text in SAMPLE_FEEDBACK:
        label = _score_text(text)
        results.append({
            "department": dept,
            "text":       text,
            "sentiment":  label,
        })
    return results


def sentiment_summary(df_sentiment_col) -> dict:
    counts = Counter(df_sentiment_col)
    total  = sum(counts.values())
    return {k: round(v / total * 100, 1) for k, v in counts.items()}


def top_themes() -> list[str]:
    all_text = " ".join(t for _, t in SAMPLE_FEEDBACK).lower()
    words = re.findall(r'\b\w{4,}\b', all_text)
    stop  = {"that", "this", "with", "have", "been", "more", "feel", "could",
             "need", "work", "team", "better", "would", "also", "very", "from"}
    filtered = [w for w in words if w not in stop]
    common = Counter(filtered).most_common(8)
    return [w for w, _ in common]
