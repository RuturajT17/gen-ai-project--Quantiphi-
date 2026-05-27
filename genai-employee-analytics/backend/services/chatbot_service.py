import logging
import re
import time
from typing import Any, Dict, List, Optional

import pandas as pd

from services.llm_service import generate_insight
from services.utils import to_native_type
from services.chatbot_config import CHATBOT_MAX_COLUMNS, CHATBOT_MAX_ROWS

QUERY_COLUMN_MAP = {
    "performance": [
        "Performance_Rating",
        "Department",
        "avg_skill_score",
        "Employee_Engagement_Score",
    ],
    "attrition": [
        "Employee_Engagement_Score",
        "Overtime",
        "Salary_Increase_%",
        "Employee_Resignation_Status",
        "Job_Satisfaction",
    ],
    "training": [
        "Professional_Development_Hours",
        "Training_Program",
        "Training_Hours",
        "Mentor_Rating",
    ],
    "project": [
        "Project_Complexity",
        "Project_Outcome",
        "Project_Role",
        "Project_Size",
    ],
    "compensation": [
        "Salary_Increase_%",
        "Bonus_%",
        "Benefits_Score",
        "Annual_Salary_Increase_Percentage",
    ],
    "hiring": [
        "Hiring_Source",
        "Recruitment_Cost",
        "Time_to_Hire",
    ],
    "engagement": [
        "Employee_Engagement_Score",
        "Job_Satisfaction",
        "Work_Life_Balance",
    ],
}

FALLBACK_COLUMNS = [
    "Department",
    "Performance_Rating",
]

_VECTOR_CACHE: Dict[tuple, Dict[str, Any]] = {}
_RESPONSE_CACHE: Dict[str, Dict[str, Any]] = {}
_LAST_VECTOR_CACHE_HIT = False

logger = logging.getLogger("genai-employee-analytics.chatbot")


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


def _row_to_compact_summary(row: pd.Series, columns: List[str]) -> str:
    parts = []
    for col in columns:
        value = row.get(col)
        if pd.isna(value):
            continue
        label = col.replace("_", " ")
        parts.append(f"{label}={value}")
    return " | ".join(parts)


def normalize_query(query: str) -> str:
    return " ".join(query.lower().strip().split())


def _normalize_query_tokens(query: str) -> List[str]:
    return re.findall(r"[a-z0-9_]+", query)


def detect_relevant_columns(query: str, dataframe_columns: List[str]) -> List[str]:
    tokens = set(_normalize_query_tokens(query))
    matched_columns: List[str] = []

    for intent, columns in QUERY_COLUMN_MAP.items():
        if intent in tokens:
            for col in columns:
                if col in dataframe_columns and col not in matched_columns:
                    matched_columns.append(col)

    for col in dataframe_columns:
        col_tokens = set(re.findall(r"[a-z0-9_]+", col.lower()))
        if tokens & col_tokens:
            if col not in matched_columns:
                matched_columns.append(col)

    if not matched_columns:
        for col in FALLBACK_COLUMNS:
            if col in dataframe_columns:
                matched_columns.append(col)

    filtered = [col for col in matched_columns if col != "Employee_ID"]
    if not filtered:
        filtered = [col for col in matched_columns if col in dataframe_columns]

    return filtered[:CHATBOT_MAX_COLUMNS]


def _get_vector_cache_key(df: pd.DataFrame, columns: List[str]) -> tuple:
    return (
        tuple(columns),
        df.shape,
        tuple(df.columns),
    )


