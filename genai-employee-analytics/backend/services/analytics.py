import pandas as pd

from config import SALARY_INCREASE_COLUMN
from services.utils import safe_sample_df, to_native_type


def _to_native(value):
    if isinstance(value, dict):
        return {key: _to_native(val) for key, val in value.items()}
    if isinstance(value, list):
        return [_to_native(val) for val in value]
    return to_native_type(value)


def get_basic_stats(df):
    performance = pd.to_numeric(df["Performance_Rating"], errors="coerce")
    salary_increase = pd.to_numeric(df[SALARY_INCREASE_COLUMN], errors="coerce")

    avg_performance = round(float(performance.mean()), 2)
    avg_salary_increase = round(float(salary_increase.mean()), 2)

    return {
        "total_employees": int(len(df)),
        "avg_performance": avg_performance,
        "avg_salary_increase": avg_salary_increase,
    }


def get_performance_groups(df):
    high_df = df[df["Performance_Rating"] >= 10]
    low_df = df[df["Performance_Rating"] <= 5]
    combined_df = pd.concat([high_df, low_df], ignore_index=True)
    count = int(len(combined_df))
    if count == 0:
        return {
            "count": 0,
            "sample": [],
            "summary": {},
            "message": "No matching employees found",
        }

    high_sample = safe_sample_df(high_df.sort_values(by="Performance_Rating"))
    low_sample = safe_sample_df(low_df.sort_values(by="Performance_Rating"))
    high_records = high_sample.to_dict(orient="records")
    low_records = low_sample.to_dict(orient="records")
    for row in high_records:
        row["performance_group"] = "high"
    for row in low_records:
        row["performance_group"] = "low"
    sample_records = high_records + low_records
    sample_records = [
        {key: to_native_type(value) for key, value in row.items()}
        for row in sample_records
    ]

    avg_performance = pd.to_numeric(
        combined_df["Performance_Rating"], errors="coerce"
    ).mean()
    if pd.isna(avg_performance):
        avg_performance = 0.0
    summary = {"avg_performance": round(float(avg_performance), 2)}
    if "avg_skill_score" in combined_df.columns:
        avg_skill = pd.to_numeric(
            combined_df["avg_skill_score"], errors="coerce"
        ).mean()
        if pd.isna(avg_skill):
            avg_skill = 0.0
        summary["avg_skill_score"] = round(float(avg_skill), 2)
    summary = {key: to_native_type(value) for key, value in summary.items()}

    return {
        "count": count,
        "sample": sample_records,
        "summary": summary,
    }


def get_underpaid(df):
    underpaid = df[
        (df["Performance_Rating"] > 8)
        & (df[SALARY_INCREASE_COLUMN] < 5)
    ]
    count = int(len(underpaid))
    if count == 0:
        return {
            "count": 0,
            "sample": [],
            "summary": {},
            "message": "No matching employees found",
        }

    sampled = safe_sample_df(underpaid.sort_values(by="Performance_Rating"))
    records = sampled.to_dict(orient="records")
    records = [
        {key: to_native_type(value) for key, value in row.items()}
        for row in records
    ]

    avg_performance = pd.to_numeric(
        underpaid["Performance_Rating"], errors="coerce"
    ).mean()
    if pd.isna(avg_performance):
        avg_performance = 0.0
    summary = {"avg_performance": round(float(avg_performance), 2)}
    if "avg_skill_score" in underpaid.columns:
        avg_skill = pd.to_numeric(
            underpaid["avg_skill_score"], errors="coerce"
        ).mean()
        if pd.isna(avg_skill):
            avg_skill = 0.0
        summary["avg_skill_score"] = round(float(avg_skill), 2)
    summary = {key: to_native_type(value) for key, value in summary.items()}

    return {
        "count": count,
        "sample": records,
        "summary": summary,
    }


def get_attrition_risk(df):
    engagement_filter = df["Employee_Engagement_Score"] < 5
    if "Overtime" in df.columns:
        overtime_filter = df["Overtime"] == "Yes"
        at_risk = df[engagement_filter | overtime_filter]
    else:
        at_risk = df[engagement_filter]
    count = int(len(at_risk))
    if count == 0:
        return {
            "count": 0,
            "sample": [],
            "summary": {},
            "message": "No matching employees found",
        }

    sampled = safe_sample_df(at_risk.sort_values(by="Performance_Rating"))
    records = sampled.to_dict(orient="records")
    records = [
        {key: to_native_type(value) for key, value in row.items()}
        for row in records
    ]

    avg_performance = pd.to_numeric(
        at_risk["Performance_Rating"], errors="coerce"
    ).mean()
    if pd.isna(avg_performance):
        avg_performance = 0.0
    summary = {"avg_performance": round(float(avg_performance), 2)}
    if "avg_skill_score" in at_risk.columns:
        avg_skill = pd.to_numeric(
            at_risk["avg_skill_score"], errors="coerce"
        ).mean()
        if pd.isna(avg_skill):
            avg_skill = 0.0
        summary["avg_skill_score"] = round(float(avg_skill), 2)
    summary = {key: to_native_type(value) for key, value in summary.items()}

    return {
        "count": count,
        "sample": records,
        "summary": summary,
    }


def training_analysis(df):
    cols = [
        "Professional_Development_Hours",
        "Performance_Rating",
        "Number_Of_Promotions",
    ]
    existing = [col for col in cols if col in df.columns]
    subset = df[existing].copy()
    count = int(len(subset))
    if count == 0:
        return {
            "count": 0,
            "sample": [],
            "summary": {},
            "message": "No matching employees found",
        }

    sampled = safe_sample_df(subset.sort_values(by="Performance_Rating"))
    records = sampled.to_dict(orient="records")
    records = [_to_native(row) for row in records]

    summary = {}
    if "Professional_Development_Hours" in subset.columns:
        avg_hours = pd.to_numeric(
            subset["Professional_Development_Hours"], errors="coerce"
        ).mean()
        if pd.isna(avg_hours):
            avg_hours = 0.0
        summary["avg_development_hours"] = round(float(avg_hours), 2)
    if "Performance_Rating" in subset.columns:
        avg_perf = pd.to_numeric(
            subset["Performance_Rating"], errors="coerce"
        ).mean()
        if pd.isna(avg_perf):
            avg_perf = 0.0
        summary["avg_performance"] = round(float(avg_perf), 2)
    if "Number_Of_Promotions" in subset.columns:
        avg_promotions = pd.to_numeric(
            subset["Number_Of_Promotions"], errors="coerce"
        ).mean()
        if pd.isna(avg_promotions):
            avg_promotions = 0.0
        summary["avg_promotions"] = round(float(avg_promotions), 2)

    return {
        "count": count,
        "sample": records,
        "summary": _to_native(summary),
    }


