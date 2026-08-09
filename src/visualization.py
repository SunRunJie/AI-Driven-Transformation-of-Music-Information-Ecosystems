"""
Data visualization system with source notes
==========================================
Report figure generation with explicit provenance and scenario labels.

Design principles:
  1. Academic standards: SimSun (Chinese) + Times New Roman (English/numbers) + STIX (math)
  2. Colorblind friendly: based on the Wong (2011) Nature Methods palette
  3. Information density: each figure conveys 3-5 key insights, avoiding empty charts
  4. Unified style: all figures share the same color, font size, and layout conventions
  5. Transparent data sources: every figure notes its data source, sample size, and
     statistical method at the bottom

Figure list (12 figures):
  1. structural_break_analysis  - structural break analysis (three panels)
  2. ai_vs_human_review_features - AI vs human review feature comparison
  3. trust_threshold_model      - trust threshold S-curve + dynamic simulation
  4. competitive_landscape      - competitive landscape bubble chart
  5. four_dimensions_framework  - four-dimensional AI impact framework
  6. genre_impact_heatmap       - genre-differentiated impact heatmap
  7. rating_distribution_evolution - rating distribution evolution comparison
  8. ai_impact_timeline         - full AI impact timeline
  9. heterogeneous_trust        - heterogeneous user trust curves
  10. policy_intervention       - policy intervention comparison
  11. sensitivity_analysis      - parameter sensitivity analysis
  12. feature_correlation_heatmap - feature correlation heatmap
"""

import warnings
import sys
from typing import Dict, List, Optional, Tuple
from pathlib import Path

_SRC = str(Path(__file__).resolve().parent)
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
from matplotlib.gridspec import GridSpec, GridSpecFromSubplotSpec
from matplotlib.patches import FancyBboxPatch
import seaborn as sns
from scipy import stats
from scipy.ndimage import gaussian_filter1d

from config import (
    FIGURES_DIR, ANALYSIS_FIGURES_DIR, CHATGPT_RELEASE_DATE, RANDOM_SEED,
    TRUST_MODEL_PARAMS, FILES, ACADEMIC_COLORS,
    COLORBLIND_PALETTE, FIGURE_DESCRIPTIONS,
    GENRE_EN_CN, METHOD_EN_CN,
)
from data_provenance import dataframe_label

warnings.filterwarnings("ignore")

# ================================================================
# 1. Global style system
# ================================================================

COLORS = ACADEMIC_COLORS  # Academic color scheme
PALETTE = COLORBLIND_PALETTE  # Colorblind friendly

# Academic style configuration
sns.set_style("white")  # White background (academic journal standard)
sns.set_palette(PALETTE)

plt.rcParams.update({
    # Fonts are configured inline below (the fix_font helper no longer exists);
    # only supplementary settings are set here.
    "figure.dpi": 150,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.1,
    "savefig.facecolor": "white",
    "savefig.edgecolor": "none",
    "lines.linewidth": 1.5,
    "lines.markersize": 6,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.spines.left": True,
    "axes.spines.bottom": True,
    "axes.edgecolor": "#333333",
    "axes.linewidth": 0.8,
    "axes.grid": True,
    "grid.alpha": 0.2,
    "grid.color": "#888888",
    "grid.linestyle": "-",
    "legend.frameon": True,
    "legend.fancybox": False,
    "legend.edgecolor": "#888888",
    "legend.facecolor": "white",
    "legend.framealpha": 0.9,
})

# Load fonts after seaborn (SimSun for Chinese, Times New Roman for English,
# STIX for math; the deleted fix_font helper is replaced by these rcParams)
plt.rcParams["font.sans-serif"] = ["SimSun", "Times New Roman", "DejaVu Sans"]
plt.rcParams["font.family"] = "serif"
plt.rcParams["mathtext.fontset"] = "stix"
plt.rcParams["axes.unicode_minus"] = False


# -- Utility functions --

def _save_figure(fig, name: str) -> Path:
    """Save the figure and print a confirmation message."""
    path = ANALYSIS_FIGURES_DIR / name
    fig.savefig(path, dpi=300, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    kb = path.stat().st_size // 1024 if path.exists() else 0
    print(f"  [SAVED] figure saved: {path} ({kb}KB)")
    plt.close(fig)
    return path


def _add_source_note(ax, text: str, y_offset: float = -0.15):
    """Add a data source note at the bottom of the figure (academic convention)."""
    ax.text(
        0, y_offset, text,
        transform=ax.transAxes, fontsize=7, color="#666666",
        ha="left", va="top", style="italic",
    )


def _add_stat_annotation(ax, x, y, text, color="#333333", fontsize=8):
    """Add a statistical test annotation."""
    ax.annotate(
        text, xy=(x, y), fontsize=fontsize, color=color,
        ha="center", va="bottom", fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                  edgecolor=color, alpha=0.8, linewidth=0.5),
    )


def _add_evidence_banner(fig, label: str):
    """Place the input source where it remains visible in exported PNGs."""
    color = COLORS["red"] if "synthetic" in label or "scenario" in label else "#555555"
    fig.text(
        0.995, 0.995, f"Source: {label}",
        ha="right", va="top", fontsize=8, color=color, fontweight="bold",
    )


# ================================================================
# 2. Figure 1: structural break analysis (three panels)
# ================================================================

