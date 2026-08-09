"""Analysis of documented third-party AOTY and RYM data archives.

The archives are cross-sectional snapshots, so this module supports
descriptive and cross-platform comparisons. It does not turn release year
into a platform time series or use the snapshots for causal break tests.
"""

from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Dict

import numpy as np
import pandas as pd

_SRC = str(Path(__file__).resolve().parent.parent)
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from config import EXTERNAL_DIR, PROCESSED_DIR


AOTY_HISTORY_PATH = EXTERNAL_DIR / "aoty_metacritic_30000" / "album_ratings.csv"
AOTY_TOP_PATH = EXTERNAL_DIR / "aoty_top5000" / "aoty.csv"
RYM_TOP_PATH = EXTERNAL_DIR / "rym_top5000" / "rym_clean1.csv"


def _normalise_name(value: object) -> str:
    ascii_value = unicodedata.normalize("NFKD", str(value)).encode(
        "ascii", "ignore"
    ).decode("ascii")
    return re.sub(r"[^a-z0-9]+", "", ascii_value.lower())


def _album_key(artist: object, title: object, year: object) -> str:
    if pd.isna(year):
        return ""
    return f"{_normalise_name(artist)}|{_normalise_name(title)}|{int(year)}"


def _gini(values: pd.Series) -> float:
    clean = np.sort(pd.to_numeric(values, errors="coerce").dropna().to_numpy())
    clean = clean[clean >= 0]
    if len(clean) == 0 or clean.sum() == 0:
        return float("nan")
    ranks = np.arange(1, len(clean) + 1)
    return float(
        2 * np.sum(ranks * clean) / (len(clean) * clean.sum())
        - (len(clean) + 1) / len(clean)
    )


def _load_aoty_history() -> pd.DataFrame:
    df = pd.read_csv(AOTY_HISTORY_PATH)
    df = df.rename(
        columns={
            "Artist": "artist",
            "Title": "title",
            "Release Year": "release_year",
            "Genre": "genres",
            "AOTY User Score": "aoty_user_score",
            "AOTY User Reviews": "aoty_user_reviews",
            "AOTY Critic Score": "aoty_critic_score",
            "AOTY Critic Reviews": "aoty_critic_reviews",
        }
    )
    numeric = [
        "release_year", "aoty_user_score", "aoty_user_reviews",
        "aoty_critic_score", "aoty_critic_reviews",
    ]
    for column in numeric:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    df["album_key"] = [
        _album_key(artist, title, year)
        for artist, title, year in zip(df["artist"], df["title"], df["release_year"])
    ]
    df["source"] = "aoty_kaggle_archive"
    df["source_snapshot_date"] = "2020-10"
    df["is_synthetic"] = False
    df["provenance_status"] = "third_party_observed_archive"
    return df


def _load_aoty_top() -> pd.DataFrame:
    df = pd.read_csv(AOTY_TOP_PATH)
    df["rating_count"] = pd.to_numeric(
        df["rating_count"].astype(str).str.replace(r"[^0-9]", "", regex=True),
        errors="coerce",
    )
    df["release_year"] = pd.to_datetime(df["release_date"], errors="coerce").dt.year
    df["album_key"] = [
        _album_key(artist, title, year)
        for artist, title, year in zip(df["artist"], df["title"], df["release_year"])
    ]
    df["source"] = "aoty_kaggle_snapshot"
    df["source_snapshot_date"] = "2024-10-20"
    df["is_synthetic"] = False
    df["provenance_status"] = "third_party_observed_archive"
    return df


def _load_rym_top() -> pd.DataFrame:
    df = pd.read_csv(RYM_TOP_PATH)
    df["release_year"] = pd.to_datetime(df["release_date"], errors="coerce").dt.year
    df["album_key"] = [
        _album_key(artist, title, year)
        for artist, title, year in zip(
            df["artist_name"], df["release_name"], df["release_year"]
        )
    ]
    df["review_share"] = np.where(
        df["rating_count"] > 0,
        df["review_count"] / df["rating_count"],
        np.nan,
    )
    df["source"] = "rym_kaggle_snapshot"
    df["source_snapshot_date"] = "2022-03-11"
    df["is_synthetic"] = False
    df["provenance_status"] = "third_party_observed_archive"
    return df


def _cross_platform_matches(
    aoty_history: pd.DataFrame, rym_top: pd.DataFrame
) -> pd.DataFrame:
    aoty = aoty_history[
        [
            "album_key", "artist", "title", "release_year",
            "aoty_user_score", "aoty_critic_score",
        ]
    ].dropna(subset=["album_key", "aoty_user_score"])
    rym = rym_top[
        [
            "album_key", "artist_name", "release_name", "avg_rating",
            "rating_count", "review_count",
        ]
    ].dropna(subset=["album_key", "avg_rating"])
    matched = aoty.merge(rym, on="album_key", how="inner")
    matched = matched.drop_duplicates("album_key").copy()
    matched["aoty_user_score_5"] = matched["aoty_user_score"] / 20
    matched["aoty_minus_rym"] = (
        matched["aoty_user_score_5"] - matched["avg_rating"]
    )
    return matched