def soft_skills_analysis(df):
    if "soft_skill_score" not in df.columns:
        return {
            "count": 0,
            "sample": [],
            "summary": {},
            "message": "No matching employees found",
        }

    subset = df[["soft_skill_score", "Performance_Rating"]].copy()
    if subset["soft_skill_score"].nunique() < 3:
        subset["soft_skill_group"] = pd.cut(
            subset["soft_skill_score"], bins=3, labels=["low", "medium", "high"]
        )
    else:
        subset["soft_skill_group"] = pd.qcut(
            subset["soft_skill_score"], q=3, labels=["low", "medium", "high"]
        )

    count = int(len(subset))
    if count == 0:
        return {
            "count": 0,
            "sample": [],
            "summary": {},
            "message": "No matching employees found",
        }

    sampled = safe_sample_df(subset.sort_values(by="Performance_Rating"))
    records = sampled.to_dict(orient="records")
    records = [_to_native(row) for row in records]

    avg_soft = pd.to_numeric(
        subset["soft_skill_score"], errors="coerce"
    ).mean()
    if pd.isna(avg_soft):
        avg_soft = 0.0
    avg_perf = pd.to_numeric(
        subset["Performance_Rating"], errors="coerce"
    ).mean()
    if pd.isna(avg_perf):
        avg_perf = 0.0

    group_counts = (
        subset["soft_skill_group"].value_counts(dropna=False).to_dict()
    )

    summary = {
        "avg_soft_skill_score": round(float(avg_soft), 2),
        "avg_performance": round(float(avg_perf), 2),
        "group_counts": group_counts,
    }

    return {
        "count": count,
        "sample": records,
        "summary": _to_native(summary),
    }