def plot_structural_break(
    data: pd.DataFrame,
    metric_col: str = "avg_rating",
    break_date: str = CHATGPT_RELEASE_DATE,
    save: bool = True,
) -> plt.Figure:
    """
    Descriptive pre/post figure around a prespecified candidate break date.

    Formal Chow and multiple-break statistics are produced by
    StructuralBreakAnalyzer; this figure does not label the candidate date as
    a detected or causal break.
    """
    print("\n [1/12] Generating structural break analysis figure...")

    if data is None or data.empty:
        raise ValueError("structural-break figure requires a non-empty dataset")
    if "date" not in data.columns or metric_col not in data.columns:
        raise ValueError(f"required columns are date and {metric_col}")

    df = data[[c for c in data.columns if c in {"date", metric_col, "is_synthetic", "source_dataset", "provenance_status"}]].copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df[metric_col] = pd.to_numeric(df[metric_col], errors="coerce")
    df = df.dropna(subset=["date", metric_col]).sort_values("date").reset_index(drop=True)
    if len(df) < 20:
        raise ValueError("at least 20 complete observations are required")
    dates = pd.to_datetime(df["date"])
    metric = df[metric_col].values
    n = len(metric)
    chatgpt_date = pd.Timestamp(break_date)

    # Compute statistics
    metric_series = pd.Series(metric)
    rolling_mean = metric_series.rolling(window=30, min_periods=5).mean()
    rolling_std = metric_series.rolling(window=30, min_periods=5).std()
    rolling_cv = (rolling_std / rolling_mean) * 100  # coefficient of variation

    # CUSUM
    mean_val = np.mean(metric)
    std_val = np.std(metric)
    cumsum = np.cumsum(metric - mean_val) / (std_val * np.sqrt(n) + 1e-10)
    cusum_threshold = 1.96  # 95% confidence level

    # Segment statistics
    before_mask = dates < chatgpt_date
    after_mask = ~before_mask
    before_mean = np.mean(metric[before_mask]) if np.any(before_mask) else np.nan
    after_mean = np.mean(metric[after_mask]) if np.any(after_mask) else np.nan

    # -- Create the three-panel figure (widen panel spacing to prevent vertical overlap) --
    fig = plt.figure(figsize=(16, 13))
    gs = GridSpec(3, 1, figure=fig, hspace=0.35, height_ratios=[1, 1, 1])

    for idx in range(3):
        ax = fig.add_subplot(gs[idx])
        for spine in ["top", "right"]:
            ax.spines[spine].set_visible(False)
        ax.tick_params(axis="both", which="both", length=3, color="#888888")
        # Increase the distance between tick labels and the axis
        ax.tick_params(axis="x", pad=8)
        ax.tick_params(axis="y", pad=6)

    ax1, ax2, ax3 = fig.axes

    # -- Panel A: raw time series --
    ax1.plot(dates, metric, color=COLORS["gray"], linewidth=0.6, alpha=0.4,
             label="Daily observations", zorder=1)

    if np.isfinite(before_mean):
        ax1.axhline(y=before_mean, xmin=0,
                    xmax=np.sum(before_mask) / n,
                    color=COLORS["blue"], linestyle="-", linewidth=1.8,
                    alpha=0.7, label=f"Pre-break mean = {before_mean:.2f}")
    if np.isfinite(after_mean):
        ax1.axhline(y=after_mean,
                    xmin=np.sum(before_mask) / n, xmax=1,
                    color=COLORS["red"], linestyle="-", linewidth=1.8,
                    alpha=0.7, label=f"Post-break mean = {after_mean:.2f}")

    ax1.axvline(x=chatgpt_date, color=COLORS["red"], linestyle="--",
                linewidth=2.5, alpha=0.8, zorder=5)
    ax1.annotate("ChatGPT release\n(Nov 2022)",
                 xy=(chatgpt_date, ax1.get_ylim()[1] * 0.9),
                 fontsize=9, color=COLORS["red"], fontweight="bold",
                 ha="center", va="bottom",
                 bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                           edgecolor=COLORS["red"], alpha=0.8))

    if np.isfinite(before_mean) and np.isfinite(after_mean):
        change = after_mean - before_mean
        ax1.annotate(f"Delta = {change:+.2f}",
                     xy=(chatgpt_date, (before_mean + after_mean) / 2),
                     fontsize=10, color=COLORS["purple"], fontweight="bold",
                     ha="left", va="center",
                     arrowprops=dict(arrowstyle="<->", color=COLORS["purple"],
                                     linewidth=1.5, alpha=0.6))

    ax1.set_ylabel(f"{metric_col} (rating)", fontsize=11)
    ax1.set_title("A  Rating time series - pre/post comparison at candidate date",
                  fontsize=13, fontweight="bold", loc="left")
    ax1.legend(loc="upper right", fontsize=8, ncol=2, framealpha=0.85)
    ax1.set_xlim(dates.iloc[0], dates.iloc[-1])

    # -- Panel B: rolling statistics --
    ax2.plot(dates, metric, color="gray", alpha=0.1, linewidth=0.5, zorder=1)
    ax2.plot(dates, rolling_mean, color=COLORS["blue"], linewidth=2,
             label="30-day rolling mean", zorder=3)
    ax2.fill_between(dates,
                     rolling_mean - 1.96 * rolling_std,
                     rolling_mean + 1.96 * rolling_std,
                     color=COLORS["blue"], alpha=0.08,
                     label="Rolling mean +/- 1.96 rolling SD")
    ax2.axvline(x=chatgpt_date, color=COLORS["red"], linestyle="--",
                linewidth=2, alpha=0.7, zorder=4)

    ax2_twin = ax2.twinx()
    ax2_twin.plot(dates, rolling_cv, color=COLORS["orange"], linewidth=1.2,
                  alpha=0.6, linestyle=":", label="Coefficient of variation (CV%)")
    ax2_twin.set_ylabel("Coefficient of variation CV%", fontsize=9, color=COLORS["orange"])
    ax2_twin.tick_params(axis="y", labelcolor=COLORS["orange"], labelsize=8)

    ax2.set_ylabel("Rolling mean", fontsize=11)
    ax2.set_title("B  Rolling trend - descriptive mean and variability envelope",
                  fontsize=13, fontweight="bold", loc="left")
    ax2.legend(loc="upper left", fontsize=8, ncol=2, framealpha=0.85)

    # -- Panel C: CUSUM --
    ax3.plot(dates, cumsum, color=COLORS["green"], linewidth=1.8, zorder=3)
    ax3.axhline(y=cusum_threshold, color=COLORS["red"], linestyle=":",
                linewidth=1.2, alpha=0.6)
    ax3.axhline(y=-cusum_threshold, color=COLORS["red"], linestyle=":",
                linewidth=1.2, alpha=0.6)
    ax3.axhline(y=0, color="#888888", linewidth=0.5, alpha=0.3)
    ax3.axvline(x=chatgpt_date, color=COLORS["red"], linestyle="--",
                linewidth=2, alpha=0.7, zorder=4)
    ax3.fill_between(dates, cusum_threshold, -cusum_threshold,
                     alpha=0.05, color=COLORS["red"])

    max_cusum = np.max(np.abs(cumsum))
    max_idx = np.argmax(np.abs(cumsum))
    ax3.scatter([dates.iloc[max_idx]], [cumsum[max_idx]],
                color=COLORS["red"], s=60, zorder=5,
                edgecolors="black", linewidth=0.5)
    ax3.annotate(f"max |CUSUM| = {max_cusum:.2f}",
                 xy=(dates.iloc[max_idx], cumsum[max_idx]),
                 xytext=(dates.iloc[max_idx] + pd.Timedelta(days=60),
                         cumsum[max_idx] + 0.5),
                 fontsize=9, fontweight="bold", color=COLORS["red"],
                 arrowprops=dict(arrowstyle="->", color=COLORS["red"],
                                 alpha=0.5, linewidth=1),
                 bbox=dict(boxstyle="round,pad=0.2", facecolor="white",
                           alpha=0.8))

    # Add headroom so the max-|CUSUM| annotation never collides with the title
    ymin_c, ymax_c = ax3.get_ylim()
    ax3.set_ylim(ymin_c, max(ymax_c, max_cusum + 2.2))

    ax3.set_xlabel("Date", fontsize=11)
    ax3.set_ylabel("CUSUM statistic", fontsize=11)
    ax3.set_title(f"C  Standardized cumulative deviation - reference +/-{cusum_threshold}",
                  fontsize=13, fontweight="bold", loc="left")
    ax3.legend(loc="upper right", fontsize=8,
               handles=[
                   plt.Line2D([], [], color=COLORS["green"], linewidth=1.8,
                              label="CUSUM path"),
                   plt.Line2D([], [], color=COLORS["red"], linestyle=":",
                              linewidth=1.2, label=f"Threshold +/-{cusum_threshold}"),
               ],
               framealpha=0.85)

    fig.text(0.5, 0.01,
             f"Data class: {dataframe_label(df)} | N={n} complete observations | "
             f"Candidate date: {break_date} | Descriptive CUSUM path and rolling statistics",
             ha="center", fontsize=7, color="#888888", style="italic")

    fig.suptitle("Pre/post rating comparison at a prespecified candidate date",
                 fontsize=15, fontweight="bold", y=0.97)
    _add_evidence_banner(fig, dataframe_label(df))
    plt.tight_layout(rect=[0, 0.02, 1, 0.95])
    # Add extra spacing between subplots
    plt.subplots_adjust(hspace=0.30)

    if save:
        return _save_figure(fig, FILES["figure_break"])
    return fig


# ================================================================
# 3. Figure 2: AI vs human review feature comparison
# ================================================================

