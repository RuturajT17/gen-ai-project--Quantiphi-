from config import NUMERIC_COLUMNS, SOFT_SKILL_COLUMN_MAP


def clean_data(df):
    df = df.drop_duplicates()
    existing_numeric = [col for col in NUMERIC_COLUMNS if col in df.columns]
    df[existing_numeric] = df[existing_numeric].fillna(
        df[existing_numeric].mean()
    )
    return df


def add_features(df):
    avg_skill_cols = [
        "Technical_Skills_Rating",
        "Communication_Skills_Rating",
        "Problem_Solving_Skills_Rating",
    ]
    missing_avg = [col for col in avg_skill_cols if col not in df.columns]
    if missing_avg:
        raise ValueError(
            f"Missing columns for avg_skill_score: {missing_avg}"
        )

    resolved_soft = []
    for options in SOFT_SKILL_COLUMN_MAP.values():
        found = next((col for col in options if col in df.columns), None)
        if found:
            resolved_soft.append(found)
    if "Teamwork_Skills_Rating" in df.columns:
        resolved_soft.append("Teamwork_Skills_Rating")

    df = df.copy()
    df["avg_skill_score"] = (
        df["Technical_Skills_Rating"]
        + df["Communication_Skills_Rating"]
        + df["Problem_Solving_Skills_Rating"]
    ) / 3
    if resolved_soft:
        df["soft_skill_score"] = df[resolved_soft].mean(axis=1)
    else:
        df["soft_skill_score"] = None
    return df
