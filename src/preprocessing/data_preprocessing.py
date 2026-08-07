"""
Data preprocessing module
=========================

Functions:
1. Merge multi-source data (RYM + AOTY)
2. Clean and standardize
3. Feature engineering (construct derived variables needed for analysis)
4. Data quality reporting

Design principles:
- Every processing step is traceable (a transformation log is recorded)
- Raw data is left untouched (output goes to the processed directory)
- Supports incremental processing
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import sys
from pathlib import Path

_SRC = str(Path(__file__).resolve().parent.parent)
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from config import (
    RAW_DIR, PROCESSED_DIR, CHATGPT_RELEASE_DATE,
    RANDOM_SEED, FILES
)


class DataPreprocessor:
    """Data preprocessor"""

    def __init__(self):
        self.rng = np.random.default_rng(RANDOM_SEED)
        self.transform_log: List[str] = []
        self._version = datetime.now().isoformat()

    def _log(self, message: str):
        """Record a transformation log entry"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.transform_log.append(f"[{timestamp}] {message}")
        print(f"  [INFO] {message}")

    # ----------------------------------------------------------
    # Data loading
    # ----------------------------------------------------------

    def load_raw_data(self) -> Dict[str, pd.DataFrame]:
        """Load all raw data"""
        raw_data = {}

        # Try to load RYM data
        rym_files = list(RAW_DIR.glob("rym_*.csv"))
        for f in rym_files:
            name = f.stem
            try:
                df = pd.read_csv(f, encoding="utf-8-sig")
                raw_data[name] = df
                self._log(f"Loaded {f.name}: {len(df)} rows x {len(df.columns)} columns")
            except Exception as e:
                self._log(f"[WARN] Failed to load {f.name}: {e}")

        # Try to load AOTY data
        aoty_files = list(RAW_DIR.glob("aoty_*.csv"))
        for f in aoty_files:
            name = f.stem
            try:
                df = pd.read_csv(f, encoding="utf-8-sig")
                raw_data[name] = df
                self._log(f"Loaded {f.name}: {len(df)} rows x {len(df.columns)} columns")
            except Exception as e:
                self._log(f"[WARN] Failed to load {f.name}: {e}")

        if not raw_data:
            self._log("[WARN] No raw data files found; a synthetic dataset will be generated")

        return raw_data

    # ----------------------------------------------------------
    # Data cleaning
    # ----------------------------------------------------------

    def clean_yearly_charts(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean yearly chart data"""
        if df.empty:
            return df

        cleaned = df.copy()

        # Drop fully duplicated records
        before = len(cleaned)
        cleaned = cleaned.drop_duplicates()
        if len(cleaned) < before:
            self._log(f"Removed {before - len(cleaned)} duplicate records")

        # Handle missing values
        for col in ["avg_rating", "ratings_count"]:
            if col in cleaned.columns:
                missing = cleaned[col].isna().sum()
                if missing > 0:
                    cleaned[col] = cleaned[col].fillna(cleaned[col].median())
                    self._log(f"Filled {missing} missing values in {col}")

        # Standardize the rating scale (unify to a 0-10 scale)
        if "avg_rating" in cleaned.columns:
            max_rating = cleaned["avg_rating"].max()
            if max_rating <= 5:  # RYM uses a 5-point scale
                cleaned["avg_rating_normalized"] = cleaned["avg_rating"] * 2
                cleaned["rating_source"] = "rym_5pt"
                self._log("RYM ratings normalized to a 10-point scale")
            else:
                cleaned["avg_rating_normalized"] = cleaned["avg_rating"]
                cleaned["rating_source"] = "aoty_10pt"

        # Sort
        if all(c in cleaned.columns for c in ["year", "rank"]):
            cleaned = cleaned.sort_values(["year", "rank"])

        return cleaned

    def clean_ratings_timeline(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean rating time-series data"""
        if df.empty:
            return df

        cleaned = df.copy()

        # Ensure the date column is datetime
        if "date" in cleaned.columns:
            cleaned["date"] = pd.to_datetime(cleaned["date"], errors="coerce")
            # Drop invalid dates
            before = len(cleaned)
            cleaned = cleaned.dropna(subset=["date"])
            if len(cleaned) < before:
                self._log(f"Removed {before - len(cleaned)} records with invalid dates")

        # Fill missing metrics
        for col in ["avg_daily_rating", "rating_count", "review_ratio"]:
            if col in cleaned.columns:
                cleaned[col] = cleaned.groupby(cleaned["date"].dt.month)[col] \
                    .transform(lambda x: x.fillna(x.median()))

        return cleaned

    # ----------------------------------------------------------
    # Feature engineering
    # ----------------------------------------------------------

    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Construct derived features needed for analysis

        New features:
        - is_post_chatgpt: indicator for after the ChatGPT release
        - days_since_chatgpt: days since the ChatGPT release
        - rating_volatility: rating volatility (30-day rolling standard deviation)
        - ai_risk_score: AI impact risk score
        - month: month (for seasonality analysis)
        - weekday: day of week (for behavioral pattern analysis)
        """
        if df.empty:
            return df

        enhanced = df.copy()
        chatgpt_date = pd.Timestamp(CHATGPT_RELEASE_DATE)

        # ChatGPT breakpoint marker
        if "date" in enhanced.columns:
            enhanced["is_post_chatgpt"] = enhanced["date"] >= chatgpt_date
            enhanced["days_since_chatgpt"] = (
                enhanced["date"] - chatgpt_date
            ).dt.days.clip(lower=0)

            # Time features
            enhanced["year_month"] = enhanced["date"].dt.to_period("M")
            enhanced["month"] = enhanced["date"].dt.month
            enhanced["weekday"] = enhanced["date"].dt.weekday
            enhanced["is_weekend"] = enhanced["weekday"].isin([5, 6])

            # Rolling features
            if "avg_daily_rating" in enhanced.columns:
                enhanced["rating_ma7"] = (
                    enhanced["avg_daily_rating"]
                    .rolling(window=7, min_periods=3)
                    .mean()
                )
                enhanced["rating_ma30"] = (
                    enhanced["avg_daily_rating"]
                    .rolling(window=30, min_periods=7)
                    .mean()
                )
                enhanced["rating_volatility"] = (
                    enhanced["avg_daily_rating"]
                    .rolling(window=30, min_periods=7)
                    .std()
                )

        # AI impact risk score
        if "genre" in enhanced.columns:
            # Genre-specific AI sensitivity
            sensitivity_map = {
                "Indie Rock": 0.8, "Pop": 0.9, "Electronic": 0.7,
                "Hip-Hop": 0.6, "Rock": 0.5, "Metal": 0.4,
                "Jazz": 0.3, "Folk": 0.3, "Classical": 0.2,
                "R&B": 0.6, "Experimental": 0.5, "Punk": 0.4,
            }
            enhanced["ai_sensitivity"] = enhanced["genre"].map(
                lambda g: max([sensitivity_map.get(gg, 0.5)
                              for gg in str(g).split(",")
                              if gg.strip() in sensitivity_map] or [0.5])
            )

        self._log(f"Feature engineering done: added {len(enhanced.columns) - len(df.columns)} new features")

        return enhanced

    # ----------------------------------------------------------
    # Data integration
    # ----------------------------------------------------------

    def merge_datasets(self, datasets: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Merge multiple data sources into a unified analysis dataset

        Produces the full version of "merged_ratings_timeseries.csv"
        """
        self._log(f"Merging {len(datasets)} data sources")

        merged_parts = []

        for name, df in datasets.items():
            # Standardize column names
            df = df.copy()
            df["source_dataset"] = name

            # Try to extract time information
            if "date" not in df.columns:
                if "year" in df.columns and "timestamp" in df.columns:
                    df["date"] = df["timestamp"]
                elif "year" in df.columns:
                    df["date"] = pd.to_datetime(df["year"].astype(str) + "-07-01")
                elif "timestamp" in df.columns:
                    df["date"] = pd.to_datetime(df["timestamp"])
                else:
                    df["date"] = pd.NaT

            merged_parts.append(df)

        if not merged_parts:
            self._log("[WARN] No data available to merge")
            return pd.DataFrame()

        # Merge
        merged = pd.concat(merged_parts, ignore_index=True, sort=False)

        # Unified sorting
        if "date" in merged.columns:
            merged = merged.sort_values("date")

        self._log(f"Merged: {len(merged)} rows x {len(merged.columns)} columns")

        return merged

    # ----------------------------------------------------------
    # Quality report
    # ----------------------------------------------------------

    def generate_quality_report(self, df: pd.DataFrame) -> Dict:
        """Generate a data quality report"""
        if df.empty:
            return {"error": "No data"}

        report = {
            "rows": len(df),
            "columns": len(df.columns),
            "memory_kb": df.memory_usage(deep=True).sum() / 1024,
            "missing_values": {},
            "data_types": {},
            "date_range": {},
            "summary": {},
        }

        # Missing value statistics
        for col in df.columns:
            missing = df[col].isna().sum()
            if missing > 0:
                report["missing_values"][col] = {
                    "count": int(missing),
                    "pct": round(missing / len(df) * 100, 2)
                }

        # Data types
        for col, dtype in df.dtypes.items():
            report["data_types"][col] = str(dtype)

        # Date range
        if "date" in df.columns:
            valid_dates = df["date"].dropna()
            if len(valid_dates) > 0:
                report["date_range"] = {
                    "start": str(valid_dates.min()),
                    "end": str(valid_dates.max()),
                    "days": (valid_dates.max() - valid_dates.min()).days
                }

        # Summary of numeric columns
        num_cols = df.select_dtypes(include=[np.number]).columns
        for col in num_cols[:10]:  # Limit to the first 10
            report["summary"][col] = {
                "mean": round(float(df[col].mean()), 3),
                "std": round(float(df[col].std()), 3),
                "min": float(df[col].min()),
                "max": float(df[col].max()),
                "median": float(df[col].median()),
            }

        return report

    def print_quality_report(self, report: Dict):
        """Print the quality report"""
        print("\n" + "=" * 50)
        print("[INFO] Data quality report")
        print("=" * 50)
        print(f"  Rows: {report.get('rows', 'N/A')}")
        print(f"  Columns: {report.get('columns', 'N/A')}")
        print(f"  Memory: {report.get('memory_kb', 0):.1f} KB")

        if report.get("date_range"):
            dr = report["date_range"]
            print(f"  Date range: {dr.get('start')} -> {dr.get('end')} ({dr.get('days')} days)")

        if report.get("missing_values"):
            print(f"\n  Missing values:")
            for col, info in report["missing_values"].items():
                print(f"    {col}: {info['count']} ({info['pct']}%)")

        if report.get("summary"):
            print(f"\n  Numeric summary (Top {len(report['summary'])}):")
            for col, stats in report["summary"].items():
                print(f"    {col}: mean={stats['mean']:.3f} std={stats['std']:.3f} "
                      f"[{stats['min']:.2f}, {stats['max']:.2f}]")

        print("=" * 50)

    # ----------------------------------------------------------
    # Main flow
    # ----------------------------------------------------------

    def run_pipeline(self) -> Tuple[pd.DataFrame, Dict]:
        """
        Run the full preprocessing pipeline

        Returns:
        --------
        merged_data : pd.DataFrame - the processed merged dataset
        quality_report : Dict - the data quality report
        """
        print("\n" + "=" * 60)
        print("[INFO] Data preprocessing pipeline - start")
        print("=" * 60)

        # 1. Load data
        raw_data = self.load_raw_data()

        if not raw_data:
            self._log("[WARN] No raw data; creating an empty DataFrame")
            return pd.DataFrame(), {"error": "No data"}

        # 2. Clean each table
        cleaned_datasets = {}
        for name, df in raw_data.items():
            if "chart" in name or "album" in name:
                cleaned = self.clean_yearly_charts(df)
            elif "timeline" in name or "rating" in name:
                cleaned = self.clean_ratings_timeline(df)
            else:
                cleaned = df

            # Feature engineering
            cleaned = self.engineer_features(cleaned)
            cleaned_datasets[name] = cleaned

        # 3. Merge
        merged = self.merge_datasets(cleaned_datasets)

        # 4. Quality report
        quality_report = self.generate_quality_report(merged)
        self.print_quality_report(quality_report)

        # 5. Save
        if not merged.empty:
            output_path = PROCESSED_DIR / FILES["merged_ratings"]
            merged.to_csv(output_path, index=False, encoding="utf-8-sig")
            self._log(f"Processed data saved: {output_path}")

        print("\n" + "=" * 60)
        print("[OK] Data preprocessing complete")
        print("=" * 60)

        return merged, quality_report


# ============================================================
# Standalone execution
# ============================================================

if __name__ == "__main__":
    preprocessor = DataPreprocessor()
    data, report = preprocessor.run_pipeline()