def dashboard_overview_analysis(df):
    def safe_mean(column):
        if column not in df.columns:
            return None
        series = pd.to_numeric(df[column], errors="coerce")
        if series.dropna().empty:
            return None
        return round(float(series.mean()), 2)

    def to_series(column):
        if column not in df.columns:
            return pd.Series(dtype="float")
        return pd.to_numeric(df[column], errors="coerce")

    def distribution_numeric(series, bins=5):
        if series.dropna().empty:
            return []
        bucketed = pd.cut(series, bins=bins)
        counts = bucketed.value_counts().sort_index()
        return [
            {"label": str(label), "count": int(value)}
            for label, value in counts.items()
        ]

    def distribution_categorical(series, top_n=8):
        if series.dropna().empty:
            return []
        counts = series.fillna("Unknown").value_counts().head(top_n)
        return [
            {"label": str(label), "count": int(value)}
            for label, value in counts.items()
        ]

    def group_avg(group_col, value_col, top_n=8):
        if group_col not in df.columns or value_col not in df.columns:
            return []
        grouped = df[[group_col, value_col]].copy()
        grouped[value_col] = pd.to_numeric(grouped[value_col], errors="coerce")
        grouped = grouped.dropna(subset=[value_col])
        if grouped.empty:
            return []
        result = (
            grouped.groupby(group_col)[value_col]
            .mean()
            .sort_values(ascending=False)
            .head(top_n)
        )
        return [
            {"label": str(label), "value": round(float(value), 2)}
            for label, value in result.items()
        ]

    def group_avg_binned(series, value_col, bins=5):
        if series.dropna().empty or value_col not in df.columns:
            return []
        binned = pd.cut(series, bins=bins)
        grouped = df[[value_col]].copy()
        grouped[value_col] = pd.to_numeric(grouped[value_col], errors="coerce")
        grouped = grouped.dropna(subset=[value_col])
        grouped["bucket"] = binned
        grouped = grouped.dropna(subset=["bucket"])
        result = (
            grouped.groupby("bucket", observed=False)[value_col]
            .mean()
            .sort_index()
        )
        return [
            {"label": str(label), "value": round(float(value), 2)}
            for label, value in result.items()
        ]

    def stacked_counts(group_col, status_col, top_n=6):
        if group_col not in df.columns or status_col not in df.columns:
            return []
        subset = df[[group_col, status_col]].copy()
        subset[group_col] = subset[group_col].fillna("Unknown")
        subset[status_col] = subset[status_col].fillna("Unknown")
        counts = (
            subset.groupby([group_col, status_col])
            .size()
            .reset_index(name="count")
        )
        top_groups = (
            counts.groupby(group_col)["count"]
            .sum()
            .sort_values(ascending=False)
            .head(top_n)
            .index
        )
        counts = counts[counts[group_col].isin(top_groups)]
        output = []
        for label in top_groups:
            rows = counts[counts[group_col] == label]
            resigned = int(rows[rows[status_col] == "Yes"]["count"].sum())
            retained = int(rows[rows[status_col] != "Yes"]["count"].sum())
            output.append(
                {"label": str(label), "resigned": resigned, "retained": retained}
            )
        return output

    performance_series = to_series("Performance_Rating")
    engagement_series = to_series("Employee_Engagement_Score")
    salary_increase_series = to_series(SALARY_INCREASE_COLUMN)
    bonus_series = to_series("Bonus_%") if "Bonus_%" in df.columns else pd.Series(dtype="float")
    avg_skill = safe_mean("avg_skill_score") if "avg_skill_score" in df.columns else None

    attrition_risk_count = 0
    if "Employee_Engagement_Score" in df.columns:
        at_risk = df[engagement_series < 5]
        if "Overtime" in df.columns:
            at_risk = df[(engagement_series < 5) | (df["Overtime"] == "Yes")]
        attrition_risk_count = int(len(at_risk))

    kpis = {
        "total_employees": int(len(df)),
        "avg_performance": safe_mean("Performance_Rating"),
        "avg_engagement": safe_mean("Employee_Engagement_Score"),
        "avg_salary_increase": safe_mean(SALARY_INCREASE_COLUMN),
        "avg_skill_score": avg_skill,
        "attrition_risk_count": attrition_risk_count,
    }

    performance_distribution = distribution_numeric(performance_series)
    department_performance = group_avg("Department", "Performance_Rating")

    avg_skills = []
    for label, col in [
        ("Technical", "Technical_Skills_Rating"),
        ("Communication", "Communication_Skills_Rating"),
        ("Problem Solving", "Problem_Solving_Skills_Rating"),
    ]:
        value = safe_mean(col)
        if value is not None:
            avg_skills.append({"label": label, "value": value})

    soft_skill_clusters = []
    if "soft_skill_score" in df.columns:
        soft_series = to_series("soft_skill_score")
        if not soft_series.dropna().empty:
            if soft_series.nunique() < 3:
                buckets = pd.cut(soft_series, bins=3, labels=["low", "medium", "high"])
            else:
                buckets = pd.qcut(soft_series, q=3, labels=["low", "medium", "high"])
            cluster_counts = buckets.value_counts().reindex(["low", "medium", "high"]).fillna(0)
            soft_skill_clusters = [
                {"label": str(label), "count": int(value)}
                for label, value in cluster_counts.items()
            ]

    engagement_vs_attrition = []
    engagement_distribution = distribution_numeric(engagement_series)
    if "Employee_Resignation_Status" in df.columns and not engagement_series.dropna().empty:
        banded = pd.cut(engagement_series, bins=[-1, 4, 10], labels=["Low", "High"])
        temp = df.copy()
        temp["Engagement_Band"] = banded
        engagement_vs_attrition = stacked_counts("Engagement_Band", "Employee_Resignation_Status", top_n=2)

    overtime_vs_resignation = []
    overtime_distribution = []
    if "Overtime" in df.columns and "Employee_Resignation_Status" in df.columns:
        overtime_vs_resignation = stacked_counts("Overtime", "Employee_Resignation_Status", top_n=2)
    if "Overtime" in df.columns:
        overtime_distribution = distribution_categorical(df["Overtime"], top_n=3)

    training_hours_vs_performance = []
    if "Professional_Development_Hours" in df.columns:
        hours_series = to_series("Professional_Development_Hours")
        training_hours_vs_performance = group_avg_binned(hours_series, "Performance_Rating")

    training_program_comparison = group_avg("Training_Program", "Performance_Rating")

    if "Project_Outcome" in df.columns:
        project_success_failure = distribution_categorical(df["Project_Outcome"])
    else:
        project_success_failure = []
    project_role_comparison = group_avg("Project_Role", "Performance_Rating")

    salary_increase_vs_performance = group_avg_binned(salary_increase_series, "Performance_Rating")
    bonus_vs_performance = group_avg_binned(bonus_series, "Performance_Rating") if not bonus_series.empty else []
    salary_increase_distribution = distribution_numeric(salary_increase_series)
    salary_increase_by_department = group_avg("Department", SALARY_INCREASE_COLUMN)

    hiring_source_effectiveness = group_avg("Hiring_Source", "Performance_Rating")
    recruitment_cost_by_source = group_avg("Hiring_Source", "Recruitment_Cost")

    data = {
        "kpis": _to_native(kpis),
        "performance": {
            "performance_distribution": _to_native(performance_distribution),
            "department_performance": _to_native(department_performance),
        },
        "skills": {
            "avg_skills": _to_native(avg_skills),
            "soft_skill_clusters": _to_native(soft_skill_clusters),
        },
        "attrition": {
            "engagement_vs_attrition": _to_native(engagement_vs_attrition),
            "overtime_vs_resignation": _to_native(overtime_vs_resignation),
            "engagement_distribution": _to_native(engagement_distribution),
            "overtime_distribution": _to_native(overtime_distribution),
        },
        "training": {
            "training_hours_vs_performance": _to_native(training_hours_vs_performance),
            "training_program_comparison": _to_native(training_program_comparison),
        },
        "projects": {
            "project_success_failure": _to_native(project_success_failure),
            "project_role_comparison": _to_native(project_role_comparison),
        },
        "compensation": {
            "salary_increase_vs_performance": _to_native(salary_increase_vs_performance),
            "bonus_vs_performance": _to_native(bonus_vs_performance),
            "salary_increase_distribution": _to_native(salary_increase_distribution),
            "salary_increase_by_department": _to_native(salary_increase_by_department),
        },
        "hiring": {
            "hiring_source_effectiveness": _to_native(hiring_source_effectiveness),
            "recruitment_cost_by_source": _to_native(recruitment_cost_by_source),
        },
    }

    return _to_native(data)


def project_analysis(df):
    cols = [
        "Project_Complexity",
        "Project_Outcome",
        "Project_Role",
        "Performance_Rating",
    ]
    existing = [col for col in cols if col in df.columns]
    subset = df[existing].copy()
    count = int(len(subset))
    if count == 0:
        return {
            "count": 0,
            "sample": [],
            "summary": {},
            "message": "No matching employees found",
        }

    sampled = safe_sample_df(subset.sort_values(by="Performance_Rating"))
    records = sampled.to_dict(orient="records")
    records = [_to_native(row) for row in records]

    summary = {}
    if "Project_Complexity" in subset.columns and "Project_Outcome" in subset.columns:
        counts = pd.crosstab(
            subset["Project_Complexity"],
            subset["Project_Outcome"],
        ).to_dict()
        summary["complexity_outcome_counts"] = counts
    if "Performance_Rating" in subset.columns:
        avg_perf = pd.to_numeric(
            subset["Performance_Rating"], errors="coerce"
        ).mean()
        if pd.isna(avg_perf):
            avg_perf = 0.0
        summary["avg_performance"] = round(float(avg_perf), 2)

    return {
        "count": count,
        "sample": records,
        "summary": _to_native(summary),
    }


