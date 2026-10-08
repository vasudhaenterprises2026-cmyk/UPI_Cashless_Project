"""Load the synthetic demonstration dataset."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.config import DATA_DIR, DATA_SOURCE_LABEL, RAW_CSV_NAME
from src.generate_sample_data import write_csv


def data_path() -> Path:
    return DATA_DIR / RAW_CSV_NAME


def load_raw_dataset() -> pd.DataFrame:
    path = data_path()
    if not path.exists():
        write_csv(path)
    df = pd.read_csv(path)
    df["data_source"] = DATA_SOURCE_LABEL
    if "record_type" not in df.columns:
        df["record_type"] = "SYNTHETIC / DEMONSTRATION — not a real respondent"
    return df
