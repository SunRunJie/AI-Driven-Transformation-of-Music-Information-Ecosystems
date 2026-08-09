"""
Time series structural break analysis
======================================

Core research question:
  Did the rating patterns on RYM/AOTY undergo a statistically
  significant structural change around the release of ChatGPT
  (November 2022)?

Analytical methods:
  1. CUSUM test - detects whether a series contains a statistically significant structural change
  2. Welch mean test - compares pre/post means around a specified break date
  3. Chow test - compares pooled vs split linear regressions around a specified break date
  4. Bai-Perron-style dynamic programming - automatically detects multiple linear break points
  4. Rolling statistics - tracks the dynamic evolution of key metrics

Testable hypotheses:
  H1: The share of low-quality ratings rises significantly after the ChatGPT release
  H2: The share of high-quality in-depth reviews declines over the same period
  H3: The statistical properties of the rating distribution (mean, variance, skewness) undergo a structural change
  H4: The rating behavior gap between new and old users widens

Data serves the logic:
  Rather than simply "plotting the trend", we run statistical tests
  on the research hypotheses.
"""

import sys
import warnings
from pathlib import Path
from typing import Dict, List, Optional, Tuple

_SRC = str(Path(__file__).resolve().parent.parent)
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

import numpy as np
import pandas as pd
from scipy import stats
from scipy.ndimage import gaussian_filter1d

from config import CHATGPT_RELEASE_DATE, ROLLING_WINDOW, CUSUM_THRESHOLD, RANDOM_SEED
from data_provenance import dataframe_label

warnings.filterwarnings("ignore", category=FutureWarning)


# ============================================================
# Structural break analyzer
# ============================================================