def compensation_analysis(df):
    cols = [SALARY_INCREASE_COLUMN, "Performance_Rating", "avg_skill_score"]
    existing = [col for col in cols if col in df.columns]
    subset = df[existing].copy()
    count = int(len(subset))
    if count == 0:
        return {
            "count": 0,
            "sample": [],
            "summary": {},
            "message": "No matching employees found",
        }

    sampled = safe_sample_df(subset.sort_values(by="Performance_Rating"))
    records = sampled.to_dict(orient="records")
    records = [_to_native(row) for row in records]

    summary = {}
    avg_salary = pd.to_numeric(
        subset[SALARY_INCREASE_COLUMN], errors="coerce"
    ).mean()
    if pd.isna(avg_salary):
        avg_salary = 0.0
    summary["avg_salary_increase"] = round(float(avg_salary), 2)
    avg_perf = pd.to_numeric(
        subset["Performance_Rating"], errors="coerce"
    ).mean()
    if pd.isna(avg_perf):
        avg_perf = 0.0
    summary["avg_performance"] = round(float(avg_perf), 2)
    if "avg_skill_score" in subset.columns:
        avg_skill = pd.to_numeric(
            subset["avg_skill_score"], errors="coerce"
        ).mean()
        if pd.isna(avg_skill):
            avg_skill = 0.0
        summary["avg_skill_score"] = round(float(avg_skill), 2)

    return {
        "count": count,
        "sample": records,
        "summary": _to_native(summary),
    }


def hiring_analysis(df):
    cols = [
        "Hiring_Source",
        "Time_to_Hire",
        "Recruitment_Cost",
        "Performance_Rating",
    ]
    existing = [col for col in cols if col in df.columns]
    subset = df[existing].copy()
    count = int(len(subset))
    if count == 0:
        return {
            "count": 0,
            "sample": [],
            "summary": {},
            "message": "No matching employees found",
        }

    sampled = safe_sample_df(subset.sort_values(by="Performance_Rating"))
    records = sampled.to_dict(orient="records")
    records = [_to_native(row) for row in records]

    summary = {}
    if "Hiring_Source" in subset.columns:
        summary["hiring_source_counts"] = (
            subset["Hiring_Source"].value_counts(dropna=False).to_dict()
        )
    if "Time_to_Hire" in subset.columns:
        avg_time = pd.to_numeric(
            subset["Time_to_Hire"], errors="coerce"
        ).mean()
        if pd.isna(avg_time):
            avg_time = 0.0
        summary["avg_time_to_hire"] = round(float(avg_time), 2)
    if "Recruitment_Cost" in subset.columns:
        avg_cost = pd.to_numeric(
            subset["Recruitment_Cost"], errors="coerce"
        ).mean()
        if pd.isna(avg_cost):
            avg_cost = 0.0
        summary["avg_recruitment_cost"] = round(float(avg_cost), 2)
    if "Performance_Rating" in subset.columns:
        avg_perf = pd.to_numeric(
            subset["Performance_Rating"], errors="coerce"
        ).mean()
        if pd.isna(avg_perf):
            avg_perf = 0.0
        summary["avg_performance"] = round(float(avg_perf), 2)

    return {
        "count": count,
        "sample": records,
        "summary": _to_native(summary),
    }


def get_composite_top_employees(df):
    rating_cols = [
        "Technical_Skills_Rating",
        "Communication_Skills_Rating",
        "Problem_Solving_Skills_Rating",
        "Leadership_Skills_Rating",
    ]
    valid_cols = [col for col in rating_cols if col in df.columns]
    if not valid_cols or df.empty:
        return {
            "count": 0,
            "sample": [],
            "summary": {},
            "message": "No matching employees found",
        }

    scored_df = df.copy()
    scored_df["composite_score"] = scored_df[valid_cols].mean(axis=1)
    top_count = int(0.1 * len(scored_df))
    if top_count <= 0:
        return {
            "count": 0,
            "sample": [],
            "summary": {},
            "message": "No matching employees found",
        }
    top_df = scored_df.nlargest(top_count, "composite_score")
    sample_df = safe_sample_df(top_df)

    return {
        "count": int(len(top_df)),
        "sample": [_to_native(row) for row in sample_df.to_dict(orient="records")],
        "summary": {
            "avg_composite_score": to_native_type(
                top_df["composite_score"].mean()
            )
        },
    }


def skill_weighted_model_analysis(df):
    cols = [
        "Technical_Skills_Rating",
        "Communication_Skills_Rating",
        "Problem_Solving_Skills_Rating",
        "Performance_Rating",
    ]
    if not all(col in df.columns for col in cols):
        return {
            "count": 0,
            "sample": [],
            "summary": {},
            "message": "No matching employees found",
        }

    df_valid = df[cols].dropna()
    count = int(len(df_valid))
    if count == 0:
        return {
            "count": 0,
            "sample": [],
            "summary": {},
            "message": "No matching employees found",
        }

    correlations = df_valid.corr(numeric_only=True)[
        "Performance_Rating"
    ].to_dict()
    sample_df = safe_sample_df(df_valid)

    return {
        "count": count,
        "sample": [_to_native(row) for row in sample_df.to_dict(orient="records")],
        "summary": {
            "skill_correlations": _to_native(correlations),
        },
    }


def skill_project_mismatch_analysis(df):
    required_cols = [
        "Technical_Skills_Rating",
        "Communication_Skills_Rating",
        "Problem_Solving_Skills_Rating",
        "Project_Outcome",
    ]
    if not all(col in df.columns for col in required_cols):
        return {
            "count": 0,
            "sample": [],
            "summary": {},
            "message": "No matching employees found",
        }

    scored_df = df.copy()
    scored_df["skill_score"] = scored_df[
        [
            "Technical_Skills_Rating",
            "Communication_Skills_Rating",
            "Problem_Solving_Skills_Rating",
        ]
    ].mean(axis=1)
    outcome = scored_df["Project_Outcome"].fillna("").astype(str).str.lower()
    mismatch_df = scored_df[(scored_df["skill_score"] > 8) & (outcome == "failed")]
    count = int(len(mismatch_df))
    if count == 0:
        return {
            "count": 0,
            "sample": [],
            "summary": {},
            "message": "No matching employees found",
        }

    sample_df = safe_sample_df(mismatch_df)

    return {
        "count": count,
        "sample": [_to_native(row) for row in sample_df.to_dict(orient="records")],
        "summary": {
            "avg_skill_score": to_native_type(
                mismatch_df["skill_score"].mean()
            )
        },
    }


