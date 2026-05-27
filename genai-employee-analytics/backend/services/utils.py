import numpy as np
import pandas as pd

from config import REQUIRED_COLUMNS, SAMPLE_SIZE


def validate_dataframe(df):
    if df.empty:
        raise ValueError("Dataframe is empty after loading and preprocessing.")

    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def to_native_type(value):
    if pd.isna(value):
        return None
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    return value


def safe_sample_df(df, max_rows=None):
    if max_rows is None:
        max_rows = SAMPLE_SIZE
    if df.empty:
        return df.copy()
    sample_size = min(len(df), max_rows)
    return df.sample(n=sample_size, random_state=42).copy()