def plot_ai_feature_comparison(
    human_reviews: List[str],
    ai_reviews: List[str],
    save: bool = True,
) -> plt.Figure:
    """
    Fully redesigned AI vs Human feature comparison figure
    Left: radar plot (filled area + clear labels)
    Right: horizontal diverging bar chart (warm-cool gradient)
    The two panels are clearly separated and undistorted
    """
    print("\n[2/12] Generating AI review feature comparison figure (redesigned)...")

    from analysis.ai_review_analysis import AIReviewAnalyzer
    analyzer = AIReviewAnalyzer()
    feature_df = analyzer.get_feature_comparison_df(human_reviews, ai_reviews)

    compare_cols = [
        "vocabulary_diversity", "avg_sentence_length",
        "emotional_words", "specific_references",
        "technical_terms", "first_person_count",
        "filler_words", "sentence_length_std",
        "allcaps_ratio", "number_references",
        "contrastive_words",
    ]

    labels_cn = {
        "vocabulary_diversity": "Vocabulary diversity",
        "avg_sentence_length": "Avg. sentence length",
        "emotional_words": "Emotional words",
        "specific_references": "Specific references",
        "technical_terms": "Technical terms",
        "first_person_count": "First person",
        "filler_words": "Filler words",
        "sentence_length_std": "Sentence length SD",
        "allcaps_ratio": "All-caps ratio",
        "number_references": "Number references",
        "contrastive_words": "Contrastive words",
    }

    human_means = feature_df[feature_df["source"] == "Human review"][compare_cols].mean()
    ai_means = feature_df[feature_df["source"] == "AI review"][compare_cols].mean()
    human_std = feature_df[feature_df["source"] == "Human review"][compare_cols].std(ddof=1)
    ai_std = feature_df[feature_df["source"] == "AI review"][compare_cols].std(ddof=1)
    pooled_std = np.sqrt((human_std.values ** 2 + ai_std.values ** 2) / 2)
    diffs = np.divide(
        ai_means.values - human_means.values,
        pooled_std,
        out=np.zeros_like(ai_means.values, dtype=float),
        where=pooled_std > 1e-9,
    )
    sort_idx = np.argsort(np.abs(diffs))[::-1]
    n_features = len(compare_cols)

    # Normalize to 0-1 (for the radar plot)
    max_vals = np.max([human_means.values, ai_means.values], axis=0)
    max_vals = np.where(max_vals == 0, 1, max_vals)
    human_norm = human_means.values / max_vals
    ai_norm = ai_means.values / max_vals

    # -- Create the two-panel figure, using GridSpec for fine spacing control --
    fig = plt.figure(figsize=(18, 8))
    gs = GridSpec(1, 3, figure=fig, width_ratios=[1.35, 0.35, 1.30], wspace=0.15)

    # ==============================================
    # Panel A: radar plot (fixed square aspect to avoid distortion)
    # ==============================================
    ax1 = fig.add_subplot(gs[0], projection="polar")
    angles = np.linspace(0, 2 * np.pi, n_features, endpoint=False).tolist()
    angles += angles[:1]

    human_vals_plot = human_norm.tolist() + human_norm[:1].tolist()
    ai_vals_plot = ai_norm.tolist() + ai_norm[:1].tolist()

    # Human - blue fill (semi-transparent)
    ax1.fill(angles, human_vals_plot, alpha=0.20, color="#0085CA", zorder=2)
    ax1.plot(angles, human_vals_plot, "o-", linewidth=2.5,
             color="#0085CA", markersize=7, label="Human", zorder=3)

    # AI - red fill (semi-transparent)
    ax1.fill(angles, ai_vals_plot, alpha=0.20, color="#E74C3C", zorder=1)
    ax1.plot(angles, ai_vals_plot, "s-", linewidth=2.5,
             color="#E74C3C", markersize=7, label="AI", zorder=3)

    # Feature name labels: radial (radiating) layout.
    # Each label is rotated so its reading direction runs along the extension
    # of the line from the origin through its own vertex (the line is not drawn),
    # giving a clockwise ring of spokes around the radar.
    # Right half: rotation = angle, ha="left" (text extends outward);
    # left half: rotation = angle + 180, ha="right" (text also extends outward,
    # reading from the outside in, so it stays upright and never shrinks inward).
    label_angles = np.linspace(0, 2 * np.pi, n_features, endpoint=False)
    for ang, col in zip(label_angles, compare_cols):
        label = labels_cn.get(col, col)
        angle_deg = np.degrees(ang)
        if 90 < angle_deg < 270:
            rotation = angle_deg + 180
            ha = "right"
        else:
            rotation = angle_deg
            ha = "left"
        ax1.text(ang, 1.10, label, fontsize=9, fontweight="bold",
                ha=ha, va="center", color="#333333",
                rotation=rotation, rotation_mode="anchor")

    ax1.set_ylim(0, 1.38)
    ax1.set_title("A  Human vs AI Radar", fontsize=14,
                  fontweight="bold", loc="left", pad=55)
    ax1.legend(loc="upper right", fontsize=10, framealpha=0.85)
    ax1.set_xticks([])
    ax1.set_yticks([])
    ax1.grid(True, alpha=0.2, linestyle="--")

    # ==============================================
    # Panel B: diverging percentage bar chart (horizontal)
    # ==============================================
    ax2 = fig.add_subplot(gs[2])
    ax2.set_facecolor("white")

    diffs_sorted = diffs[sort_idx]
    cols_sorted = [compare_cols[i] for i in sort_idx]
    labels_sorted = [labels_cn.get(c, c) for c in cols_sorted]

    max_abs = max(abs(diffs_sorted))
    norm = plt.Normalize(-max_abs, max_abs)
    cmap_div = plt.cm.RdYlBu_r
    bar_colors = [cmap_div(norm(d)) for d in diffs_sorted]

    bars = ax2.barh(range(n_features), diffs_sorted, color=bar_colors,
                    alpha=0.85, edgecolor="white", linewidth=0.6,
                    height=0.65, zorder=3)

    ax2.set_yticks(range(n_features))
    ax2.set_yticklabels(labels_sorted, fontsize=9, fontweight="bold")
    ax2.axvline(x=0, color="#333333", linewidth=1.5, zorder=2)

    for bar, diff in zip(bars, diffs_sorted):
        x_pos = bar.get_width()
        label_x = x_pos + max_abs * 0.035 if x_pos >= 0 else x_pos - max_abs * 0.035
        ha = "left" if x_pos >= 0 else "right"
        clr = "#C0392B" if x_pos > 0 else "#2980B9"
        ax2.text(label_x, bar.get_y() + bar.get_height() / 2,
                f"{diff:+.2f}", va="center", ha=ha,
                fontsize=9, fontweight="bold", color=clr)

    ax2.set_xlabel("Standardized mean difference (AI - human)", fontsize=11)
    ax2.set_title("B  Standardized difference (sorted by magnitude)", fontsize=14,
                  fontweight="bold", loc="left")
    ax2.grid(True, alpha=0.12, axis="x")
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.set_xlim(-max_abs * 1.3, max_abs * 1.3)

    from analysis.ai_review_analysis import HUMAN_CORPUS_LABEL

    # Bottom source note
    fig.text(0.5, 0.01,
             f"Controlled comparison | Human: {HUMAN_CORPUS_LABEL} | "
             "AI: 15 manually authored assistant-style controls | No external detector validation",
             ha="center", fontsize=7, color="#888888", style="italic")
    _add_evidence_banner(fig, "observed human text + controlled AI text")

    plt.tight_layout(rect=[0, 0.02, 1, 0.95])

    if save:
        return _save_figure(fig, FILES["figure_ai_features"])
    return fig


# ================================================================
# 4. Figure 3: trust threshold model
# ================================================================

def plot_trust_threshold(
    ai_penetration_data: Optional[pd.DataFrame] = None,
    save: bool = True,
) -> plt.Figure:
    """
    Uncalibrated trust-threshold scenario model and deterministic scenarios.
    """
    print("\n [3/12] Generating trust threshold model figure...")

    from analysis.trust_threshold_analysis import TrustThresholdModel
    model = TrustThresholdModel(TRUST_MODEL_PARAMS)

    fig = plt.figure(figsize=(18, 8))
    gs = GridSpec(1, 2, figure=fig, width_ratios=[1, 1], wspace=0.3)

    # -- Left panel: trust curve (enhanced) --
    ax1 = fig.add_subplot(gs[0])
    penetration_range = np.linspace(0, 1, 500)
    trust_values = np.array([model.user_trust_function(p) for p in penetration_range])
    derivatives = np.array([model.trust_derivative(p) for p in penetration_range])
    threshold = model.params["trust_threshold"]

    ax1.plot(penetration_range, trust_values, color=COLORS["blue"],
             linewidth=3.5, label="Trust function T(p)", zorder=4)
    ax1.axhline(y=threshold, color=COLORS["red"], linestyle="--",
                linewidth=2, alpha=0.8, zorder=3)
    ax1.annotate(f"Selected reference = {threshold}",
                 xy=(0.75, threshold + 0.02), fontsize=9,
                 color=COLORS["red"], fontweight="bold",
                 ha="left", va="bottom")
    ax1.fill_between(penetration_range, trust_values, 0,
                     where=trust_values > threshold,
                     color=COLORS["green"], alpha=0.06, label="Above reference")
    ax1.fill_between(penetration_range, trust_values, 0,
                     where=trust_values <= threshold,
                     color=COLORS["red"], alpha=0.06, label="Below reference")

    critical = model.find_critical_point()
    ax1.scatter([critical["critical_penetration"]], [critical["critical_trust"]],
                color=COLORS["orange"], s=120, zorder=5,
                edgecolors="black", linewidth=1.5)
    ax1.annotate(f"Steepest modeled slope\nPenetration = {critical['critical_penetration']:.1%}\nTrust = {critical['critical_trust']:.2f}",
                 xy=(critical["critical_penetration"], critical["critical_trust"]),
                 xytext=(critical["critical_penetration"] + 0.15,
                         critical["critical_trust"] + 0.15),
                 fontsize=9, fontweight="bold", color=COLORS["orange"],
                 arrowprops=dict(arrowstyle="->", color=COLORS["orange"],
                                 linewidth=1.5),
                 bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                           edgecolor=COLORS["orange"], alpha=0.9))

    ax1_twin = ax1.twinx()
    ax1_twin.plot(penetration_range, derivatives, color=COLORS["purple"],
                  linewidth=1.5, alpha=0.5, linestyle="--",
                  label="Trust decay rate T'(p)")
    ax1_twin.set_ylabel("Trust decay rate (derivative)", fontsize=10,
                        color=COLORS["purple"])
    ax1_twin.tick_params(axis="y", labelcolor=COLORS["purple"], labelsize=8)

    ax1.set_xlabel("AI content penetration rate", fontsize=11)
    ax1.set_ylabel("User trust", fontsize=11)
    ax1.set_title("A  Trust curve under selected assumptions",
                  fontsize=13, fontweight="bold", loc="left")
    ax1.set_xlim(-0.02, 1.02)
    ax1.set_ylim(-0.02, 1.08)
    ax1.legend(loc="upper right", fontsize=8, ncol=2, framealpha=0.85)
    ax1.grid(True, alpha=0.15)

    # -- Right panel: dynamic simulation (enhanced) --
    ax2 = fig.add_subplot(gs[1])
    scenarios = model.simulate_multiple_scenarios()
    scenario_colors = [COLORS["blue"], COLORS["green"], COLORS["orange"],
                       COLORS["purple"], COLORS["red"]]

    for (name, df), color in zip(scenarios.items(), scenario_colors):
        ax2.plot(df["time"], df["trust"], color=color, linewidth=2,
                 label=name, alpha=0.8, zorder=3)
        final_trust = df["trust"].iloc[-1]
        ax2.scatter([df["time"].iloc[-1]], [final_trust],
                    color=color, s=50, zorder=4,
                    edgecolors="black", linewidth=0.5)

    ax2.axhline(y=threshold, color=COLORS["red"], linestyle=":",
                linewidth=1.5, alpha=0.6, zorder=2)
    ax2.annotate(f"Selected reference = {threshold}",
                 xy=(0, threshold), fontsize=8, color=COLORS["red"],
                 ha="right", va="bottom", fontweight="bold")

    ax2.set_xlabel("Time steps", fontsize=11)
    ax2.set_ylabel("User trust", fontsize=11)
    ax2.set_title("B  Five parameter settings over 100 steps",
                  fontsize=13, fontweight="bold", loc="left")
    ax2.legend(loc="lower left", fontsize=8, ncol=1, framealpha=0.85)
    ax2.set_ylim(-0.05, 1.05)
    ax2.grid(True, alpha=0.15)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)

    fig.text(0.5, 0.01,
             "Model parameters: alpha(preference)={0}, beta(discrimination)={1}, gamma(network)={2}, threshold={3}  "
             "| Method: deterministic logistic scenario analysis; parameters are not empirically calibrated".format(
                 model.params["alpha"], model.params["beta"],
                 model.params["gamma"], model.params["trust_threshold"]),
             ha="center", fontsize=7, color="#888888", style="italic")

    fig.suptitle("Trust response under selected assumptions",
                 fontsize=15, fontweight="bold", y=0.98)
    _add_evidence_banner(fig, "uncalibrated assumptions")
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])

    if save:
        return _save_figure(fig, FILES["figure_trust"])
    return fig


