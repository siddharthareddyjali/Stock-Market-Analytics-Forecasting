from __future__ import annotations

import numpy as np
import pandas as pd


class PreprocessingService:
    @staticmethod
    def ensure_numeric(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
        clean = frame.copy()
        for column in columns:
            if column in clean.columns:
                clean[column] = pd.to_numeric(clean[column], errors="coerce")
        return clean

    @staticmethod
    def remove_invalid_rows(frame: pd.DataFrame) -> pd.DataFrame:
        return frame.dropna().copy()

    @staticmethod
    def prepare_price_frame(frame: pd.DataFrame) -> pd.DataFrame:
        if frame is None or frame.empty:
            raise ValueError("Price dataset is empty.")
        clean = frame.copy()
        clean.index = pd.to_datetime(clean.index)
        clean = clean.sort_index()
        clean = clean[~clean.index.duplicated(keep="last")]
        clean = clean.replace([np.inf, -np.inf], np.nan)
        clean = clean.ffill().bfill()
        return clean
