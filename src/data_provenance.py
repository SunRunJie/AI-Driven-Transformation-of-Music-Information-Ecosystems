"""Data-provenance helpers shared by preprocessing, analysis, and figures."""

from __future__ import annotations

from typing import Dict, Tuple

import pandas as pd


AUDIT_DATASETS = {
    "aoty_collection_events",
    "rym_collection_events",
}

KNOWN_SYNTHETIC_DATASETS = {
    "aoty_album_ratings",
    "aoty_genre_trends_2010_2026",
    "rym_forum_ai_discussions",
    "rym_ratings_timeline",
    "rym_yearly_charts_2000_2026",
}

EMPIRICAL_SOURCES = {
    "aoty_web",
    "aoty_text_snapshot",
    "aoty_kaggle_archive",
    "aoty_kaggle_snapshot",
    "rym_web",
    "rym_kaggle_snapshot",
}


def _as_bool(series: pd.Series) -> pd.Series:
    return series.astype(str).str.strip().str.lower().isin({"true", "1", "yes"})


def assess_dataframe(df: pd.DataFrame, dataset_name: str) -> Dict:
    """Return an auditable provenance summary without mutating the input."""
    total = int(len(df))
    if dataset_name in AUDIT_DATASETS:
        return {
            "dataset": dataset_name,
            "rows_total": total,
            "rows_empirical": 0,
            "rows_synthetic": 0,
            "rows_unknown": 0,
            "status": "audit_only",
            "reason": "collection event log; not an observation table",
        }

    explicit_empirical = False
    if "is_synthetic" in df.columns and total:
        explicit_empirical |= bool((~_as_bool(df["is_synthetic"])).any())
    if "source" in df.columns and total:
        explicit_empirical |= bool(
            df["source"].fillna("").astype(str).str.strip().str.lower().isin(EMPIRICAL_SOURCES).any()
        )

    if dataset_name in KNOWN_SYNTHETIC_DATASETS and not explicit_empirical:
        return {
            "dataset": dataset_name,
            "rows_total": total,
            "rows_empirical": 0,
            "rows_synthetic": total,
            "rows_unknown": 0,
            "status": "synthetic_only",
            "reason": "legacy generator output recorded in the repository",
        }

    synthetic_mask = pd.Series(False, index=df.index)
    empirical_mask = pd.Series(False, index=df.index)

    if "is_synthetic" in df.columns:
        synthetic_mask |= _as_bool(df["is_synthetic"])
        empirical_mask |= ~_as_bool(df["is_synthetic"])

    if "source" in df.columns:
        source = df["source"].fillna("").astype(str).str.strip().str.lower()
        synthetic_mask |= source.eq("synthetic")
        empirical_mask |= source.isin(EMPIRICAL_SOURCES)

    empirical_mask &= ~synthetic_mask
    unknown_mask = ~(synthetic_mask | empirical_mask)
    empirical_rows = int(empirical_mask.sum())
    synthetic_rows = int(synthetic_mask.sum())
    unknown_rows = int(unknown_mask.sum())

    if total == 0:
        status = "empty"
        reason = "dataset contains no rows"
    elif empirical_rows == total:
        status = "empirical"
        reason = "all rows carry an explicit empirical source marker"
    elif empirical_rows > 0:
        status = "mixed"
        reason = "empirical rows coexist with synthetic or unclassified rows"
    elif synthetic_rows == total:
        status = "synthetic_only"
        reason = "all rows are explicitly synthetic"
    else:
        status = "unknown"
        reason = "rows lack sufficient provenance metadata"

    return {
        "dataset": dataset_name,
        "rows_total": total,
        "rows_empirical": empirical_rows,
        "rows_synthetic": synthetic_rows,
        "rows_unknown": unknown_rows,
        "status": status,
        "reason": reason,
    }


def empirical_rows(df: pd.DataFrame, dataset_name: str) -> Tuple[pd.DataFrame, Dict]:
    """Return only explicitly empirical rows plus the provenance assessment."""
    audit = assess_dataframe(df, dataset_name)
    if audit["status"] in {"audit_only", "synthetic_only", "unknown", "empty"}:
        return df.iloc[0:0].copy(), audit

    mask = pd.Series(False, index=df.index)
    if "is_synthetic" in df.columns:
        mask |= ~_as_bool(df["is_synthetic"])
    if "source" in df.columns:
        source = df["source"].fillna("").astype(str).str.strip().str.lower()
        mask |= source.isin(EMPIRICAL_SOURCES)
        mask &= ~source.eq("synthetic")

    result = df.loc[mask].copy()
    result["provenance_status"] = "empirical"
    return result, audit


def dataframe_label(df: pd.DataFrame) -> str:
    """Short figure/report label for an in-memory table."""
    if df is None or df.empty:
        return "no observations"
    if "provenance_status" in df.columns:
        statuses = set(df["provenance_status"].dropna().astype(str).str.lower())
        if statuses == {"empirical"}:
            return "empirical observations"
        if statuses == {"third_party_observed_archive"}:
            return "third-party observed archive"
    if "is_synthetic" in df.columns and _as_bool(df["is_synthetic"]).any():
        return "illustrative synthetic data"
    if "source_dataset" in df.columns and df["source_dataset"].astype(str).str.contains(
        "synthetic|simulation|illustrative", case=False, regex=True
    ).any():
        return "illustrative synthetic data"
    return "provenance not established"