def _genre_summary(
    aoty_top: pd.DataFrame, rym_top: pd.DataFrame, n_genres: int = 12
) -> pd.DataFrame:
    aoty = aoty_top.assign(genre=aoty_top["genres"].fillna("").str.split(", ")).explode("genre")
    aoty = aoty[aoty["genre"].ne("")]
    aoty_grouped = aoty.groupby("genre").agg(
        aoty_albums=("album_key", "nunique"),
        aoty_median_score=("user_score", lambda x: x.median() / 20),
        aoty_median_ratings=("rating_count", "median"),
    )

    rym = rym_top.assign(
        genre=rym_top["primary_genres"].fillna("").str.split(", ")
    ).explode("genre")
    rym = rym[rym["genre"].ne("")]
    rym_grouped = rym.groupby("genre").agg(
        rym_albums=("album_key", "nunique"),
        rym_median_score=("avg_rating", "median"),
        rym_median_ratings=("rating_count", "median"),
        rym_median_review_share=("review_share", "median"),
    )

    common = aoty_grouped.join(rym_grouped, how="inner")
    common["minimum_platform_count"] = common[
        ["aoty_albums", "rym_albums"]
    ].min(axis=1)
    common = common.sort_values(
        ["minimum_platform_count", "aoty_albums", "rym_albums"],
        ascending=False,
    ).head(n_genres)
    return common.reset_index()


def _summary(
    aoty_history: pd.DataFrame,
    aoty_top: pd.DataFrame,
    rym_top: pd.DataFrame,
    matched: pd.DataFrame,
) -> Dict:
    critic_user = aoty_history.dropna(
        subset=["aoty_user_score", "aoty_critic_score"]
    )
    difference = matched["aoty_minus_rym"]
    return {
        "sources": {
            "aoty_history_rows": int(len(aoty_history)),
            "aoty_top5000_rows": int(len(aoty_top)),
            "rym_top5000_rows": int(len(rym_top)),
        },
        "aoty_critic_user": {
            "n": int(len(critic_user)),
            "pearson_r": float(
                critic_user[["aoty_user_score", "aoty_critic_score"]]
                .corr().iloc[0, 1]
            ),
            "spearman_r": float(
                critic_user[["aoty_user_score", "aoty_critic_score"]]
                .corr(method="spearman").iloc[0, 1]
            ),
            "mean_absolute_gap_points": float(
                (critic_user["aoty_user_score"] - critic_user["aoty_critic_score"])
                .abs().mean()
            ),
        },
        "cross_platform": {
            "exact_matches": int(len(matched)),
            "pearson_r": float(
                matched[["aoty_user_score_5", "avg_rating"]].corr().iloc[0, 1]
            ),
            "spearman_r": float(
                matched[["aoty_user_score_5", "avg_rating"]]
                .corr(method="spearman").iloc[0, 1]
            ),
            "mean_aoty_minus_rym_5_point": float(difference.mean()),
            "median_aoty_minus_rym_5_point": float(difference.median()),
            "share_within_half_point": float((difference.abs() <= 0.5).mean()),
        },
        "attention": {
            "aoty_top5000_total_ratings": int(aoty_top["rating_count"].sum()),
            "aoty_top5000_median_ratings": float(aoty_top["rating_count"].median()),
            "aoty_top_one_percent_share": float(
                aoty_top.nlargest(50, "rating_count")["rating_count"].sum()
                / aoty_top["rating_count"].sum()
            ),
            "aoty_rating_count_gini": _gini(aoty_top["rating_count"]),
            "rym_top5000_total_ratings": int(rym_top["rating_count"].sum()),
            "rym_top5000_total_reviews": int(rym_top["review_count"].sum()),
            "rym_top5000_median_ratings": float(rym_top["rating_count"].median()),
            "rym_median_review_share": float(rym_top["review_share"].median()),
            "rym_top_one_percent_share": float(
                rym_top.nlargest(50, "rating_count")["rating_count"].sum()
                / rym_top["rating_count"].sum()
            ),
            "rym_rating_count_gini": _gini(rym_top["rating_count"]),
        },
    }


def load_observed_archives(export: bool = True) -> Dict:
    """Load, standardise, match, and summarise the three local archives."""
    required = [AOTY_HISTORY_PATH, AOTY_TOP_PATH, RYM_TOP_PATH]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing external archive files: " + ", ".join(missing))

    aoty_history = _load_aoty_history()
    aoty_top = _load_aoty_top()
    rym_top = _load_rym_top()
    matched = _cross_platform_matches(aoty_history, rym_top)
    genre_summary = _genre_summary(aoty_top, rym_top)
    summary = _summary(aoty_history, aoty_top, rym_top, matched)

    result = {
        "aoty_history": aoty_history,
        "aoty_top5000": aoty_top,
        "rym_top5000": rym_top,
        "cross_platform_matches": matched,
        "genre_summary": genre_summary,
        "summary": summary,
    }
    if export:
        PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
        matched.to_csv(
            PROCESSED_DIR / "cross_platform_exact_matches.csv",
            index=False,
            encoding="utf-8-sig",
        )
        genre_summary.to_csv(
            PROCESSED_DIR / "observed_genre_summary.csv",
            index=False,
            encoding="utf-8-sig",
        )
        with open(
            PROCESSED_DIR / "observed_archive_summary.json", "w", encoding="utf-8"
        ) as handle:
            json.dump(summary, handle, ensure_ascii=False, indent=2)
    return result


if __name__ == "__main__":
    loaded = load_observed_archives(export=True)
    print(json.dumps(loaded["summary"], indent=2))