class StructuralBreakAnalyzer:
    """
    Structural break analyzer

    Performs systematic break point detection on rating time series,
    testing whether the AI shock (ChatGPT release) is a statistically
    significant structural change point.
    """

    def __init__(self, data: pd.DataFrame):
        """
        Parameters:
        -----------
        data : pd.DataFrame
            Must contain a 'date' column and at least one metric column
        """
        self.data = data.sort_values("date").reset_index(drop=True)
        self.dates = self.data["date"]
        self.n = len(self.data)
        self.rng = np.random.default_rng(RANDOM_SEED)

        # Auto-detect metric columns (excluding date and metadata columns)
        self.metric_columns = [
            col for col in self.data.columns
            if col not in ["date", "album_id", "source_dataset",
                          "is_synthetic", "collection_date",
                          "year_month", "month", "weekday", "is_weekend",
                          "source"]
            and self.data[col].dtype in [np.float64, np.int64, np.float32, np.int32]
            and self.data[col].nunique() > 5  # Need enough unique values
        ]

        print(f"  Analyzer initialized: {self.n} time points, {len(self.metric_columns)} metrics")

    # ----------------------------------------------------------
    # CUSUM test
    # ----------------------------------------------------------

    def cusum_test(self, metric: np.ndarray,
                   threshold: float = CUSUM_THRESHOLD) -> Dict:
        """
        CUSUM test - detects whether a series contains a structural change

        Principle:
          Cumulative deviation = Sum(observed - expected) / (std * sqrt(n))
          When the cumulative deviation exceeds the threshold, a structural change is indicated

        Parameters:
        -----------
        metric : np.ndarray - time series to test
        threshold : float - CUSUM test threshold (default 1.5)

        Returns:
        --------
        dict - test results
        """
        n = len(metric)
        if n < 10:
            return {"has_break": False, "error": "series too short"}

        # Detrend (using linear regression residuals)
        x = np.arange(n)
        slope, intercept, _, _, _ = stats.linregress(x, metric)
        detrended = metric - (slope * x + intercept)

        # Compute cumulative deviation
        mean_val = np.mean(detrended)
        std_val = np.std(detrended)

        if std_val == 0:
            return {"has_break": False, "error": "zero-variance series"}

        cumsum = np.cumsum(detrended - mean_val) / (std_val * np.sqrt(n))

        # Detection
        max_cusum = np.max(np.abs(cumsum))
        break_idx = int(np.argmax(np.abs(cumsum)))

        # Bootstrap test for significance
        n_bootstrap = 1000
        bootstrap_max = np.zeros(n_bootstrap)
        for b in range(n_bootstrap):
            # Permute the series
            perm = self.rng.permutation(detrended)
            boot_cumsum = np.cumsum(perm - np.mean(perm)) / (np.std(perm) * np.sqrt(n))
            bootstrap_max[b] = np.max(np.abs(boot_cumsum))

        p_value = np.mean(bootstrap_max >= max_cusum)

        return {
            "has_break": bool(max_cusum > threshold),
            "break_point_idx": break_idx,
            "break_point_date": str(self.dates.iloc[min(break_idx, self.n - 1)]),
            "cusum_statistic": float(max_cusum),
            "cusum_series": cumsum.tolist(),
            "threshold": threshold,
            "p_value": float(p_value),
            "significant": bool(p_value < 0.05),
        }

    # ----------------------------------------------------------
    # Welch mean test and Chow test
    # ----------------------------------------------------------

    @staticmethod
    def _ols_sse(y: np.ndarray, x: Optional[np.ndarray] = None) -> Tuple[float, int]:
        """Return residual sum of squares and parameter count for OLS."""
        y = np.asarray(y, dtype=float)
        if x is None:
            x = np.arange(len(y), dtype=float)
        x = np.asarray(x, dtype=float)
        design = np.column_stack([np.ones(len(y)), x])
        beta, *_ = np.linalg.lstsq(design, y, rcond=None)
        residuals = y - design @ beta
        return float(np.sum(residuals ** 2)), design.shape[1]

    def welch_mean_test(self, metric: np.ndarray,
                        break_date: str = CHATGPT_RELEASE_DATE) -> Dict:
        """
        Welch mean test - tests for a pre/post mean difference.

        Parameters:
        -----------
        metric : np.ndarray - time series to test
        break_date : str - assumed break point date

        Returns:
        --------
        dict - test results (including effect size)
        """
        if self.n < 20:
            return {"error": "insufficient sample size"}

        # Find the break point position
        break_idx = self.data[self.data["date"] >= break_date].index
        if len(break_idx) == 0:
            return {"error": f"break date {break_date} is out of the data range"}
        break_idx = int(break_idx[0])

        # Split
        y1 = metric[:break_idx]
        y2 = metric[break_idx:]

        n1, n2 = len(y1), len(y2)
        if n1 < 5 or n2 < 5:
            return {"error": "insufficient sample size on one side of the break point"}

        # Independent samples t-test (Welch's t-test, does not assume equal variances)
        t_stat, p_value = stats.ttest_ind(y1, y2, equal_var=False)

        # Cohen's d effect size
        pooled_std = np.sqrt(
            (np.var(y1, ddof=1) + np.var(y2, ddof=1)) / 2
        )
        cohens_d = (np.mean(y2) - np.mean(y1)) / pooled_std if pooled_std > 0 else 0

        # Percent change
        mean1, mean2 = np.mean(y1), np.mean(y2)
        change_pct = ((mean2 - mean1) / abs(mean1) * 100) if mean1 != 0 else 0

        # Test of variance homogeneity (Levene's test)
        levene_stat, levene_p = stats.levene(y1, y2)

        return {
            "test_name": "Welch two-sample t-test",
            "t_statistic": float(t_stat),
            "p_value": float(p_value),
            "significant": bool(p_value < 0.05),
            "highly_significant": bool(p_value < 0.001),
            "cohens_d": float(cohens_d),
            "effect_size": "large" if abs(cohens_d) > 0.8 else "medium" if abs(cohens_d) > 0.5 else "small",
            "mean_before": float(mean1),
            "mean_after": float(mean2),
            "std_before": float(np.std(y1, ddof=1)),
            "std_after": float(np.std(y2, ddof=1)),
            "change_pct": float(change_pct),
            "n_before": int(n1),
            "n_after": int(n2),
            "levene_statistic": float(levene_stat),
            "levene_p_value": float(levene_p),
            "variance_homogeneous": bool(levene_p > 0.05),
        }

    def chow_test(self, metric: np.ndarray,
                  break_date: str = CHATGPT_RELEASE_DATE) -> Dict:
        """
        Standard Chow test for a known structural break in a linear trend.

        The pooled model is y ~ 1 + time. The split model fits the same
        regression separately before and after the specified break date.
        """
        if self.n < 20:
            return {"error": "insufficient sample size"}

        break_idx = self.data[self.data["date"] >= break_date].index
        if len(break_idx) == 0:
            return {"error": f"break date {break_date} is out of the data range"}
        break_idx = int(break_idx[0])

        y = np.asarray(metric, dtype=float)
        x = np.arange(len(y), dtype=float)
        y1, y2 = y[:break_idx], y[break_idx:]
        x1, x2 = x[:break_idx], x[break_idx:]

        if len(y1) < 5 or len(y2) < 5:
            return {"error": "insufficient sample size on one side of the break point"}

        sse_pooled, k = self._ols_sse(y, x)
        sse_before, _ = self._ols_sse(y1, x1)
        sse_after, _ = self._ols_sse(y2, x2)
        sse_split = sse_before + sse_after

        numerator = max(sse_pooled - sse_split, 0.0) / k
        denominator_df = len(y1) + len(y2) - 2 * k
        if denominator_df <= 0 or sse_split <= 0:
            return {"error": "invalid degrees of freedom or zero split SSE"}

        denominator = sse_split / denominator_df
        f_stat = numerator / max(denominator, 1e-12)
        p_value = stats.f.sf(f_stat, k, denominator_df)

        return {
            "test_name": "Chow regression test",
            "break_date": str(self.data["date"].iloc[break_idx]),
            "f_statistic": float(f_stat),
            "p_value": float(p_value),
            "significant": bool(p_value < 0.05),
            "highly_significant": bool(p_value < 0.001),
            "sse_pooled": float(sse_pooled),
            "sse_split": float(sse_split),
            "df_num": int(k),
            "df_den": int(denominator_df),
            "n_before": int(len(y1)),
            "n_after": int(len(y2)),
        }

    # ----------------------------------------------------------
    # Bai-Perron-style multiple-break test
    # ----------------------------------------------------------

    def _segment_sse(self, metric: np.ndarray, start: int, end: int) -> float:
        """OLS SSE for metric[start:end] using a local linear trend."""
        y = np.asarray(metric[start:end], dtype=float)
        if len(y) < 2:
            return 0.0
        x = np.arange(len(y), dtype=float)
        sse, _ = self._ols_sse(y, x)
        return sse

    def bai_perron_test(self, metric: np.ndarray,
                        max_breaks: int = 3,
                        min_segment_size: Optional[int] = None) -> Dict:
        """
        Multiple structural-break detection using Bai-Perron-style dynamic
        programming for linear regression segments.

        This implements the central least-squares segmentation idea: minimize
        total residual SSE across m+1 linear segments subject to a minimum
        segment length, then choose the break count by BIC.
        """
        y = np.asarray(metric, dtype=float)
        n = len(y)
        if n < 30:
            return {"error": "series too short for multiple-break detection"}

        if min_segment_size is None:
            min_segment_size = max(8, n // 10)
        max_breaks = min(max_breaks, max(0, n // min_segment_size - 1))
        if max_breaks < 1:
            return {"error": "series too short under the minimum segment-size constraint"}

        sse_cache = {}
        for start in range(n):
            for end in range(start + min_segment_size, n + 1):
                sse_cache[(start, end)] = self._segment_sse(y, start, end)

        inf = float("inf")
        dp = np.full((max_breaks + 1, n + 1), inf)
        prev = [[None for _ in range(n + 1)] for _ in range(max_breaks + 1)]

        for end in range(min_segment_size, n + 1):
            dp[0, end] = sse_cache[(0, end)]

        for breaks in range(1, max_breaks + 1):
            min_end = (breaks + 1) * min_segment_size
            for end in range(min_end, n + 1):
                best_cost = inf
                best_split = None
                split_start = breaks * min_segment_size
                for split in range(split_start, end - min_segment_size + 1):
                    if (split, end) not in sse_cache:
                        continue
                    cost = dp[breaks - 1, split] + sse_cache[(split, end)]
                    if cost < best_cost:
                        best_cost = cost
                        best_split = split
                dp[breaks, end] = best_cost
                prev[breaks][end] = best_split

        candidates = []
        for breaks in range(max_breaks + 1):
            sse = dp[breaks, n]
            if not np.isfinite(sse):
                continue
            segment_count = breaks + 1
            parameter_count = segment_count * 2 + breaks
            bic = n * np.log(max(sse / n, 1e-12)) + parameter_count * np.log(n)
            candidates.append({
                "break_count": breaks,
                "sse": float(sse),
                "bic": float(bic),
            })

        if not candidates:
            return {"error": "no feasible segmentation found"}

        selected = min(candidates, key=lambda item: item["bic"])
        breaks = selected["break_count"]

        break_indices = []
        end = n
        for b in range(breaks, 0, -1):
            split = prev[b][end]
            if split is None:
                break
            break_indices.append(int(split))
            end = split
        break_indices = sorted(break_indices)

        return {
            "test_name": "Bai-Perron least-squares multiple-break segmentation",
            "selected_break_count": int(breaks),
            "break_indices": break_indices,
            "break_dates": [str(self.dates.iloc[i]) for i in break_indices],
            "min_segment_size": int(min_segment_size),
            "max_breaks": int(max_breaks),
            "selected_bic": float(selected["bic"]),
            "selected_sse": float(selected["sse"]),
            "candidates": candidates,
            "has_break": bool(breaks > 0),
        }

    # ----------------------------------------------------------
    # Distribution change analysis
    # ----------------------------------------------------------

    def distribution_change_analysis(self, metric: np.ndarray,
                                     break_date: str = CHATGPT_RELEASE_DATE) -> Dict:
        """
        Distribution change analysis - detects changes in the shape of the distribution before and after the break point

        Statistics of interest:
        - Mean: change in central location
        - Standard deviation: change in dispersion
        - Skewness: change in symmetry (are AI ratings more symmetric?)
        - Kurtosis: change in tail thickness (are AI rating tails thinner?)
        """
        break_idx = self.data[self.data["date"] >= break_date].index
        if len(break_idx) == 0:
            return {"error": "break point out of range"}
        break_idx = int(break_idx[0])

        y1 = metric[:break_idx]
        y2 = metric[break_idx:]

        if len(y1) < 10 or len(y2) < 10:
            return {"error": "insufficient sample size"}

        # Distribution statistics
        stats_before = {
            "mean": float(np.mean(y1)),
            "std": float(np.std(y1, ddof=1)),
            "skewness": float(stats.skew(y1)),
            "kurtosis": float(stats.kurtosis(y1)),  # Excess kurtosis
            "median": float(np.median(y1)),
            "q25": float(np.percentile(y1, 25)),
            "q75": float(np.percentile(y1, 75)),
            "iqr": float(np.percentile(y1, 75) - np.percentile(y1, 25)),
        }

        stats_after = {
            "mean": float(np.mean(y2)),
            "std": float(np.std(y2, ddof=1)),
            "skewness": float(stats.skew(y2)),
            "kurtosis": float(stats.kurtosis(y2)),
            "median": float(np.median(y2)),
            "q25": float(np.percentile(y2, 25)),
            "q75": float(np.percentile(y2, 75)),
            "iqr": float(np.percentile(y2, 75) - np.percentile(y2, 25)),
        }

        # Distribution tests
        # Kolmogorov-Smirnov test
        ks_stat, ks_p = stats.ks_2samp(y1, y2)

        # Variance ratio test
        f_stat = np.var(y1, ddof=1) / max(np.var(y2, ddof=1), 1e-10)
        f_p = 2 * (1 - stats.f.cdf(abs(f_stat), len(y1) - 1, len(y2) - 1))

        return {
            "before": stats_before,
            "after": stats_after,
            "changes": {
                "mean_change": float(stats_after["mean"] - stats_before["mean"]),
                "std_ratio": float(stats_after["std"] / max(stats_before["std"], 1e-10)),
                "skewness_change": float(stats_after["skewness"] - stats_before["skewness"]),
                "kurtosis_change": float(stats_after["kurtosis"] - stats_before["kurtosis"]),
            },
            "ks_test": {
                "statistic": float(ks_stat),
                "p_value": float(ks_p),
                "significant": bool(ks_p < 0.05),
            },
            "f_test": {
                "statistic": float(f_stat),
                "p_value": float(f_p),
                "variance_changed": bool(f_p < 0.05),
            },
        }

    # ----------------------------------------------------------
    # Multi-metric combined analysis
    # ----------------------------------------------------------

    def analyze_all_metrics(self) -> Dict:
        """
        Runs the complete break point analysis on all metrics

        Returns:
        --------
        dict - combined break point analysis results
        """
        results = {}

        for metric_col in self.metric_columns:
            metric_df = self.data[["date", metric_col]].dropna().reset_index(drop=True)
            if len(metric_df) != self.n:
                aligned = StructuralBreakAnalyzer(metric_df.rename(columns={metric_col: "metric"}))
                metric = metric_df["metric"].values
                metric_dates = aligned.dates
            else:
                aligned = self
                metric = self.data[metric_col].values
                metric_dates = self.dates
            if len(metric) < 20:
                continue

            result = {
                "welch_mean_test": aligned.welch_mean_test(metric),
                "chow_test": aligned.chow_test(metric),
                "bai_perron_test": aligned.bai_perron_test(metric),
                "distribution": aligned.distribution_change_analysis(metric),
                "cusum_test": aligned.cusum_test(metric),
                "descriptive": {
                    "mean": float(np.mean(metric)),
                    "std": float(np.std(metric)),
                    "min": float(np.min(metric)),
                    "max": float(np.max(metric)),
                    "date_start": str(metric_dates.iloc[0]),
                    "date_end": str(metric_dates.iloc[-1]),
                }
            }

            results[metric_col] = result

        return results

    # ----------------------------------------------------------
    # Core hypothesis tests
    # ----------------------------------------------------------

    def test_hypothesis_H1(self, df: pd.DataFrame) -> Dict:
        """
        Tests hypothesis H1: the share of low-quality ratings rises significantly after the ChatGPT release

        Operational definition:
        - Low-quality rating: a rating below 2.5/5 (RYM) or below 4/10 (AOTY)
        - Method: compare the change in the share of low-quality ratings before and after the break point
        """
        print("\n  [INFO] Hypothesis H1 test: low-quality rating ratio change")

        # Detect rating columns
        rating_cols = [c for c in df.columns if "rating" in c.lower()
                      and c not in ["rating_ma7", "rating_ma30", "rating_volatility"]]
        if not rating_cols:
            return {"error": "no rating column found"}

        results = {}
        for col in rating_cols:
            clean = df[col].dropna()

            # Determine whether the scale is out of 5 or out of 10
            max_val = clean.max()
            threshold_5pt = 2.5 if max_val <= 5 else 4.0

            # Flag low-quality ratings
            low_quality = (clean <= threshold_5pt).astype(int)

            # Need date information
            if "date" in df.columns:
                date_df = df.loc[clean.index, "date"]
                before_mask = date_df < CHATGPT_RELEASE_DATE
                after_mask = date_df >= CHATGPT_RELEASE_DATE

                before_lq_ratio = low_quality[before_mask].mean()
                after_lq_ratio = low_quality[after_mask].mean()

                # Test for difference in proportions
                n_before = low_quality[before_mask].sum()
                n_total_before = len(low_quality[before_mask])
                n_after = low_quality[after_mask].sum()
                n_total_after = len(low_quality[after_mask])

                # Z test
                p_before = before_lq_ratio
                p_after = after_lq_ratio
                p_pooled = (n_before + n_after) / (n_total_before + n_total_after)
                se = np.sqrt(p_pooled * (1 - p_pooled) * (1/n_total_before + 1/n_total_after))
                z_stat = (p_after - p_before) / max(se, 1e-10)
                z_p = 2 * (1 - stats.norm.cdf(abs(z_stat)))

                results[col] = {
                    "before_ratio": float(before_lq_ratio),
                    "after_ratio": float(after_lq_ratio),
                    "change_pp": float((after_lq_ratio - before_lq_ratio) * 100),
                    "z_statistic": float(z_stat),
                    "p_value": float(z_p),
                    "significant": bool(z_p < 0.05),
                    "H1_supported": bool(after_lq_ratio > before_lq_ratio and z_p < 0.05),
                }

        return results

    def test_hypothesis_H2(self, df: pd.DataFrame,
                           review_col: Optional[str] = None) -> Dict:
        """
        Tests hypothesis H2: the share of high-quality in-depth reviews declines after the ChatGPT release

        Operational definition:
        - High-quality review: more than 300 characters and containing specific detail (track references, technical terms, etc.)
        - Method: compare the share of high-quality reviews before and after the break point
        """
        print("\n  [INFO] Hypothesis H2 test: high-quality review ratio change")

        # H2 is specifically about review depth, so a review-presence flag is
        # not an adequate proxy and missing text makes the hypothesis untestable.
        if review_col and review_col in df.columns:
            # Compute review text length
            review_length = df[review_col].fillna("").astype(str).str.len()
            high_quality = review_length > 300
        else:
            reason = "review text is required to operationalize review depth"
            print(f"  [WARN] H2 not testable: {reason}")
            return {"status": "not_testable", "reason": reason}

        if "date" in df.columns:
            before_mask = df["date"] < CHATGPT_RELEASE_DATE
            after_mask = df["date"] >= CHATGPT_RELEASE_DATE

            before_ratio = high_quality[before_mask].mean()
            after_ratio = high_quality[after_mask].mean()

            # Test for difference in proportions
            n_before = high_quality[before_mask].sum()
            n_total_before = len(high_quality[before_mask])
            n_after = high_quality[after_mask].sum()
            n_total_after = len(high_quality[after_mask])

            p_pooled = (n_before + n_after) / (n_total_before + n_total_after)
            se = np.sqrt(p_pooled * (1 - p_pooled) * (1/n_total_before + 1/n_total_after))
            z_stat = (after_ratio - before_ratio) / max(se, 1e-10)
            z_p = 2 * (1 - stats.norm.cdf(abs(z_stat)))

            return {
                "before_ratio": float(before_ratio),
                "after_ratio": float(after_ratio),
                "change_pp": float((after_ratio - before_ratio) * 100),
                "z_statistic": float(z_stat),
                "p_value": float(z_p),
                "significant": bool(z_p < 0.05),
                "H2_supported": bool(after_ratio < before_ratio and z_p < 0.05),
            }

        return {"error": "no date information"}

    def test_hypothesis_H3(self, df: pd.DataFrame) -> Dict:
        """
        Tests hypothesis H3: rating behavior shows a structural divergence between newly registered and existing users

        Expectation: after the AI shock, the influence (volume/quality) of new-user ratings rises relative to old users
        (because AI accounts tend to be newly registered users)
        """
        print("\n  [INFO] Hypothesis H3 test: rating behavior divergence between new and old users")

        if "user_age_days" not in df.columns:
            reason = "user_age_days is required to distinguish new and existing users"
            print(f"  [WARN] H3 not testable: {reason}")
            return {"status": "not_testable", "reason": reason}

        # Define new users (registered for fewer than 90 days)
        is_new_user = pd.to_numeric(df["user_age_days"], errors="coerce") < 90

        if "date" in df.columns:
            before_mask = df["date"] < CHATGPT_RELEASE_DATE
            after_mask = df["date"] >= CHATGPT_RELEASE_DATE

            # Share of ratings from new users
            before_new_ratio = is_new_user[before_mask].mean()
            after_new_ratio = is_new_user[after_mask].mean()

            # Difference in mean ratings between new and old users
            if "rating" in df.columns or "avg_rating" in df.columns:
                rating_col = "rating" if "rating" in df.columns else "avg_rating"
                old_before = df.loc[~is_new_user & before_mask, rating_col].mean()
                new_before = df.loc[is_new_user & before_mask, rating_col].mean()
                old_after = df.loc[~is_new_user & after_mask, rating_col].mean()
                new_after = df.loc[is_new_user & after_mask, rating_col].mean()

                return {
                    "new_user_ratio_before": float(before_new_ratio),
                    "new_user_ratio_after": float(after_new_ratio),
                    "new_user_ratio_change_pp": float((after_new_ratio - before_new_ratio) * 100),
                    "old_user_mean_before": float(old_before) if pd.notna(old_before) else None,
                    "new_user_mean_before": float(new_before) if pd.notna(new_before) else None,
                    "old_user_mean_after": float(old_after) if pd.notna(old_after) else None,
                    "new_user_mean_after": float(new_after) if pd.notna(new_after) else None,
                    "gap_before": float(new_before - old_before) if (pd.notna(new_before) and pd.notna(old_before)) else None,
                    "gap_after": float(new_after - old_after) if (pd.notna(new_after) and pd.notna(old_after)) else None,
                    "H3_supported": bool(after_new_ratio > before_new_ratio),
                }

        return {"error": "unable to test H3"}

    def run_hypothesis_tests(self, df: pd.DataFrame) -> Dict:
        """Runs all hypothesis tests"""
        print("\n" + "=" * 50)
        print("[INFO] Core hypothesis statistical tests")
        print("=" * 50)

        results = {
            "H1_low_quality_ratio_increase": self.test_hypothesis_H1(df),
            "H2_high_quality_review_decline": self.test_hypothesis_H2(df),
            "H3_new_old_user_behavior_divergence": self.test_hypothesis_H3(df),
        }

        # Print summary
        print("\n[INFO] Hypothesis test result summary:")
        for h, r in results.items():
            if r.get("status") == "not_testable":
                print(f"  {h}: [WARN] not testable ({r['reason']})")
            elif "error" in r:
                print(f"  {h}: [WARN] {r['error']}")
            elif "H1_supported" in r:
                status = "[OK] supported" if r["H1_supported"] else "[FAIL] not supported"
                print(f"  {h}: {status} (change {r.get('change_pp', 0):+.2f} percentage points, "
                      f"p={r.get('p_value', 1):.4f})")
            elif "H2_supported" in r:
                status = "[OK] supported" if r["H2_supported"] else "[FAIL] not supported"
                print(f"  {h}: {status} (change {r.get('change_pp', 0):+.2f} percentage points, "
                      f"p={r.get('p_value', 1):.4f})")
            elif "H3_supported" in r:
                status = "[OK] supported" if r["H3_supported"] else "[FAIL] not supported"
                print(f"  {h}: {status}")
            else:
                print(f"  {h}: results below")
                for k, v in r.items():
                    if isinstance(v, float):
                        print(f"    {k}: {v:.4f}")

        return results


# ============================================================
# Convenience functions
# ============================================================

def run_full_analysis(data: pd.DataFrame,
                      allow_non_empirical: bool = False) -> Dict:
    """
    Runs the complete break point analysis pipeline

    Parameters:
    -----------
    data : pd.DataFrame - data containing date and metric columns

    Returns:
    --------
    dict - complete analysis results
    """
    evidence_class = dataframe_label(data)
    if evidence_class != "empirical observations" and not allow_non_empirical:
        reason = f"structural-break inference requires empirical observations; got {evidence_class}"
        print(f"[WARN] {reason}")
        return {
            "status": "not_testable",
            "reason": reason,
            "evidence_class": evidence_class,
        }

    print("\n" + "=" * 60)
    print("[INFO] Time series structural break analysis - start")
    print("=" * 60)

    analyzer = StructuralBreakAnalyzer(data)

    # 1. Multi-metric break point analysis
    print("\n[Stage 1] Multi-metric break point analysis...")
    break_results = analyzer.analyze_all_metrics()

    # 2. Hypothesis tests
    print("\n[Stage 2] Core hypothesis statistical tests...")
    hypothesis_results = analyzer.run_hypothesis_tests(data)

    # 3. Summary report
    print("\n[Stage 3] Generating summary report...")
    summary = _generate_summary(break_results, hypothesis_results)

    print("\n" + "=" * 60)
    print("[OK] Break point analysis complete")
    print("=" * 60)

    return {
        "status": "demonstration" if evidence_class != "empirical observations" else "empirical_analysis",
        "evidence_class": evidence_class,
        "break_analysis": break_results,
        "hypothesis_tests": hypothesis_results,
        "summary": summary,
    }


def _generate_summary(break_results: Dict,
                       hypothesis_results: Dict) -> Dict:
    """Generates the analysis summary"""
    significant_breaks = 0
    total_metrics = len(break_results)

    for metric, result in break_results.items():
        chow = result.get("chow_test", {})
        if chow.get("significant"):
            significant_breaks += 1

    testable_results = [
        result for result in hypothesis_results.values()
        if result.get("status") != "not_testable" and "error" not in result
    ]

    return {
        "total_metrics_analyzed": total_metrics,
        "significant_breaks": significant_breaks,
        "break_detection_rate": round(significant_breaks / max(total_metrics, 1) * 100, 1),
        "hypotheses_tested": len(testable_results),
        "hypotheses_not_testable": len(hypothesis_results) - len(testable_results),
        "hypotheses_supported": sum(
            1 for r in testable_results
            if r.get("H1_supported") or r.get("H2_supported") or r.get("H3_supported")
        ),
    }


# ============================================================
# Standalone run
# ============================================================

if __name__ == "__main__":
    # Demonstrate with simulated data
    print("Generating simulated data...")
    dates = pd.date_range(start="2020-01-01", end="2026-07-01", freq="7D")
    n = len(dates)

    # Simulate rating metric: change after November 2022
    rng = np.random.default_rng(RANDOM_SEED)
    metric = np.where(
        dates < pd.Timestamp("2022-11-01"),
        3.5 + 0.3 * rng.standard_normal(n),
        3.2 + 0.5 * rng.standard_normal(n)
    )

    df = pd.DataFrame({
        "date": dates,
        "avg_rating": np.clip(metric, 1, 5),
        "rating_count": rng.poisson(100, n).astype(float),
        "review_ratio": np.clip(0.3 + 0.1 * rng.standard_normal(n), 0.05, 0.6),
    })

    df["is_synthetic"] = True
    df["source_dataset"] = "illustrative_structural_break_benchmark"
    results = run_full_analysis(df, allow_non_empirical=True)
    print(f"\nAnalysis summary: {results['summary']}")