# ================================================================
# 5. Figure 4: competitive landscape bubble chart
# ================================================================

def plot_competitive_landscape(save: bool = True) -> plt.Figure:
    """
    Enhanced competitive landscape quadrant bubble chart
    Horizontal axis: data depth  Vertical axis: social engagement
    Points and colors are analyst-coded ordinal scenario inputs, not measured
    platform metrics.
    """
    print("\n [4/12] Generating competitive landscape positioning figure...")

    from analysis.platform_competition_analysis import PLATFORM_DATA

    df = pd.DataFrame.from_dict(PLATFORM_DATA, orient="index").reset_index()
    df = df.rename(columns={"index": "platform"})

    fig, ax = plt.subplots(figsize=(14, 10))

    colors = df["ai_risk_score"]

    scatter = ax.scatter(
        df["data_depth"], df["social_engagement"],
        s=260, c=colors, cmap="RdYlGn_r",
        alpha=0.8, edgecolors="#333333", linewidth=1.2, zorder=4,
    )

    offsets = {
        "RYM": (0.3, 0.2), "AOTY": (-0.3, 0.3),
        "Pitchfork": (-0.5, -0.3), "Discogs": (0.3, -0.2),
        "Spotify": (-0.3, -0.3), "Bandcamp": (0.3, 0.2),
        "Douban Music": (-0.3, 0.3), "Last.fm": (0.3, -0.2),
        "SoundCloud": (-0.3, 0.2),
    }

    for _, row in df.iterrows():
        offset = offsets.get(row["platform"], (0.15, 0.15))
        ax.annotate(
            row["platform"],
            (row["data_depth"], row["social_engagement"]),
            fontsize=11, fontweight="bold",
            xytext=(12 + offset[0] * 20, 8 + offset[1] * 20),
            textcoords="offset points",
            bbox=dict(boxstyle="round,pad=0.3",
                     facecolor="white", alpha=0.85, edgecolor="#888888",
                     linewidth=0.5),
            zorder=5,
            arrowprops=dict(arrowstyle="-", color="#888888",
                           alpha=0.4, linewidth=0.5),
        )

    high_risk = df[df["ai_risk_score"] >= 8]
    # Each "[WARN] High risk" label sits directly below its own bubble in data
    # coordinates (robust under tight-bbox saving) with a short arrow up to it,
    # so every label is clearly tied to its own dot and they never bunch up.
    warn_positions = {
        "RYM": (9.5, 6.15),
        "AOTY": (7.0, 7.70),
        "Douban Music": (6.5, 7.00),
    }
    for _, row in high_risk.iterrows():
        lx, ly = warn_positions.get(
            row["platform"],
            (row["data_depth"], row["social_engagement"] - 1.0),
        )
        ax.annotate("Higher coded risk",
                    (row["data_depth"], row["social_engagement"]),
                    xytext=(lx, ly),
                    textcoords="data",
                    fontsize=8, color=COLORS["red"], alpha=0.9,
                    fontweight="bold", zorder=5,
                    ha="center", va="center",
                    bbox=dict(boxstyle="round,pad=0.15", facecolor="white",
                             edgecolor=COLORS["red"], alpha=0.8, linewidth=0.5),
                    arrowprops=dict(arrowstyle="->", color=COLORS["red"],
                                   alpha=0.55, linewidth=0.9))

    ax.axhline(y=5.5, color="#888888", linestyle=":", alpha=0.3, linewidth=1)
    ax.axvline(x=5.5, color="#888888", linestyle=":", alpha=0.3, linewidth=1)

    quad_props = dict(boxstyle="round,pad=0.3", facecolor="white",
                     edgecolor="none", alpha=0.6)
    ax.text(3.2, 8.5, "Social-Driven", fontsize=10,
            color="#666666", ha="center", va="center", bbox=quad_props)
    ax.text(8.2, 8.5, "Full-Stack", fontsize=10,
            color="#666666", ha="center", va="center", bbox=quad_props)
    ax.text(3.2, 2.0, "Niche", fontsize=10,
            color="#666666", ha="center", va="center", bbox=quad_props)
    ax.text(8.2, 2.0, "Data-Driven", fontsize=10,
            color="#666666", ha="center", va="center", bbox=quad_props)

    cbar = plt.colorbar(scatter, ax=ax, shrink=0.6, pad=0.02)
    cbar.set_label("AI risk score", fontsize=10)
    cbar.ax.tick_params(labelsize=8)

    ax.set_xlabel("Data depth - database size / metadata granularity", fontsize=12)
    ax.set_ylabel("Social engagement - community interaction / UGC activity", fontsize=12)
    ax.set_title("Analyst-coded platform positioning scenario\nColor = assumed AI-risk score (ordinal, 1-10)",
                 fontsize=14, fontweight="bold")
    ax.set_xlim(2, 10.5)
    ax.set_ylim(1.5, 10)
    ax.grid(True, alpha=0.15)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.text(0.5, 0.01,
             "Analyst-authored rubric for hypothesis generation | Scores are assumptions, not observed measurements or rankings",
             ha="center", fontsize=7, color="#888888", style="italic")
    _add_evidence_banner(fig, "analyst assumptions")

    plt.tight_layout(rect=[0, 0.03, 1, 0.97])

    if save:
        return _save_figure(fig, FILES["figure_competitive"])
    return fig


# ================================================================
# 6. Figure 5: AI impact four-dimensional framework overview
# ================================================================