def high_perf_low_leadership(df):
    if "Leadership_Skills_Rating" not in df.columns:
        return {
            "count": 0,
            "sample": [],
            "summary": {},
            "message": "No matching employees found",
        }

    filtered = df[
        (df["Performance_Rating"] >= 9)
        & (df["Leadership_Skills_Rating"] <= 5)
    ]
    count = int(len(filtered))
    if count == 0:
        return {
            "count": 0,
            "sample": [],
            "summary": {},
            "message": "No matching employees found",
        }

    sample_df = safe_sample_df(filtered)

    return {
        "count": count,
        "sample": [_to_native(row) for row in sample_df.to_dict(orient="records")],
        "summary": {
            "avg_performance": to_native_type(
                filtered["Performance_Rating"].mean()
            ),
            "avg_leadership": to_native_type(
                filtered["Leadership_Skills_Rating"].mean()
            ),
        },
    }


def training_correlation_analysis(df):
    cols = [
        "Professional_Development_Hours",
        "Performance_Rating",
        "Number_Of_Promotions",
    ]
    valid_cols = [col for col in cols if col in df.columns]
    if len(valid_cols) < 2:
        return {
            "count": 0,
            "sample": [],
            "summary": {},
            "message": "No matching employees found",
        }

    df_valid = df[valid_cols].dropna()
    count = int(len(df_valid))
    if count == 0:
        return {
            "count": 0,
            "sample": [],
            "summary": {},
            "message": "No matching employees found",
        }

    corr_matrix = df_valid.corr(numeric_only=True).to_dict()
    sample_df = safe_sample_df(df_valid)

    return {
        "count": count,
        "sample": [_to_native(row) for row in sample_df.to_dict(orient="records")],
        "summary": {
            "correlations": _to_native(corr_matrix),
        },
    }


def mentorship_analysis(df):
    required = ["Mentor_Rating", "Mentor_Experience_Level", "Performance_Rating"]
    if not all(col in df.columns for col in required):
        return {
            "count": 0,
            "sample": [],
            "summary": {},
            "message": "No matching employees found",
        }

    grouped = df.groupby(required[:-1]).agg({
        "Performance_Rating": "mean",
    }).reset_index()
    count = int(len(grouped))
    if count == 0:
        return {
            "count": 0,
            "sample": [],
            "summary": {},
            "message": "No matching employees found",
        }

    sample_df = safe_sample_df(grouped)

    summary = {
        "avg_performance": to_native_type(grouped["Performance_Rating"].mean())
    }
    if "Internship_Conversion_Status" in df.columns:
        conversion_values = (
            df["Internship_Conversion_Status"].fillna("").astype(str).str.lower()
        )
        total = len(conversion_values)
        if total:
            converted = (conversion_values == "yes").sum()
            summary["conversion_rate"] = to_native_type(
                round((converted / total) * 100, 2)
            )

    return {
        "count": count,
        "sample": [_to_native(row) for row in sample_df.to_dict(orient="records")],
        "summary": summary,
    }


def training_program_analysis(df):
    required = [
        "Training_Program",
        "Performance_Rating",
        "Number_Of_Promotions",
    ]
    if not all(col in df.columns for col in required):
        return {
            "count": 0,
            "sample": [],
            "summary": {},
            "message": "No matching employees found",
        }

    grouped = df.groupby("Training_Program").agg({
        "Performance_Rating": "mean",
        "Number_Of_Promotions": "mean",
    }).reset_index()
    count = int(len(grouped))
    if count == 0:
        return {
            "count": 0,
            "sample": [],
            "summary": {},
            "message": "No matching employees found",
        }

    sample_df = safe_sample_df(grouped)

    return {
        "count": count,
        "sample": [_to_native(row) for row in sample_df.to_dict(orient="records")],
        "summary": {
            "avg_performance": to_native_type(grouped["Performance_Rating"].mean())
        },
    }


def training_improvement_gap(df):
    required = ["Professional_Development_Hours"]
    if not all(col in df.columns for col in required):
        return {
            "count": 0,
            "sample": [],
            "summary": {},
            "message": "No matching employees found",
        }

    if {
        "Previous_Performance_Rating",
        "Current_Performance_Rating",
    }.issubset(df.columns):
        scored_df = df.copy()
        scored_df["performance_delta"] = (
            scored_df["Current_Performance_Rating"]
            - scored_df["Previous_Performance_Rating"]
        )
        gap_df = scored_df[
            (scored_df["Professional_Development_Hours"] > 20)
            & (scored_df["performance_delta"] <= 0)
        ]
        avg_delta = to_native_type(
            gap_df["performance_delta"].mean()
            if not gap_df.empty
            else 0
        )
        summary = {"avg_performance_delta": avg_delta}
    else:
        if "Performance_Rating" not in df.columns:
            return {
                "count": 0,
                "sample": [],
                "summary": {},
                "message": "No matching employees found",
            }
        gap_df = df[
            (df["Professional_Development_Hours"] > 20)
            & (df["Performance_Rating"] < 6)
        ]
        summary = {
            "avg_training_hours": to_native_type(
                gap_df["Professional_Development_Hours"].mean()
                if not gap_df.empty
                else 0
            )
        }
    count = int(len(gap_df))
    if count == 0:
        return {
            "count": 0,
            "sample": [],
            "summary": {},
            "message": "No matching employees found",
        }

    sample_df = safe_sample_df(gap_df)

    return {
        "count": count,
        "sample": [_to_native(row) for row in sample_df.to_dict(orient="records")],
        "summary": summary,
    }


