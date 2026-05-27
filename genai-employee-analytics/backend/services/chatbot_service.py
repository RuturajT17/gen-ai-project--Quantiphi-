import re
from typing import Any, Dict, List, Optional

import pandas as pd

from services.llm_service import generate_insight
from services.utils import to_native_type
from services.chatbot_config import CHATBOT_MAX_COLUMNS, CHATBOT_MAX_ROWS


def _normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).lower()


def _row_to_text(row: pd.Series, columns: List[str]) -> str:
    parts = []
    for col in columns:
        value = row.get(col)
        if pd.isna(value):
            continue
        parts.append(f"{col}: {value}")
    return " | ".join(parts)


def _select_columns(df: pd.DataFrame, max_cols: int = CHATBOT_MAX_COLUMNS) -> List[str]:
    preferred = [
        "Employee_ID",
        "Department",
        "Job_Role",
        "Performance_Rating",
        "Employee_Engagement_Score",
        "Salary_Increase_%",
        "Bonus_%",
        "Project_Outcome",
        "Project_Role",
        "Training_Program",
        "Hiring_Source",
        "Employee_Resignation_Status",
    ]
    cols = [col for col in preferred if col in df.columns]
    if len(cols) >= max_cols:
        return cols[:max_cols]
    for col in df.columns:
        if col in cols:
            continue
        cols.append(col)
        if len(cols) >= max_cols:
            break
    return cols


def _simple_keyword_scores(docs: List[str], query: str) -> List[float]:
    tokens = set(re.findall(r"[a-z0-9_]+", query.lower()))
    scores = []
    for doc in docs:
        doc_tokens = set(re.findall(r"[a-z0-9_]+", doc.lower()))
        overlap = len(tokens & doc_tokens)
        scores.append(float(overlap))
    return scores


def _retrieve_rows(df: pd.DataFrame, query: str, top_k: int = CHATBOT_MAX_ROWS) -> List[Dict[str, Any]]:
    if df.empty:
        return []

    columns = _select_columns(df)
    texts = [_row_to_text(row, columns) for _, row in df.iterrows()]

    scores = None
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity

        vectorizer = TfidfVectorizer(stop_words="english")
        doc_matrix = vectorizer.fit_transform(texts)
        query_vec = vectorizer.transform([query])
        sims = cosine_similarity(query_vec, doc_matrix).flatten()
        scores = sims.tolist()
    except Exception:
        scores = _simple_keyword_scores(texts, query)

    ranked = sorted(enumerate(scores), key=lambda item: item[1], reverse=True)
    top_indices = [idx for idx, score in ranked[:top_k] if score > 0]
    if not top_indices:
        top_indices = [idx for idx, _ in ranked[:top_k]]

    sample = df.iloc[top_indices]
    records = sample.to_dict(orient="records")
    return [{k: to_native_type(v) for k, v in row.items()} for row in records]


def _pick_chart_column(df: pd.DataFrame, query: str) -> Optional[str]:
    query_lower = query.lower()
    for col in df.columns:
        name = col.replace("_", " ").lower()
        if name in query_lower:
            return col
    for col in df.columns:
        name = col.replace("_", " ").lower()
        if any(word in query_lower for word in name.split()):
            return col
    return None


def _build_chart(df: pd.DataFrame, query: str) -> Optional[Dict[str, Any]]:
    if df.empty:
        return None

    column = _pick_chart_column(df, query)
    if not column:
        return None

    series = df[column]
    query_lower = query.lower()

    if series.dtype == "object" or series.nunique(dropna=True) <= 10:
        counts = series.fillna("Unknown").value_counts().head(6)
        chart_type = "pie" if any(token in query_lower for token in ["share", "percentage", "proportion"]) else "bar"
        return {
            "type": chart_type,
            "title": f"Distribution of {column}",
            "labels": [str(label) for label in counts.index.tolist()],
            "values": [to_native_type(v) for v in counts.values.tolist()],
            "description": f"This {chart_type} chart shows how {column} values are distributed across the dataset.",
        }

    if pd.api.types.is_numeric_dtype(series):
        bins = pd.cut(series, bins=6)
        counts = bins.value_counts().sort_index()
        chart_type = "histogram" if any(token in query_lower for token in ["distribution", "range", "spread", "histogram"]) else "bar"
        return {
            "type": chart_type,
            "title": f"Distribution of {column}",
            "labels": [str(label) for label in counts.index.tolist()],
            "values": [to_native_type(v) for v in counts.values.tolist()],
            "description": f"This {chart_type} summarizes the spread of {column} across employees.",
        }

    return None


def generate_chat_response(df: pd.DataFrame, query: str) -> Dict[str, Any]:
    samples = _retrieve_rows(df, query)
    chart = _build_chart(df, query)

    columns = list(df.columns)
    prompt = f"""
You are an HR analytics assistant. Use the employee dataset context to answer the user query.

User Query:
{query}

Available Columns:
{columns}

Relevant Sample Records:
{samples}

Instructions:
1. Answer the query using the sample records.
2. If the query requests a visual, summarize what the chart indicates.
3. Provide concise, actionable insights.

Output Format:
- Response:
- Insights:
- Recommendations:
"""

    insight = generate_insight(prompt)

    summary = {
        "chart": chart,
        "chart_description": chart.get("description") if chart else None,
    }

    return {
        "count": len(samples),
        "sample": samples,
        "summary": summary,
        "insight": insight,
    }