def plot_four_dimensions(save: bool = True) -> plt.Figure:
    """
    Four-dimensional institutional logic framework figure
    Left: four-dimensional impact assessment (grouped bars + gap annotations)
    Right: strategic priority matrix (bubble chart)
    """
    print("\n [5/12] Generating AI impact four-dimensional framework figure...")

    dimensions = ["Information production\nmodel disruption", "Evaluation discourse\nreallocation",
                  "Service function\ngenerational upgrade", "Data asset\nvalue revaluation"]
    dim_short = ["Information production", "Discourse power", "Service function", "Data assets"]
    impact_scores = [9, 8, 6, 7]
    future_scores = [9, 9, 8, 9]
    readiness = [4, 3, 6, 3]

    fig = plt.figure(figsize=(20, 8))
    gs = GridSpec(1, 2, figure=fig, width_ratios=[1, 1], wspace=0.3)

    ax1 = fig.add_subplot(gs[0])
    x = np.arange(len(dimensions))
    width = 0.22

    bars1 = ax1.bar(x - width, impact_scores, width,
                    label="Current impact",
                    color=COLORS["red"], alpha=0.8,
                    edgecolor="white", linewidth=0.5, zorder=3)
    bars2 = ax1.bar(x, future_scores, width,
                    label="Future impact (3 years)",
                    color=COLORS["dark"], alpha=0.8,
                    edgecolor="white", linewidth=0.5, zorder=3)
    bars3 = ax1.bar(x + width, readiness, width,
                    label="Platform readiness",
                    color=COLORS["blue"], alpha=0.8,
                    edgecolor="white", linewidth=0.5, zorder=3)

    ax1.set_xticks(x)
    ax1.set_xticklabels(dimensions, fontsize=8.5, fontweight="bold")
    ax1.tick_params(axis="x", pad=8)
    ax1.set_ylabel("Score - 1 (low) to 10 (high)", fontsize=11)
    ax1.set_title("A  Four-dimensional AI impact framework - impact and readiness assessment",
                  fontsize=13, fontweight="bold", loc="left")
    ax1.legend(fontsize=9, loc="upper right", framealpha=0.85)
    ax1.grid(True, alpha=0.15, axis="y")
    ax1.set_ylim(0, 11)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)

    for i in range(4):
        gap = impact_scores[i] - readiness[i]
        color = COLORS["red"] if gap >= 4 else COLORS["orange"]
        ax1.annotate(f"Gap = {gap}",
                    xy=(i, readiness[i]),
                    xytext=(i + width * 1.5, readiness[i] - 1.5),
                    fontsize=9, color=color, fontweight="bold",
                    arrowprops=dict(arrowstyle="->", color=color,
                                  alpha=0.5, linewidth=1.5), zorder=5,
                    bbox=dict(boxstyle="round,pad=0.15", facecolor="white",
                             alpha=0.8, edgecolor="none"))

    for bars in [bars1, bars2, bars3]:
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width() / 2, height + 0.1,
                     f"{int(height)}", ha="center", va="bottom",
                     fontsize=8, fontweight="bold", color="#555555")

    ax2 = fig.add_subplot(gs[1])
    urgency, importance = impact_scores, future_scores
    point_colors = [COLORS["red"], COLORS["red"], COLORS["orange"], COLORS["red"]]
    ax2.scatter(importance, urgency, s=500, c=point_colors,
                alpha=0.75, edgecolors="#333333", linewidth=1.5, zorder=4)

    for i, dim in enumerate(dim_short):
        ax2.annotate(dim, (importance[i] + 0.15, urgency[i] + 0.15),
                    fontsize=11, fontweight="bold", zorder=5)

    ax2.axhline(y=7, color="#888888", linestyle=":", alpha=0.3)
    ax2.axvline(x=7, color="#888888", linestyle=":", alpha=0.3)

    for rx, ry, rlabel, rcolor in [
        (8.5, 9.5, "Act Now", COLORS["red"]),
        (5, 9.5, "Plan", COLORS["orange"]),
        (8.5, 5, "Monitor", COLORS["orange"]),
        (5, 5, "Routine", COLORS["green"]),
    ]:
        ax2.text(rx, ry, rlabel, fontsize=11, fontweight="bold",
                color=rcolor, ha="center", va="center",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                         alpha=0.7, edgecolor=rcolor, linewidth=0.5))

    ax2.set_xlabel("Strategic importance", fontsize=11)
    ax2.set_ylabel("Action urgency", fontsize=11)
    ax2.set_title("B  Strategic priority matrix", fontsize=13, fontweight="bold", loc="left")
    ax2.set_xlim(4, 10.5)
    ax2.set_ylim(4, 10.5)
    ax2.grid(True, alpha=0.15)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)

    fig.text(0.5, 0.01,
             "Illustrative analyst-coded rubric | Ordinal scores are assumptions for discussion, not measured effects or forecasts",
             ha="center", fontsize=7, color="#888888", style="italic")

    fig.suptitle("Four dimensions considered in the AI scenario",
                 fontsize=15, fontweight="bold", y=0.98)
    _add_evidence_banner(fig, "analyst assumptions")
    plt.tight_layout(rect=[0, 0.05, 1, 0.95])

    if save:
        return _save_figure(fig, FILES["figure_four_dimensions"])
    return fig


# ================================================================
# 7. Figure 6: genre impact heatmap
# ================================================================

def plot_genre_impact_heatmap(
    observed_archives: Optional[Dict] = None,
    save: bool = True,
) -> plt.Figure:
    """Observed genre profiles across the AOTY and RYM snapshots."""
    print("\n [6/12] Generating observed genre profile heatmap...")

    if observed_archives is None:
        from analysis.observed_archive_analysis import load_observed_archives
        observed_archives = load_observed_archives(export=False)
    genre = observed_archives["genre_summary"].copy()

    raw_columns = [
        "aoty_median_score", "aoty_median_ratings", "rym_median_score",
        "rym_median_ratings", "rym_median_review_share",
    ]
    labels = [
        "AOTY median\nscore (0-5)", "AOTY median\nratings",
        "RYM median\nscore (0-5)", "RYM median\nratings",
        "RYM reviews per\n100 ratings",
    ]
    display = genre[raw_columns].copy()
    display["rym_median_review_share"] *= 100
    standardised = (display - display.mean()) / display.std(ddof=0)

    annotations = np.empty(display.shape, dtype=object)
    for row in range(len(display)):
        annotations[row, 0] = f"{display.iloc[row, 0]:.2f}"
        annotations[row, 1] = f"{display.iloc[row, 1]:,.0f}"
        annotations[row, 2] = f"{display.iloc[row, 2]:.2f}"
        annotations[row, 3] = f"{display.iloc[row, 3]:,.0f}"
        annotations[row, 4] = f"{display.iloc[row, 4]:.2f}%"

    fig = plt.figure(figsize=(15, 9))
    gs = GridSpec(1, 2, figure=fig, width_ratios=[4.4, 1.1], wspace=0.08)
    ax1 = fig.add_subplot(gs[0])
    cmap = sns.diverging_palette(250, 15, s=75, l=55, as_cmap=True)
    sns.heatmap(
        standardised,
        cmap=cmap,
        center=0,
        vmin=-2,
        vmax=2,
        annot=annotations,
        fmt="",
        linewidths=0.6,
        linecolor="white",
        cbar_kws={"label": "Within-column standard deviations", "shrink": 0.68},
        ax=ax1,
    )
    ax1.set_xticklabels(labels, rotation=0, fontsize=9, fontweight="bold")
    ax1.set_yticklabels(genre["genre"], rotation=0, fontsize=9)
    ax1.set_xlabel("")
    ax1.set_ylabel("")
    ax1.set_title(
        "A  Observed score, attention, and review profiles by shared genre",
        fontsize=13,
        fontweight="bold",
        loc="left",
    )

    ax2 = fig.add_subplot(gs[1])
    y = np.arange(len(genre))
    ax2.barh(
        y - 0.18, genre["aoty_albums"], height=0.34,
        color=COLORS["blue"], label="AOTY", alpha=0.85,
    )
    ax2.barh(
        y + 0.18, genre["rym_albums"], height=0.34,
        color=COLORS["orange"], label="RYM", alpha=0.85,
    )
    ax2.set_yticks(y)
    ax2.set_yticklabels([])
    ax2.invert_yaxis()
    ax2.set_xlabel("Albums in snapshot", fontsize=9)
    ax2.set_title("B  Coverage", fontsize=13, fontweight="bold", loc="left")
    ax2.legend(fontsize=9, framealpha=0.85)
    ax2.grid(True, axis="x", alpha=0.15)

    fig.suptitle(
        "Genre structure in observed AOTY and RYM archive snapshots",
        fontsize=15,
        fontweight="bold",
        y=0.98,
    )
    fig.text(
        0.5, 0.01,
        "AOTY high-rated snapshot (2024-10-20) and RYM most-popular snapshot (2022-03-11) | "
        "Cells show raw medians; colour is standardised within each metric | Selection rules differ",
        ha="center", fontsize=7, color="#777777", style="italic",
    )
    _add_evidence_banner(fig, "third-party observed archives")
    plt.tight_layout(rect=[0, 0.04, 1, 0.95])

    if save:
        return _save_figure(fig, FILES["figure_genre_impact"])
    return fig


# ================================================================
# 8. Figure 7: rating distribution evolution
# ================================================================