def training_recommendation_candidates(df):
    required = ["Performance_Rating", "avg_skill_score", "Employee_Engagement_Score"]
    if not all(col in df.columns for col in required):
        return {
            "count": 0,
            "sample": [],
            "summary": {},
            "message": "No matching employees found",
        }

    scored_df = df.copy()
    scored_df["training_score"] = (
        (scored_df["Performance_Rating"] * 0.4)
        + (scored_df["avg_skill_score"] * 0.3)
        + (scored_df["Employee_Engagement_Score"] * 0.3)
    )
    candidates = scored_df[
        (scored_df["Performance_Rating"] >= 6)
        & (scored_df["Performance_Rating"] <= 8)
    ]
    count = int(len(candidates))
    if count == 0:
        return {
            "count": 0,
            "sample": [],
            "summary": {},
            "message": "No matching employees found",
        }

    top_candidates = candidates.sort_values(
        by="training_score", ascending=False
    )
    sample_df = safe_sample_df(top_candidates)

    return {
        "count": count,
        "sample": [_to_native(row) for row in sample_df.to_dict(orient="records")],
        "summary": {
            "avg_performance": to_native_type(
                candidates["Performance_Rating"].mean()
            ),
            "avg_training_score": to_native_type(
                candidates["training_score"].mean()
            ),
        },
    }


def soft_skill_clustering(df):
    cols = [
        "Leadership_Skills_Rating",
        "Teamwork_Skills_Rating",
        "Adaptability_Skills_Rating",
        "Creativity_Skills_Rating",
    ]
    valid_cols = [col for col in cols if col in df.columns]
    if len(valid_cols) < 3:
        return {
            "count": 0,
            "sample": [],
            "summary": {},
            "message": "No matching employees found",
        }

    try:
        from sklearn.cluster import KMeans
    except ImportError:
        return {
            "count": 0,
            "sample": [],
            "summary": {},
            "message": "No matching employees found",
        }

    df_valid = df[valid_cols].dropna().copy()
    count = int(len(df_valid))
    if count == 0:
        return {
            "count": 0,
            "sample": [],
            "summary": {},
            "message": "No matching employees found",
        }

    kmeans = KMeans(n_clusters=3, random_state=42)
    df_valid["cluster"] = kmeans.fit_predict(df_valid)

    sample_df = safe_sample_df(df_valid)
    cluster_summary = (
        df_valid.groupby("cluster").mean(numeric_only=True).to_dict()
    )

    return {
        "count": count,
        "sample": [_to_native(row) for row in sample_df.to_dict(orient="records")],
        "summary": {
            "cluster_profiles": _to_native(cluster_summary),
        },
    }


def conflict_vs_teamwork(df):
    required = ["Conflict_Resolution_Score", "Teamwork_Skills_Rating"]
    if not all(col in df.columns for col in required):
        return {
            "count": 0,
            "sample": [],
            "summary": {},
            "message": "No matching employees found",
        }

    filtered = df[
        (df["Conflict_Resolution_Score"] >= 8)
        & (df["Teamwork_Skills_Rating"] <= 5)
    ]
    count = int(len(filtered))
    if count == 0:
        return {
            "count": 0,
            "sample": [],
            "summary": {},
            "message": "No matching employees found",
        }

    sample_df = safe_sample_df(filtered)

    return {
        "count": count,
        "sample": [_to_native(row) for row in sample_df.to_dict(orient="records")],
        "summary": {
            "avg_conflict_score": to_native_type(
                filtered["Conflict_Resolution_Score"].mean()
            ),
            "avg_teamwork": to_native_type(
                filtered["Teamwork_Skills_Rating"].mean()
            ),
        },
    }


def engagement_satisfaction_analysis(df):
    cols = ["Employee_Engagement_Score", "Job_Satisfaction_Score"]
    valid_cols = [col for col in cols if col in df.columns]
    if len(valid_cols) < 2:
        return {
            "count": 0,
            "sample": [],
            "summary": {},
            "message": "No matching employees found",
        }

    df_valid = df[valid_cols].dropna()
    count = int(len(df_valid))
    if count == 0:
        return {
            "count": 0,
            "sample": [],
            "summary": {},
            "message": "No matching employees found",
        }

    correlation = df_valid.corr(numeric_only=True).to_dict()
    sample_df = safe_sample_df(df_valid)

    summary = {
        "engagement_satisfaction_correlation": _to_native(correlation),
    }

    if "Employee_Resignation_Status" in df.columns:
        status_df = df[
            [
                "Employee_Resignation_Status",
                "Employee_Engagement_Score",
                "Job_Satisfaction_Score",
            ]
        ].dropna()
        if not status_df.empty:
            grouped = status_df.groupby("Employee_Resignation_Status").agg({
                "Employee_Engagement_Score": "mean",
                "Job_Satisfaction_Score": "mean",
            })
            retention_analysis = {}
            for status, row in grouped.iterrows():
                key = str(status).strip().lower()
                if key in {"yes", "resigned", "true"}:
                    label = "resigned"
                elif key in {"no", "retained", "false"}:
                    label = "retained"
                else:
                    label = key
                retention_analysis[label] = {
                    "avg_engagement": to_native_type(row["Employee_Engagement_Score"]),
                    "avg_satisfaction": to_native_type(row["Job_Satisfaction_Score"]),
                }
            summary["retention_analysis"] = _to_native(retention_analysis)

    return {
        "count": count,
        "sample": [_to_native(row) for row in sample_df.to_dict(orient="records")],
        "summary": summary,
    }


def initiative_vs_innovation(df):
    cols = ["Initiative_Score", "Innovation_Score"]
    if not all(col in df.columns for col in cols):
        return {
            "count": 0,
            "sample": [],
            "summary": {},
            "message": "No matching employees found",
        }

    filtered = df[
        (df["Initiative_Score"] >= 8)
        & (df["Innovation_Score"] <= 5)
    ]
    count = int(len(filtered))
    if count == 0:
        return {
            "count": 0,
            "sample": [],
            "summary": {},
            "message": "No matching employees found",
        }

    sample_df = safe_sample_df(filtered)

    return {
        "count": count,
        "sample": [_to_native(row) for row in sample_df.to_dict(orient="records")],
        "summary": {
            "avg_initiative": to_native_type(
                filtered["Initiative_Score"].mean()
            ),
            "avg_innovation": to_native_type(
                filtered["Innovation_Score"].mean()
            ),
        },
    }


