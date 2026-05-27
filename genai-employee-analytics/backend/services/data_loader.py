import os

import pandas as pd


def load_data(file_path="data/employee_data.csv"):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.abspath(os.path.join(base_dir, "..", file_path))
    try:
        return pd.read_csv(data_path)
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Data file not found at: {data_path}") from exc