def plot_rating_distribution_evolution(
    data: Optional[pd.DataFrame] = None,
    rating_col: Optional[str] = None,
    observed_archives: Optional[Dict] = None,
    save: bool = True,
) -> plt.Figure:
    """Cross-platform score agreement among exact album matches."""
    print("\n [7/12] Generating cross-platform rating comparison...")

    if observed_archives is None:
        from analysis.observed_archive_analysis import load_observed_archives
        observed_archives = load_observed_archives(export=False)
    matched = observed_archives["cross_platform_matches"].dropna(
        subset=["aoty_user_score_5", "avg_rating", "aoty_minus_rym"]
    )
    x = matched["aoty_user_score_5"].to_numpy()
    y = matched["avg_rating"].to_numpy()
    difference = matched["aoty_minus_rym"].to_numpy()
    pearson = stats.pearsonr(x, y).statistic
    spearman = stats.spearmanr(x, y).statistic
    within_half = np.mean(np.abs(difference) <= 0.5)

    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    ax = axes[0]
    hb = ax.hexbin(x, y, gridsize=38, mincnt=1, cmap="Blues", linewidths=0.1)
    ax.plot([2, 5], [2, 5], color=COLORS["red"], linestyle="--", linewidth=1.5,
            label="Equal score after rescaling")
    fit = np.polyfit(x, y, 1)
    grid = np.linspace(max(2, x.min()), min(5, x.max()), 100)
    ax.plot(grid, fit[0] * grid + fit[1], color=COLORS["orange"], linewidth=2,
            label="Observed linear fit")
    cbar = fig.colorbar(hb, ax=ax, shrink=0.72)
    cbar.set_label("Matched albums per hexagon", fontsize=9)
    ax.set_xlabel("AOTY user score, rescaled to 0-5", fontsize=11)
    ax.set_ylabel("RYM average rating, 0-5", fontsize=11)
    ax.set_xlim(2.2, 5.0)
    ax.set_ylim(2.2, 5.0)
    ax.set_title("A  The same albums are ranked similarly", fontsize=13,
                 fontweight="bold", loc="left")
    ax.text(
        0.04, 0.95,
        f"Exact matches: {len(matched):,}\nPearson r = {pearson:.3f}\nSpearman rho = {spearman:.3f}",
        transform=ax.transAxes, va="top", fontsize=10,
        bbox=dict(boxstyle="round,pad=0.35", facecolor="white", alpha=0.9,
                  edgecolor="#999999"),
    )
    ax.legend(loc="lower right", fontsize=9)

    ax = axes[1]
    ax.hist(difference, bins=45, color=COLORS["orange"], alpha=0.82,
            edgecolor="white", linewidth=0.5)
    ax.axvspan(-0.5, 0.5, color=COLORS["green"], alpha=0.10,
               label="Within 0.5 points")
    ax.axvline(0, color="#333333", linestyle="--", linewidth=1.5)
    ax.axvline(np.median(difference), color=COLORS["red"], linewidth=2,
               label=f"Median AOTY - RYM = {np.median(difference):+.2f}")
    ax.set_xlabel("AOTY score minus RYM score (0-5 scale)", fontsize=11)
    ax.set_ylabel("Matched albums", fontsize=11)
    ax.set_title("B  Agreement remains high despite a scale offset", fontsize=13,
                 fontweight="bold", loc="left")
    ax.text(
        0.96, 0.95,
        f"{within_half:.1%} within 0.5 points\nMean offset = {difference.mean():+.2f}",
        transform=ax.transAxes, va="top", ha="right", fontsize=10,
        bbox=dict(boxstyle="round,pad=0.35", facecolor="white", alpha=0.9,
                  edgecolor="#999999"),
    )
    ax.legend(loc="upper left", fontsize=9)

    fig.suptitle(
        "Cross-platform agreement and score calibration",
        fontsize=15, fontweight="bold", y=0.98,
    )
    fig.text(
        0.5, 0.012,
        "Exact artist-title-year matches between the AOTY archive (through 2020-10) and "
        "RYM popularity snapshot (2022-03-11) | Descriptive association; snapshots use different selection rules",
        ha="center", fontsize=7, color="#777777", style="italic",
    )
    _add_evidence_banner(fig, "third-party observed archives")
    plt.tight_layout(rect=[0, 0.045, 1, 0.95])

    if save:
        return _save_figure(fig, FILES["figure_rating_dist"])
    return fig


# ================================================================
# 9. Figure 8: AI impact timeline overview
# ================================================================

def plot_ai_impact_timeline(
    observed_archives: Optional[Dict] = None,
    save: bool = True,
) -> plt.Figure:
    """
    Serpentine timeline - events alternate left/right + large text on separate lines
    Left: serpentine wavy timeline, events alternate left and right, title and description
          on clearly separate lines
    Right: AI penetration S-curve + phase color bands (enlarged)
    """
    print("\n[8/12] Generating AI impact timeline overview figure (serpentine version)...")

    events = [
        ("2022-11", "ChatGPT public release", "Prespecified external event", "#0077BB", True),
        ("2024-08", "EU AI Act enters into force", "Staged obligations begin", "#228833", True),
        ("2024-10", "AOTY top-5,000 snapshot", "Observed archive updated", "#228833", True),
        ("2025-09", "China labelling rules take effect", "Synthetic-content labels", "#228833", True),
        ("2025-10", "AOTY genre charts reweighted", "Score and rating count both matter", "#EE7733", True),
        ("2026-04", "AOTY adds CSV export", "Users can export their ratings", "#EE7733", True),
        ("2026-06", "AOTY critic charts reweighted", "Low-count scores receive less rank", "#EE7733", True),
        ("2026-07", "AOTY user charts reweighted", "Weighted score becomes default", "#CC3311", True),
    ]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 12),
                                   gridspec_kw={"width_ratios": [1.8, 1]})

    n_events = len(events)
    y_pos = np.linspace(11.0, 1.0, n_events)

    # -- First draw a wavy timeline axis --
    y_fine = np.linspace(y_pos[0], y_pos[-1], 300)
    x_wave = 0.6 * np.sin(np.linspace(0, 4.5 * np.pi, 300))
    ax1.plot(x_wave, y_fine, color="#888888", linewidth=2.5, alpha=0.3, zorder=1)

    # Left/right alternating swing amplitude (shorten the connecting lines,
    # keep the text closer to the center)
    x_swing = 1.6

    for i, (date, title, desc, color_key, is_past) in enumerate(events):
        y = y_pos[i]
        side = "right" if i % 2 == 0 else "left"
        x_node = 0.5 if side == "right" else -0.5
        x_text = x_swing if side == "right" else -x_swing
        ha_t = "left" if side == "right" else "right"

        marker = "o" if is_past else "D"
        alpha = 1.0 if is_past else 0.55
        size = 260 if is_past else 170

        # Node
        ax1.scatter(x_node, y, s=size, c=color_key, alpha=alpha,
                    edgecolors="black", linewidth=1.5, zorder=5, marker=marker)
        # Connecting line (shortened, node to the edge of the text area)
        conn_x = x_text * 0.7 if side == "right" else x_text * 0.7
        ax1.plot([x_node, conn_x], [y, y], color=color_key, linewidth=1.5,
                alpha=0.25, linestyle="--", zorder=2)

        # Date (right next to the outer edge of the text)
        date_x = x_text * 1.45 if side == "right" else x_text * 1.45
        ax1.text(date_x, y, date, fontsize=15, fontweight="bold",
                ha=ha_t, va="center", color=color_key, alpha=alpha)

        # Title
        ax1.text(x_text, y + 0.55, title, fontsize=17, fontweight="bold",
                ha=ha_t, va="bottom", color=color_key, alpha=alpha)

        # Description
        ax1.text(x_text, y - 0.55, desc, fontsize=12, ha=ha_t, va="top",
                color="#555555", alpha=alpha)

    ax1.set_xlim(-3.5, 3.5)
    ax1.set_ylim(0.2, 12)
    ax1.axis("off")
    ax1.set_title("Evidence-building sequence", fontsize=20, fontweight="bold", pad=15)

    # -- Right: evidence now available --
    if observed_archives is None:
        from analysis.observed_archive_analysis import load_observed_archives
        observed_archives = load_observed_archives(export=False)
    summary = observed_archives["summary"]
    sample_labels = [
        "Published critic excerpts", "AOTY historical albums",
        "AOTY high-rated snapshot", "RYM popular snapshot",
        "Exact cross-platform matches",
    ]
    sample_values = [
        116384,
        summary["sources"]["aoty_history_rows"],
        summary["sources"]["aoty_top5000_rows"],
        summary["sources"]["rym_top5000_rows"],
        summary["cross_platform"]["exact_matches"],
    ]
    y_bar = np.arange(len(sample_labels))
    bars = ax2.barh(
        y_bar, sample_values,
        color=[COLORS["green"], COLORS["blue"], COLORS["blue"],
               COLORS["orange"], COLORS["purple"]],
        alpha=0.84, height=0.62,
    )
    ax2.set_yticks(y_bar)
    ax2.set_yticklabels(sample_labels, fontsize=11)
    ax2.invert_yaxis()
    ax2.set_xscale("log")
    ax2.set_xlabel("Records represented (log scale)", fontsize=12)
    ax2.set_title("Observed evidence now in hand", fontsize=17, fontweight="bold")
    ax2.grid(True, axis="x", alpha=0.18)
    for bar, value in zip(bars, sample_values):
        ax2.text(
            value * 1.05, bar.get_y() + bar.get_height() / 2,
            f"{value:,}", va="center", fontsize=10, fontweight="bold",
        )
    ax2.text(
        0.03, 0.03,
        f"AOTY-RYM matched scores: r = {summary['cross_platform']['pearson_r']:.3f}\n"
        f"Within 0.5 points: {summary['cross_platform']['share_within_half_point']:.1%}\n"
        f"AOTY critic-user scores: r = {summary['aoty_critic_user']['pearson_r']:.3f}\n"
        f"RYM median review share: {summary['attention']['rym_median_review_share']:.2%}",
        transform=ax2.transAxes, fontsize=11, va="bottom",
        bbox=dict(boxstyle="round,pad=0.5", facecolor="white", alpha=0.92,
                  edgecolor="#888888"),
    )

    fig.suptitle("From an external shock to a documented evidence base",
                fontsize=19, fontweight="bold", y=0.96)
    fig.text(0.5, 0.015,
             "Sources: official policy dates, AOTY changelog, and documented third-party AOTY/RYM archives | Archive counts are not platform totals",
             ha="center", fontsize=8, color="#666666", style="italic")
    _add_evidence_banner(fig, "official dates + observed archives")
    plt.tight_layout(rect=[0, 0.05, 1, 0.94])

    if save:
        return _save_figure(fig, FILES["figure_timeline"])
    return fig