def project_complexity_size_analysis(df):
    required = ["Project_Complexity", "Project_Size", "Project_Outcome"]
    if not all(col in df.columns for col in required):
        return {
            "count": 0,
            "sample": [],
            "summary": {},
            "message": "No matching employees found",
        }

    grouped = df.groupby(["Project_Complexity", "Project_Size"]).agg({
        "Project_Outcome": "count",
    }).reset_index()
    count = int(len(grouped))
    if count == 0:
        return {
            "count": 0,
            "sample": [],
            "summary": {},
            "message": "No matching employees found",
        }

    sample_df = safe_sample_df(grouped)

    return {
        "count": count,
        "sample": [_to_native(row) for row in sample_df.to_dict(orient="records")],
        "summary": {
            "total_projects": to_native_type(len(df)),
        },
    }


def project_success_failure_analysis(df):
    required = ["Project_Outcome", "Performance_Rating"]
    if not all(col in df.columns for col in required):
        return {
            "count": 0,
            "sample": [],
            "summary": {},
            "message": "No matching employees found",
        }

    outcomes = df["Project_Outcome"].fillna("").astype(str).str.lower()
    success_df = df[outcomes == "successful"]
    failure_df = df[outcomes == "failed"]
    count = int(len(df))
    if count == 0:
        return {
            "count": 0,
            "sample": [],
            "summary": {},
            "message": "No matching employees found",
        }

    sample_df = safe_sample_df(df)

    return {
        "count": count,
        "sample": [_to_native(row) for row in sample_df.to_dict(orient="records")],
        "summary": {
            "success_count": to_native_type(len(success_df)),
            "failure_count": to_native_type(len(failure_df)),
            "avg_success_performance": to_native_type(
                success_df["Performance_Rating"].mean()
            ),
            "avg_failure_performance": to_native_type(
                failure_df["Performance_Rating"].mean()
            ),
        },
    }


def project_success_model(df):
    required = ["Project_Outcome", "Performance_Rating"]
    if not all(col in df.columns for col in required):
        return {
            "count": 0,
            "sample": [],
            "summary": {},
            "message": "No matching employees found",
        }

    scored_df = df.copy()
    scored_df["is_success"] = scored_df["Project_Outcome"].fillna("").astype(str).str.lower().apply(
        lambda value: 1 if value == "successful" else 0
    )
    count = int(len(scored_df))
    if count == 0:
        return {
            "count": 0,
            "sample": [],
            "summary": {},
            "message": "No matching employees found",
        }

    success_rate = scored_df["is_success"].mean()
    sample_df = safe_sample_df(scored_df)

    summary = {
        "success_rate": to_native_type(success_rate),
    }

    skill_cols = [
        "Technical_Skills_Rating",
        "Communication_Skills_Rating",
        "Problem_Solving_Skills_Rating",
    ]
    available_skill_cols = [col for col in skill_cols if col in scored_df.columns]
    if available_skill_cols:
        scored_df["avg_skill_score"] = scored_df[available_skill_cols].mean(axis=1)

    success_df = scored_df[
        scored_df["Project_Outcome"].fillna("").astype(str).str.lower()
        == "successful"
    ]
    failure_df = scored_df[
        scored_df["Project_Outcome"].fillna("").astype(str).str.lower()
        == "failed"
    ]

    def build_group_summary(group_df):
        summary_data = {
            "avg_performance": to_native_type(
                group_df["Performance_Rating"].mean()
            ),
        }
        if "avg_skill_score" in group_df.columns:
            summary_data["avg_skill_score"] = to_native_type(
                group_df["avg_skill_score"].mean()
            )
        if "Project_Role" in group_df.columns:
            summary_data["role_distribution"] = _to_native(
                group_df["Project_Role"].value_counts(dropna=False).to_dict()
            )
        return summary_data

    summary["success"] = build_group_summary(success_df)
    summary["failure"] = build_group_summary(failure_df)

    return {
        "count": count,
        "sample": [_to_native(row) for row in sample_df.to_dict(orient="records")],
        "summary": summary,
    }


def project_role_analysis(df):
    required = ["Project_Role", "Performance_Rating", "Project_Outcome"]
    if not all(col in df.columns for col in required):
        return {
            "count": 0,
            "sample": [],
            "summary": {},
            "message": "No matching employees found",
        }

    grouped = df.groupby("Project_Role").agg({
        "Performance_Rating": "mean",
        "Project_Outcome": "count",
    }).reset_index()
    count = int(len(grouped))
    if count == 0:
        return {
            "count": 0,
            "sample": [],
            "summary": {},
            "message": "No matching employees found",
        }

    sample_df = safe_sample_df(grouped)

    return {
        "count": count,
        "sample": [_to_native(row) for row in sample_df.to_dict(orient="records")],
        "summary": {
            "roles": to_native_type(grouped["Project_Role"].nunique()),
        },
    }


def resignation_analysis(df):
    if "Employee_Resignation_Status" not in df.columns:
        return {
            "count": 0,
            "sample": [],
            "summary": {},
            "message": "No matching employees found",
        }

    status_series = df["Employee_Resignation_Status"].fillna("").astype(str)
    resigned_df = df[status_series.str.lower() == "yes"].copy()
    count = int(len(resigned_df))
    if count == 0:
        return {
            "count": 0,
            "sample": [],
            "summary": {},
            "message": "No matching employees found",
        }

    sample_df = safe_sample_df(resigned_df)

    summary = {}
    if "Employee_Engagement_Score" in resigned_df.columns:
        summary["avg_engagement"] = to_native_type(
            resigned_df["Employee_Engagement_Score"].mean()
        )
    if "Salary_Increase_%" in resigned_df.columns:
        summary["avg_salary_increase"] = to_native_type(
            resigned_df["Salary_Increase_%"].mean()
        )

    return {
        "count": count,
        "sample": [_to_native(row) for row in sample_df.to_dict(orient="records")],
        "summary": summary,
    }


def attrition_risk_score(df):
    required = ["Employee_Engagement_Score", "Salary_Increase_%", "Overtime"]
    if not all(col in df.columns for col in required):
        return {
            "count": 0,
            "sample": [],
            "summary": {},
            "message": "No matching employees found",
        }

    scored_df = df.copy()
    overtime_flags = scored_df["Overtime"].fillna("").astype(str).str.lower()
    scored_df["risk_score"] = (
        (10 - scored_df["Employee_Engagement_Score"]) * 0.4
        + (10 - scored_df["Salary_Increase_%"]) * 0.3
        + overtime_flags.apply(lambda value: 1 if value == "yes" else 0) * 0.3
    )

    threshold = scored_df["risk_score"].quantile(0.75)
    high_risk = scored_df[scored_df["risk_score"] >= threshold]
    count = int(len(high_risk))
    if count == 0:
        return {
            "count": 0,
            "sample": [],
            "summary": {},
            "message": "No matching employees found",
        }

    sample_df = safe_sample_df(high_risk)

    return {
        "count": count,
        "sample": [_to_native(row) for row in sample_df.to_dict(orient="records")],
        "summary": {
            "avg_risk_score": to_native_type(high_risk["risk_score"].mean())
        },
    }