def _get_cached_vectors(df: pd.DataFrame, columns: List[str]) -> Dict[str, Any]:
    global _LAST_VECTOR_CACHE_HIT
    cache_key = _get_vector_cache_key(df, columns)
    cached = _VECTOR_CACHE.get(cache_key)
    if cached:
        _LAST_VECTOR_CACHE_HIT = True
        return cached

    texts = [_row_to_text(row, columns) for _, row in df.iterrows()]
    vectorizer = None
    matrix = None
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer

        vectorizer = TfidfVectorizer(stop_words="english")
        matrix = vectorizer.fit_transform(texts)
    except Exception:
        vectorizer = None
        matrix = None

    cached = {
        "row_count": len(df),
        "columns": columns,
        "texts": texts,
        "vectorizer": vectorizer,
        "matrix": matrix,
    }
    _VECTOR_CACHE[cache_key] = cached
    _LAST_VECTOR_CACHE_HIT = False
    return cached


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

    normalized_query = normalize_query(query)
    columns = detect_relevant_columns(normalized_query, list(df.columns))
    cache = _get_cached_vectors(df, columns)
    texts = cache["texts"]

    scores = None
    if cache.get("vectorizer") is not None and cache.get("matrix") is not None:
        try:
            from sklearn.metrics.pairwise import cosine_similarity

            query_vec = cache["vectorizer"].transform([normalized_query])
            sims = cosine_similarity(query_vec, cache["matrix"]).flatten()
            scores = sims.tolist()
        except Exception:
            scores = None

    if scores is None:
        scores = _simple_keyword_scores(texts, normalized_query)

    ranked = sorted(enumerate(scores), key=lambda item: item[1], reverse=True)
    reduced_top_k = min(top_k, 5)
    top_indices = [idx for idx, score in ranked[:reduced_top_k] if score > 0]
    if not top_indices:
        top_indices = [idx for idx, _ in ranked[:reduced_top_k]]

    sample = df.iloc[top_indices][columns]
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
    normalized_query = normalize_query(query)
    cached_response = _RESPONSE_CACHE.get(normalized_query)
    if cached_response:
        logger.info(
            "[CHATBOT] query=\"%s\" vector_cache_hit=%s response_cache_hit=%s retrieval_time_ms=%s prompt_row_count=%s relevant_column_count=%s",
            normalized_query,
            _LAST_VECTOR_CACHE_HIT,
            True,
            0,
            len(cached_response.get("sample", [])),
            0,
        )
        return cached_response

    retrieval_start = time.perf_counter()
    samples = _retrieve_rows(df, normalized_query)
    chart = _build_chart(df, normalized_query)
    retrieval_ms = int((time.perf_counter() - retrieval_start) * 1000)

    columns = detect_relevant_columns(normalized_query, list(df.columns))
    sample_rows = samples[:5]
    compact_rows = []
    for row in sample_rows:
        series = pd.Series(row)
        compact = _row_to_compact_summary(series, columns)
        if compact:
            compact_rows.append(compact)

    prompt = (
        "You are an HR analytics assistant. Use the employee data sample to answer the query. "
        "Respond with key insights and recommendations.\n\n"
        f"Query: {normalized_query}\n"
        f"Columns: {columns}\n"
        "Samples:\n"
        + "\n".join(f"- {row}" for row in compact_rows)
    )

    insight = generate_insight(prompt)
    logger.info(
        "[CHATBOT] query=\"%s\" vector_cache_hit=%s response_cache_hit=%s retrieval_time_ms=%s",
        normalized_query,
        _LAST_VECTOR_CACHE_HIT,
        False,
        retrieval_ms,
    )

    summary = {
        "chart": chart,
        "chart_description": chart.get("description") if chart else None,
    }

    response = {
        "count": len(samples),
        "sample": samples,
        "summary": summary,
        "insight": insight,
    }

    _RESPONSE_CACHE[normalized_query] = response
    logger.info(
        "[CHATBOT] query=\"%s\" vector_cache_hit=%s response_cache_hit=%s retrieval_time_ms=%s prompt_row_count=%s relevant_column_count=%s",
        normalized_query,
        _LAST_VECTOR_CACHE_HIT,
        False,
        retrieval_ms,
        len(compact_rows),
        len(columns),
    )
    return response