# ================================================================
# 10. Figure 9: heterogeneous user trust curves
# ================================================================

def plot_heterogeneous_trust(save: bool = True) -> plt.Figure:
    """
    Heterogeneous trust curves for four assumed user profiles.
    """
    print("\n [9/12] Generating heterogeneous user trust curves...")

    from analysis.trust_threshold_analysis import TrustThresholdModel
    user_types = [
        {"name": "Power user", "alpha": 0.55, "beta": 4.0,
         "threshold": 0.50, "color": COLORS["blue"]},
        {"name": "Regular user", "alpha": 0.70, "beta": 2.0,
         "threshold": 0.40, "color": COLORS["green"]},
        {"name": "Newcomer", "alpha": 0.80, "beta": 1.2,
         "threshold": 0.32, "color": COLORS["orange"]},
        {"name": "Casual browser", "alpha": 0.90, "beta": 0.6,
         "threshold": 0.20, "color": COLORS["purple"]},
    ]

    penetration_range = np.linspace(0, 1, 300)
    fig, ax = plt.subplots(figsize=(14, 8))

    ax.axvspan(0, 0.10, alpha=0.06, color=COLORS["green"], zorder=0)
    ax.axvspan(0.10, 0.30, alpha=0.06, color=COLORS["orange"], zorder=0)
    ax.axvspan(0.30, 1, alpha=0.06, color=COLORS["red"], zorder=0)
    ax.text(0.05, 0.02, "Assumed low-risk zone", fontsize=9, color=COLORS["green"],
           ha="center", fontweight="bold", alpha=0.5)
    ax.text(0.20, 0.02, "Assumed transition zone", fontsize=9, color=COLORS["orange"],
           ha="center", fontweight="bold", alpha=0.5)
    ax.text(0.65, 0.02, "Assumed low-trust zone", fontsize=9, color=COLORS["red"],
           ha="center", fontweight="bold", alpha=0.5)

    for user in user_types:
        model = TrustThresholdModel({
            "alpha": user["alpha"], "beta": user["beta"],
            "trust_threshold": user["threshold"],
        })
        trust_values = [model.user_trust_function(p) for p in penetration_range]
        ax.plot(penetration_range, trust_values,
               color=user["color"], linewidth=2.5, label=user["name"], zorder=3)

        threshold_line = np.full_like(penetration_range, user["threshold"])
        cross_idx = np.argmin(np.abs(np.array(trust_values) - user["threshold"]))
        cross_penetration = penetration_range[cross_idx]
        ax.scatter([cross_penetration], [user["threshold"]],
                  color=user["color"], s=60, zorder=4,
                  edgecolors="black", linewidth=0.5)
        ax.annotate(f"{user['name'].split('(')[0].strip()}\nReference = {user['threshold']:.2f}",
                   xy=(cross_penetration, user["threshold"]),
                   xytext=(cross_penetration + 0.12, user["threshold"] + 0.08),
                   fontsize=8, color=user["color"], fontweight="bold",
                   arrowprops=dict(arrowstyle="->", color=user["color"],
                                 alpha=0.4, linewidth=0.8),
                   bbox=dict(boxstyle="round,pad=0.15", facecolor="white",
                            alpha=0.7, edgecolor="none"))

    ax.set_xlabel("AI content penetration rate", fontsize=12)
    ax.set_ylabel("User trust", fontsize=12)
    ax.set_title("Heterogeneous trust thresholds across user groups",
                fontsize=14, fontweight="bold")
    ax.legend(fontsize=10, loc="lower left", framealpha=0.85)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.08)
    ax.grid(True, alpha=0.15)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.text(0.5, 0.01,
             "Uncalibrated heterogeneous-user scenarios | Group parameters and zone boundaries are assumptions for sensitivity analysis",
             ha="center", fontsize=7, color="#888888", style="italic")
    _add_evidence_banner(fig, "analyst assumptions")
    plt.tight_layout(rect=[0, 0.03, 1, 0.97])

    if save:
        return _save_figure(fig, "heterogeneous_trust.png")
    return fig


# ================================================================
# 11. Figure 10: policy intervention comparison
# ================================================================

def plot_policy_intervention(save: bool = True) -> plt.Figure:
    """
    Comparison of trust retention across four governance strategies
    Includes a "no intervention" baseline and a recommended optimal strategy
    """
    print("\n [10/12] Generating policy intervention comparison figure...")

    from analysis.trust_threshold_analysis import TrustThresholdModel
    model = TrustThresholdModel()
    policy_df = model.simulate_policy_intervention()

    fig, ax = plt.subplots(figsize=(14, 8))

    policy_styles = {
        "No intervention": {"color": COLORS["red"], "ls": "-", "lw": 2.5},
        "AI content detection": {"color": COLORS["orange"], "ls": "--", "lw": 2},
        "User education program": {"color": COLORS["blue"], "ls": "-.", "lw": 2},
        "Dual intervention (detection + education)": {"color": COLORS["green"], "ls": "-", "lw": 3},
    }

    for policy_name in policy_df["policy"].unique():
        subset = policy_df[policy_df["policy"] == policy_name]
        style = policy_styles.get(policy_name, {"color": COLORS["gray"], "ls": "-", "lw": 1.5})
        ax.plot(subset["effective_penetration"], subset["trust"],
               color=style["color"], linestyle=style["ls"],
               linewidth=style["lw"], label=policy_name, zorder=3)

    threshold = model.params["trust_threshold"]
    ax.axhline(y=threshold, color=COLORS["red"], linestyle=":",
               linewidth=1.5, alpha=0.6, zorder=2)
    ax.annotate(f"Selected trust reference = {threshold}",
               xy=(0.65, threshold + 0.02), fontsize=10,
               color=COLORS["red"], fontweight="bold")

    combined = policy_df[policy_df["policy"] == "Dual intervention (detection + education)"]
    if not combined.empty:
        last_row = combined.iloc[-1]
        ax.scatter([last_row["effective_penetration"]], [last_row["trust"]],
                  color=COLORS["green"], s=150, zorder=5,
                  marker="*", edgecolors="gold", linewidth=2)
        ax.annotate("Highest modeled retention\n(by assumed multipliers)",
                   xy=(last_row["effective_penetration"], last_row["trust"]),
                   xytext=(0.6, 0.75),
                   fontsize=10, fontweight="bold", color=COLORS["green"],
                   arrowprops=dict(arrowstyle="->", color=COLORS["green"],
                                 linewidth=1.5))

    ax.set_xlabel("AI effective penetration rate", fontsize=12)
    ax.set_ylabel("User trust", fontsize=12)
    ax.set_title("Trust retention under different policy intervention strategies",
                fontsize=14, fontweight="bold")
    ax.legend(fontsize=10, loc="upper right", framealpha=0.85)
    ax.set_xlim(0, 0.8)
    ax.set_ylim(0, 1.08)
    ax.grid(True, alpha=0.15)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.text(0.5, 0.01,
             "Deterministic policy scenarios | Relative ordering follows assumed efficacy multipliers; no observed intervention effects",
             ha="center", fontsize=8, style="italic", color="#666666")
    _add_evidence_banner(fig, "analyst assumptions")
    plt.tight_layout(rect=[0, 0.05, 1, 0.97])

    if save:
        return _save_figure(fig, "policy_intervention.png")
    return fig


# ================================================================
# 12. Figure 11: parameter sensitivity analysis
# ================================================================