def worklife_retention_analysis(df):
    required = ["Work_Life_Balance_Score", "Employee_Resignation_Status"]
    if not all(col in df.columns for col in required):
        return {
            "count": 0,
            "sample": [],
            "summary": {},
            "message": "No matching employees found",
        }

    base_cols = [
        "Employee_Resignation_Status",
        "Work_Life_Balance_Score",
    ]
    if "Employee_Engagement_Score" in df.columns:
        base_cols.append("Employee_Engagement_Score")
    if "Overtime" in df.columns:
        base_cols.append("Overtime")

    scoped = df[base_cols].dropna(subset=["Employee_Resignation_Status"])
    count = int(len(scoped))
    if count == 0:
        return {
            "count": 0,
            "sample": [],
            "summary": {},
            "message": "No matching employees found",
        }

    sample_df = safe_sample_df(scoped)

    summary = {}
    if "Work_Life_Balance_Score" in scoped.columns:
        grouped_worklife = scoped.groupby("Employee_Resignation_Status")[
            "Work_Life_Balance_Score"
        ].mean()
        summary["worklife_by_status"] = _to_native(grouped_worklife.to_dict())

    if "Employee_Engagement_Score" in scoped.columns:
        grouped_engagement = scoped.groupby("Employee_Resignation_Status")[
            "Employee_Engagement_Score"
        ].mean()
        summary["engagement_by_status"] = _to_native(grouped_engagement.to_dict())

    if "Overtime" in scoped.columns:
        overtime_flags = scoped["Overtime"].fillna("").astype(str).str.lower()
        scoped_with_flags = scoped.copy()
        scoped_with_flags["overtime_flag"] = overtime_flags == "yes"
        grouped_overtime = scoped_with_flags.groupby("Employee_Resignation_Status")[
            "overtime_flag"
        ].mean()
        summary["overtime_ratio_by_status"] = _to_native(grouped_overtime.to_dict())

    return {
        "count": count,
        "sample": [_to_native(row) for row in sample_df.to_dict(orient="records")],
        "summary": summary,
    }


def compensation_bonus_analysis(df):
    required = ["Salary_Increase_%", "Bonus_%", "Performance_Rating"]
    if not all(col in df.columns for col in required):
        return {
            "count": 0,
            "sample": [],
            "summary": {},
            "message": "No matching employees found",
        }

    df_valid = df[required].dropna()
    count = int(len(df_valid))
    if count == 0:
        return {
            "count": 0,
            "sample": [],
            "summary": {},
            "message": "No matching employees found",
        }

    correlations = df_valid.corr(numeric_only=True).to_dict()
    sample_df = safe_sample_df(df_valid)

    return {
        "count": count,
        "sample": [_to_native(row) for row in sample_df.to_dict(orient="records")],
        "summary": {
            "compensation_correlations": _to_native(correlations),
        },
    }


def benefits_impact_analysis(df):
    if "Benefits_Score" not in df.columns:
        return {
            "count": 0,
            "sample": [],
            "summary": {},
            "message": "No matching employees found",
        }

    agg_map = {"Employee_Resignation_Status": "count"}
    if "Job_Satisfaction_Score" in df.columns:
        agg_map["Job_Satisfaction_Score"] = "mean"

    grouped = df.groupby("Benefits_Score").agg(agg_map).reset_index()
    count = int(len(grouped))
    if count == 0:
        return {
            "count": 0,
            "sample": [],
            "summary": {},
            "message": "No matching employees found",
        }

    sample_df = safe_sample_df(grouped)

    return {
        "count": count,
        "sample": [_to_native(row) for row in sample_df.to_dict(orient="records")],
        "summary": {
            "benefits_levels": to_native_type(len(grouped))
        },
    }


def hiring_intelligence_analysis(df):
    required = ["Hiring_Source", "Time_to_Hire", "Recruitment_Cost"]
    if not all(col in df.columns for col in required):
        return {
            "count": 0,
            "sample": [],
            "summary": {},
            "message": "No matching employees found",
        }

    grouped = df.groupby("Hiring_Source").agg({
        "Time_to_Hire": "mean",
        "Recruitment_Cost": "mean",
    }).reset_index()
    count = int(len(df))
    if count == 0:
        return {
            "count": 0,
            "sample": [],
            "summary": {},
            "message": "No matching employees found",
        }

    summary = {
        "avg_time_to_hire_by_source": {
            row["Hiring_Source"]: to_native_type(row["Time_to_Hire"])
            for _, row in grouped.iterrows()
        },
        "avg_cost_by_source": {
            row["Hiring_Source"]: to_native_type(row["Recruitment_Cost"])
            for _, row in grouped.iterrows()
        },
    }

    if "Performance_Rating" in df.columns:
        perf = df.groupby("Hiring_Source")["Performance_Rating"].mean()
        summary["avg_performance_by_source"] = _to_native(perf.to_dict())

    if "Employee_Resignation_Status" in df.columns:
        resignation = df.groupby("Hiring_Source")["Employee_Resignation_Status"].apply(
            lambda values: (
                values.fillna("").astype(str).str.lower() == "yes"
            ).mean()
        )
        summary["resignation_rate_by_source"] = _to_native(resignation.to_dict())

    if "Job_Satisfaction_Score" in df.columns:
        satisfaction = df.groupby("Hiring_Source")["Job_Satisfaction_Score"].mean()
        summary["avg_satisfaction_by_source"] = _to_native(satisfaction.to_dict())

    sample_df = safe_sample_df(df)

    return {
        "count": count,
        "sample": [_to_native(row) for row in sample_df.to_dict(orient="records")],
        "summary": summary,
    }