def plot_sensitivity_analysis(save: bool = True) -> plt.Figure:
    """
    Sensitivity analysis of key parameters (alpha, beta, gamma) on model output
    Reveals how robust the model conclusions are to its assumptions
    """
    print("\n [11/12] Generating parameter sensitivity analysis figure...")

    from analysis.trust_threshold_analysis import TrustThresholdModel
    penetration_range = np.linspace(0, 1, 300)
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    ax = axes[0]
    for alpha in [0.5, 0.6, 0.7, 0.8, 0.9]:
        model = TrustThresholdModel({"alpha": alpha, "beta": 2.0, "gamma": 0.3})
        trust = [model.user_trust_function(p) for p in penetration_range]
        ax.plot(penetration_range, trust, linewidth=2, label=f"alpha={alpha}", alpha=0.8)
    ax.set_title("alpha (preference) sensitivity", fontsize=12, fontweight="bold")
    ax.set_xlabel("AI penetration", fontsize=10); ax.set_ylabel("Trust", fontsize=10)
    ax.legend(fontsize=8, framealpha=0.85); ax.grid(True, alpha=0.15)
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    ax = axes[1]
    for beta in [0.5, 1.0, 2.0, 3.0, 5.0]:
        model = TrustThresholdModel({"alpha": 0.7, "beta": beta, "gamma": 0.3})
        trust = [model.user_trust_function(p) for p in penetration_range]
        ax.plot(penetration_range, trust, linewidth=2, label=f"beta={beta}", alpha=0.8)
    ax.set_title("beta (discrimination) sensitivity", fontsize=12, fontweight="bold")
    ax.set_xlabel("AI penetration", fontsize=10); ax.set_ylabel("Trust", fontsize=10)
    ax.legend(fontsize=8, framealpha=0.85); ax.grid(True, alpha=0.15)
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    ax = axes[2]
    for gamma in [0.0, 0.15, 0.3, 0.45, 0.6]:
        model = TrustThresholdModel({"alpha": 0.7, "beta": 2.0, "gamma": gamma})
        trust = [model.user_trust_function(p) for p in penetration_range]
        ax.plot(penetration_range, trust, linewidth=2, label=f"gamma={gamma}", alpha=0.8)
    ax.set_title("gamma (network) sensitivity", fontsize=12, fontweight="bold")
    ax.set_xlabel("AI penetration", fontsize=10); ax.set_ylabel("Trust", fontsize=10)
    ax.legend(fontsize=8, framealpha=0.85); ax.grid(True, alpha=0.15)
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    fig.suptitle("Parameter Sensitivity Analysis", fontsize=14, fontweight="bold", y=1.02)
    fig.text(0.5, 0.01,
             "One-at-a-time sensitivity analysis of uncalibrated assumptions; curve changes show model dependence, not empirical robustness.",
             ha="center", fontsize=8, style="italic", color="#666666")
    _add_evidence_banner(fig, "analyst assumptions")
    plt.tight_layout(rect=[0, 0.05, 1, 0.95])
    if save:
        return _save_figure(fig, "sensitivity_analysis.png")
    return fig


# ================================================================
# 13. Figure 12: feature correlation heatmap
# ================================================================

def plot_feature_correlation_heatmap(save: bool = True) -> plt.Figure:
    """
    Correlation matrix heatmap of the AI detection features
    Helps understand feature redundancy and independence
    """
    print("\n [12/12] Generating feature correlation heatmap...")

    from analysis.ai_review_analysis import (
        AIReviewAnalyzer, HUMAN_REVIEWS, AI_REVIEWS, HUMAN_CORPUS_LABEL,
    )
    analyzer = AIReviewAnalyzer()
    feature_df = analyzer.get_feature_comparison_df(HUMAN_REVIEWS, AI_REVIEWS)

    compare_cols = [
        "vocabulary_diversity", "avg_sentence_length",
        "emotional_words", "specific_references",
        "technical_terms", "first_person_count",
        "filler_words", "sentence_length_std",
        "allcaps_ratio", "number_references", "contrastive_words",
    ]
    labels_cn = {
        "vocabulary_diversity": "Vocabulary diversity", "avg_sentence_length": "Avg. sentence length",
        "emotional_words": "Emotional words", "specific_references": "Specific references",
        "technical_terms": "Technical terms", "first_person_count": "First person",
        "filler_words": "Filler words", "sentence_length_std": "Sentence length SD",
        "allcaps_ratio": "Capital ratio", "number_references": "Number references",
        "contrastive_words": "Contrastive words",
    }

    corr_matrix = feature_df[compare_cols].corr().rename(index=labels_cn, columns=labels_cn)

    fig, ax = plt.subplots(figsize=(12, 10))
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)
    cmap = sns.diverging_palette(250, 10, s=80, l=50, as_cmap=True)
    sns.heatmap(corr_matrix, mask=mask, cmap=cmap, vmin=-1, vmax=1,
                center=0, annot=True, fmt=".2f", linewidths=0.5,
                square=True, cbar_kws={"shrink": 0.7, "label": "Pearson r"}, ax=ax)
    ax.set_title("Correlation matrix of AI detection language features", fontsize=14, fontweight="bold")
    ax.set_xlabel("Features", fontsize=11)
    ax.set_ylabel("Features", fontsize=11)

    fig.text(0.5, 0.01,
             f"N=30 | Human: {HUMAN_CORPUS_LABEL} | AI: 15 controlled assistant-style texts | Correlations are exploratory",
             ha="center", fontsize=7, color="#888888", style="italic")
    _add_evidence_banner(fig, "observed human text + controlled AI text")
    plt.tight_layout(rect=[0, 0.03, 1, 0.97])

    if save:
        return _save_figure(fig, "feature_correlation_heatmap.png")
    return fig


# ================================================================
# 14. Batch generation of all figures
# ================================================================

def generate_all_figures(
    data: Optional[pd.DataFrame] = None,
    human_reviews: Optional[List[str]] = None,
    ai_reviews: Optional[List[str]] = None,
    observed_archives: Optional[Dict] = None,
) -> List[Path]:
    """
    Batch-generate figures with explicit evidence-class labels.
    """
    print("\n" + "=" * 60)
    print("[Visualization] Batch generating 12 figures with source notes")
    print("=" * 60)

    try:
        from analysis.ai_review_analysis import HUMAN_REVIEWS, AI_REVIEWS
    except ImportError:
        from analysis.ai_review_analysis import HUMAN_REVIEWS, AI_REVIEWS

    if human_reviews is None:
        human_reviews = HUMAN_REVIEWS
    if ai_reviews is None:
        ai_reviews = AI_REVIEWS

    generated = []

    has_structural_data = data is not None and not data.empty
    chart_plans = [
        ("[1/12] Structural break analysis", lambda: plot_structural_break(data)
         if has_structural_data else print(
             "  [INFO] skipped: no empirical time-series rows available"
         )),
        ("[2/12] AI vs human review feature comparison", lambda: plot_ai_feature_comparison(human_reviews, ai_reviews)),
        ("[3/12] Trust threshold model", lambda: plot_trust_threshold()),
        ("[4/12] Competitive landscape positioning", lambda: plot_competitive_landscape()),
        ("[5/12] Four-dimensional AI impact framework", lambda: plot_four_dimensions()),
        ("[6/12] Observed genre profile heatmap", lambda: plot_genre_impact_heatmap(
            observed_archives=observed_archives
        )),
        ("[7/12] Cross-platform rating comparison", lambda: plot_rating_distribution_evolution(
            data=data, observed_archives=observed_archives
        )),
        ("[8/12] AI impact timeline", lambda: plot_ai_impact_timeline(
            observed_archives=observed_archives
        )),
        ("[9/12] Heterogeneous user trust curves", lambda: plot_heterogeneous_trust()),
        ("[10/12] Policy intervention comparison", lambda: plot_policy_intervention()),
        ("[11/12] Parameter sensitivity analysis", lambda: plot_sensitivity_analysis()),
        ("[12/12] Feature correlation heatmap", lambda: plot_feature_correlation_heatmap()),
    ]

    for plan_name, plan_func in chart_plans:
        print(f"\n{plan_name}")
        try:
            result = plan_func()
            if result is not None:
                generated.append(result)
        except Exception as e:
            print(f"  [WARN] generation failed: {e}")
            import traceback
            traceback.print_exc()

    n_success = len(generated)
    n_total = len(chart_plans)
    n_skipped = 0 if has_structural_data else 1
    print("\n" + "=" * 60)
    print(
        f"[OK] visualization complete - {n_success} generated, "
        f"{n_skipped} skipped, {n_total} planned"
    )
    print(f"   output directory: {ANALYSIS_FIGURES_DIR}")
    for g in generated:
        if hasattr(g, 'name'):
            size_kb = (ANALYSIS_FIGURES_DIR / g.name).stat().st_size // 1024
            print(f"   [FILE] {g.name} ({size_kb}KB)")
    print("=" * 60)

    return generated


# ================================================================
# 15. Standalone entry point
# ================================================================

if __name__ == "__main__":
    generate_all_figures()
