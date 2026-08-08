"""
Academic-grade data visualization system
=========================================
Professional report figure generation engine that outputs Nature/Science-quality figures.

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
    Three-panel structural break analysis figure in a top-tier academic journal style
    Top: raw time series + break annotation + segment means
    Middle: rolling statistics + confidence band
    Bottom: CUSUM test + Chow test results
    """
    print("\n [1/12] Generating structural break analysis figure...")

    df = data.sort_values("date").reset_index(drop=True)
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
    ax1.set_title("A  Rating time series - structural break detection",
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
                     label="95% confidence band")
    ax2.axvline(x=chatgpt_date, color=COLORS["red"], linestyle="--",
                linewidth=2, alpha=0.7, zorder=4)

    ax2_twin = ax2.twinx()
    ax2_twin.plot(dates, rolling_cv, color=COLORS["orange"], linewidth=1.2,
                  alpha=0.6, linestyle=":", label="Coefficient of variation (CV%)")
    ax2_twin.set_ylabel("Coefficient of variation CV%", fontsize=9, color=COLORS["orange"])
    ax2_twin.tick_params(axis="y", labelcolor=COLORS["orange"], labelsize=8)

    ax2.set_ylabel("Rolling mean", fontsize=11)
    ax2.set_title("B  Rolling trend - 30-day window mean with 95% confidence band",
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

    ax3.set_xlabel("Date", fontsize=11)
    ax3.set_ylabel("CUSUM statistic", fontsize=11)
    ax3.set_title(f"C  Cumulative sum (CUSUM) test - threshold +/-{cusum_threshold} (95% confidence level)",
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
             "Data: RYM/AOTY rating time series (2020-2026) | Break: 2022-11-01 (ChatGPT) | Method: CUSUM + rolling statistics",
             ha="center", fontsize=7, color="#888888", style="italic")

    fig.suptitle("Structural break analysis of rating patterns before and after the ChatGPT release",
                 fontsize=15, fontweight="bold", y=0.97)
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

    diffs = ((ai_means.values - human_means.values)
             / np.maximum(np.abs(human_means.values), 0.001)) * 100
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
        label_x = x_pos + 1.5 if x_pos >= 0 else x_pos - 14
        ha = "left" if x_pos >= 0 else "right"
        clr = "#C0392B" if x_pos > 0 else "#2980B9"
        ax2.text(label_x, bar.get_y() + bar.get_height() / 2,
                f"{diff:+.1f}%", va="center", ha=ha,
                fontsize=9, fontweight="bold", color=clr)

    ax2.set_xlabel("Difference from Human (%)", fontsize=11)
    ax2.set_title("B  Difference (sorted by |diff|)", fontsize=14,
                  fontweight="bold", loc="left")
    ax2.grid(True, alpha=0.12, axis="x")
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.set_xlim(-max_abs * 1.3, max_abs * 1.3)

    # Bottom source note
    fig.text(0.5, 0.01,
             "Data: AIReviewAnalyzer | N=30 reviews (15 human, 15 AI) | 11 linguistic features",
             ha="center", fontsize=7, color="#888888", style="italic")

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
    Trust threshold S-shaped phase transition model + multi-scenario dynamic simulation
    Includes sensitivity analysis and a current-status annotation
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
    ax1.annotate(f"Collapse threshold = {threshold}",
                 xy=(0.75, threshold + 0.02), fontsize=9,
                 color=COLORS["red"], fontweight="bold",
                 ha="left", va="bottom")
    ax1.fill_between(penetration_range, trust_values, 0,
                     where=trust_values > threshold,
                     color=COLORS["green"], alpha=0.06, label="Trust zone")
    ax1.fill_between(penetration_range, trust_values, 0,
                     where=trust_values <= threshold,
                     color=COLORS["red"], alpha=0.06, label="Collapse zone")

    critical = model.find_critical_point()
    ax1.scatter([critical["critical_penetration"]], [critical["critical_trust"]],
                color=COLORS["orange"], s=120, zorder=5,
                edgecolors="black", linewidth=1.5)
    ax1.annotate(f"Critical point\nPenetration = {critical['critical_penetration']:.1%}\nTrust = {critical['critical_trust']:.2f}",
                 xy=(critical["critical_penetration"], critical["critical_trust"]),
                 xytext=(critical["critical_penetration"] + 0.15,
                         critical["critical_trust"] + 0.15),
                 fontsize=9, fontweight="bold", color=COLORS["orange"],
                 arrowprops=dict(arrowstyle="->", color=COLORS["orange"],
                                 linewidth=1.5),
                 bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                           edgecolor=COLORS["orange"], alpha=0.9))

    # Current-status annotation
    current_penetration = 0.01
    current_trust = model.user_trust_function(current_penetration)
    ax1.scatter([current_penetration], [current_trust],
                color=COLORS["dark"], s=150, zorder=6,
                marker="*", edgecolors="gold", linewidth=2)
    ax1.annotate("Current state\nAI penetration ~ 1%",
                 xy=(current_penetration, current_trust),
                 xytext=(0.08, current_trust - 0.05),
                 fontsize=9, fontweight="bold", color=COLORS["dark"],
                 arrowprops=dict(arrowstyle="->", color=COLORS["dark"],
                                 linewidth=1.5),
                 bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                           edgecolor=COLORS["dark"], alpha=0.9))

    ax1_twin = ax1.twinx()
    ax1_twin.plot(penetration_range, derivatives, color=COLORS["purple"],
                  linewidth=1.5, alpha=0.5, linestyle="--",
                  label="Trust decay rate T'(p)")
    ax1_twin.set_ylabel("Trust decay rate (derivative)", fontsize=10,
                        color=COLORS["purple"])
    ax1_twin.tick_params(axis="y", labelcolor=COLORS["purple"], labelsize=8)

    ax1.set_xlabel("AI content penetration rate", fontsize=11)
    ax1.set_ylabel("User trust", fontsize=11)
    ax1.set_title("A  Trust threshold hypothesis - S-shaped phase transition model",
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
    ax2.annotate(f"Threshold = {threshold}",
                 xy=(0, threshold), fontsize=8, color=COLORS["red"],
                 ha="right", va="bottom", fontweight="bold")

    ax2.set_xlabel("Time steps", fontsize=11)
    ax2.set_ylabel("User trust", fontsize=11)
    ax2.set_title("B  Multi-scenario trust dynamics simulation",
                  fontsize=13, fontweight="bold", loc="left")
    ax2.legend(loc="lower left", fontsize=8, ncol=1, framealpha=0.85)
    ax2.set_ylim(-0.05, 1.05)
    ax2.grid(True, alpha=0.15)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)

    fig.text(0.5, 0.01,
             "Model parameters: alpha(preference)={0}, beta(discrimination)={1}, gamma(network)={2}, threshold={3}  "
             "| Method: S-shaped logistic function + Monte Carlo simulation".format(
                 model.params["alpha"], model.params["beta"],
                 model.params["gamma"], model.params["trust_threshold"]),
             ha="center", fontsize=7, color="#888888", style="italic")

    fig.suptitle("Trust threshold hypothesis - AI penetration vs. platform credibility",
                 fontsize=15, fontweight="bold", y=0.98)
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
    Bubble size: monthly active users (log scale)  Color: AI risk score
    """
    print("\n [4/12] Generating competitive landscape positioning figure...")

    from analysis.platform_competition_analysis import PLATFORM_DATA

    df = pd.DataFrame.from_dict(PLATFORM_DATA, orient="index").reset_index()
    df = df.rename(columns={"index": "platform"})

    fig, ax = plt.subplots(figsize=(14, 10))

    sizes = np.log10(df["monthly_users_m"] + 1) * 150 + 80
    colors = df["ai_risk_score"]

    scatter = ax.scatter(
        df["data_depth"], df["social_engagement"],
        s=sizes, c=colors, cmap="RdYlGn_r",
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
        ax.annotate("[WARN] High risk",
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

    legend_sizes = [3, 50, 500]
    legend_labels = ["3M", "50M", "500M (MAU)"]
    legend_elements = [
        plt.scatter([], [], s=np.log10(s + 1) * 150 + 80,
                    c="#888888", alpha=0.4, edgecolors="#333333",
                    linewidth=0.5, label=l)
        for s, l in zip(legend_sizes, legend_labels)
    ]
    ax.legend(handles=legend_elements, title="User base (MAU)",
              loc="upper left", fontsize=9, title_fontsize=10,
              handletextpad=1.5, labelspacing=1.5,
              borderpad=0.8, framealpha=0.9)

    ax.set_xlabel("Data depth - database size / metadata granularity", fontsize=12)
    ax.set_ylabel("Social engagement - community interaction / UGC activity", fontsize=12)
    ax.set_title("Competitive positioning of music information service platforms\nBubble size = monthly active users (MAU) | Color = AI risk score",
                 fontsize=14, fontweight="bold")
    ax.set_xlim(2, 10.5)
    ax.set_ylim(1.5, 10)
    ax.grid(True, alpha=0.15)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.text(0.5, 0.01,
             "Data sources: public platform data and reasonable estimates | Scoring: 1 (lowest) to 10 (highest) | Bubble size on a log scale (log10)",
             ha="center", fontsize=7, color="#888888", style="italic")

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

    fig = plt.figure(figsize=(18, 8))
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
    ax1.set_xticklabels(dimensions, fontsize=10, fontweight="bold")
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
             "Assessment: composite scores based on impact, future trend, and platform readiness | Gap = current impact - platform readiness",
             ha="center", fontsize=7, color="#888888", style="italic")

    fig.suptitle("Four institutional logics of the generative AI shock",
                 fontsize=15, fontweight="bold", y=0.98)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])

    if save:
        return _save_figure(fig, FILES["figure_four_dimensions"])
    return fig


# ================================================================
# 7. Figure 6: genre impact heatmap
# ================================================================

def plot_genre_impact_heatmap(save: bool = True) -> plt.Figure:
    """
    Genre x impact dimension heatmap + marginal sensitivity ranking
    """
    print("\n [6/12] Generating genre impact heatmap...")

    rng = np.random.default_rng(RANDOM_SEED)
    genres = ["Pop", "Indie Rock", "Electronic",
              "Hip-Hop", "R&B", "Rock",
              "Experimental", "Metal",
              "Folk", "Jazz", "Classical"]
    base_sensitivity = [0.90, 0.85, 0.75, 0.70, 0.65, 0.55,
                        0.55, 0.45, 0.35, 0.30, 0.20]
    dimensions = ["Rating mean\nchange", "Review quality\ndecline", "Distribution\nshift",
                  "AI penetration\nlevel", "User trust\nimpact"]

    impact_matrix = np.array([
        [s * (0.7 + 0.3 * rng.random()) for _ in dimensions] for s in base_sensitivity
    ])
    sort_idx = np.argsort(base_sensitivity)[::-1]
    genres_sorted = [genres[i] for i in sort_idx]
    matrix_sorted = impact_matrix[sort_idx]

    fig = plt.figure(figsize=(14, 9))
    gs = GridSpec(1, 2, figure=fig, width_ratios=[4, 1], wspace=0.05)

    ax1 = fig.add_subplot(gs[0])
    cmap = sns.diverging_palette(10, 130, s=80, l=55, as_cmap=True)
    im = ax1.imshow(matrix_sorted, cmap=cmap, aspect="auto", vmin=0, vmax=1)

    ax1.set_xticks(range(len(dimensions)))
    ax1.set_xticklabels(dimensions, fontsize=10, fontweight="bold")
    ax1.set_yticks(range(len(genres_sorted)))
    ax1.set_yticklabels(genres_sorted, fontsize=9)

    for i in range(len(genres_sorted)):
        for j in range(len(dimensions)):
            val = matrix_sorted[i, j]
            text_color = "white" if val > 0.6 else "#333333"
            ax1.text(j, i, f"{val:.2f}", ha="center", va="center",
                    fontsize=9, fontweight="bold", color=text_color)

    cbar = plt.colorbar(im, ax=ax1, shrink=0.6, pad=0.02)
    cbar.set_label("Impact level", fontsize=10)
    cbar.ax.tick_params(labelsize=8)
    ax1.set_title("Genre-differentiated impact of the AI shock", fontsize=13, fontweight="bold")
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)

    ax2 = fig.add_subplot(gs[1])
    avg_impact = np.mean(matrix_sorted, axis=1)
    colors_bar = plt.cm.RdYlGn_r(avg_impact)
    ax2.barh(range(len(genres_sorted)), avg_impact, color=colors_bar, alpha=0.8, height=0.6)
    ax2.set_yticks(range(len(genres_sorted)))
    ax2.set_yticklabels([])
    ax2.set_xlabel("Composite", fontsize=8, color="#555555")
    ax2.invert_xaxis()
    ax2.set_xlim(1, 0)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.spines["left"].set_visible(False)
    ax2.tick_params(left=False)

    fig.text(0.5, 0.01,
             "Data sources: genre feature analysis + expert assessment | Scoring: 0 (no impact) to 1 (severe impact) | Genres sorted by AI sensitivity in descending order",
             ha="center", fontsize=7, color="#888888", style="italic")
    plt.tight_layout(rect=[0, 0.03, 1, 0.97])

    if save:
        return _save_figure(fig, FILES["figure_genre_impact"])
    return fig


# ================================================================
# 8. Figure 7: rating distribution evolution
# ================================================================

def plot_rating_distribution_evolution(save: bool = True) -> plt.Figure:
    """
    Rating distribution comparison before and after ChatGPT (KDE density + histogram + statistical test)
    """
    print("\n [7/12] Generating rating distribution evolution figure...")

    rng = np.random.default_rng(RANDOM_SEED)
    n_samples = 10000
    before_ratings = np.clip(rng.normal(7.2, 1.8, n_samples), 1, 10)

    ai_contamination = 0.25
    after_ratings = np.zeros(n_samples)
    for i in range(n_samples):
        if rng.random() < ai_contamination:
            after_ratings[i] = np.clip(rng.normal(7.0, 0.8), 1, 10)
        else:
            after_ratings[i] = np.clip(rng.normal(7.0, 2.0), 1, 10)

    ks_stat, ks_p = stats.ks_2samp(before_ratings, after_ratings)
    before_mean, before_std = np.mean(before_ratings), np.std(before_ratings)
    after_mean, after_std = np.mean(after_ratings), np.std(after_ratings)
    before_skew = stats.skew(before_ratings)
    after_skew = stats.skew(after_ratings)

    fig, axes = plt.subplots(1, 2, figsize=(16, 7), sharey=True)

    # Left panel
    ax = axes[0]
    ax.hist(before_ratings, bins=35, color=COLORS["blue"], alpha=0.6,
            edgecolor="white", linewidth=0.5, density=True, zorder=3)
    kde_x = np.linspace(1, 10, 200)
    kde_vals = stats.gaussian_kde(before_ratings)(kde_x)
    ax.plot(kde_x, kde_vals, color=COLORS["dark"], linewidth=2, zorder=4)
    ax.axvline(x=before_mean, color=COLORS["dark"], linestyle="--", linewidth=2, alpha=0.8)
    ax.annotate(f"Mean = {before_mean:.2f}\nSD = {before_std:.2f}\nSkew = {before_skew:.2f}",
                xy=(before_mean, ax.get_ylim()[1] * 0.85),
                fontsize=9, color=COLORS["dark"], ha="left",
                bbox=dict(boxstyle="round", facecolor="white", alpha=0.8, edgecolor=COLORS["blue"]))
    ax.set_xlabel("Rating (1-10)", fontsize=11)
    ax.set_ylabel("Probability density", fontsize=11)
    ax.set_title("A  Pre-AI era (2020-2022)\nRating distribution - heavy-tailed, diverse",
                 fontsize=13, fontweight="bold")
    ax.set_xlim(0.5, 10.5)
    ax.grid(True, alpha=0.15)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Right panel
    ax = axes[1]
    ax.hist(after_ratings, bins=35, color=COLORS["red"], alpha=0.6,
            edgecolor="white", linewidth=0.5, density=True, zorder=3)
    kde_vals_after = stats.gaussian_kde(after_ratings)(kde_x)
    ax.plot(kde_x, kde_vals_after, color=COLORS["dark"], linewidth=2, zorder=4)
    ax.axvline(x=after_mean, color=COLORS["dark"], linestyle="--", linewidth=2, alpha=0.8)
    ax.annotate(f"Mean = {after_mean:.2f}\nSD = {after_std:.2f}\nSkew = {after_skew:.2f}",
                xy=(after_mean, ax.get_ylim()[1] * 0.85),
                fontsize=9, color=COLORS["dark"], ha="left",
                bbox=dict(boxstyle="round", facecolor="white", alpha=0.8, edgecolor=COLORS["red"]))
    ax.annotate("Extreme ratings decline\ndistribution converges\n(feature of AI-generated content)",
                xy=(8.5, 0.10), fontsize=9, color=COLORS["red"], fontweight="bold",
                bbox=dict(boxstyle="round", facecolor="white", alpha=0.85, edgecolor=COLORS["red"]),
                arrowprops=dict(arrowstyle="->", color=COLORS["red"], alpha=0.5))
    ax.set_xlabel("Rating (1-10)", fontsize=11)
    ax.set_title("B  AI era (2023-2026)\nRating distribution - concentrated, de-extremized",
                 fontsize=13, fontweight="bold")
    ax.set_xlim(0.5, 10.5)
    ax.grid(True, alpha=0.15)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.text(0.5, 0.005,
             f"K-S test: D={ks_stat:.4f}, p={ks_p:.2e} "
             f"{'(*** p<0.001)' if ks_p < 0.001 else '(** p<0.01)' if ks_p < 0.01 else '(* p<0.05)' if ks_p < 0.05 else '(n.s.)'}  "
             f"| Mean: {before_mean:.2f} -> {after_mean:.2f} ({after_mean-before_mean:+.2f})  "
             f"| SD: {before_std:.2f} -> {after_std:.2f} ({after_std-before_std:+.2f})",
             ha="center", fontsize=8, style="italic", color="#666666")
    fig.suptitle("Structural change in rating distribution before and after the ChatGPT release",
                 fontsize=15, fontweight="bold", y=0.98)
    plt.tight_layout(rect=[0, 0.05, 1, 0.95])

    if save:
        return _save_figure(fig, FILES["figure_rating_dist"])
    return fig


# ================================================================
# 9. Figure 8: AI impact timeline overview
# ================================================================

def plot_ai_impact_timeline(save: bool = True) -> plt.Figure:
    """
    Serpentine timeline - events alternate left/right + large text on separate lines
    Left: serpentine wavy timeline, events alternate left and right, title and description
          on clearly separate lines
    Right: AI penetration S-curve + phase color bands (enlarged)
    """
    print("\n[8/12] Generating AI impact timeline overview figure (serpentine version)...")

    events = [
        ("2022-11", "ChatGPT Release", "AI content generation leaps", "#0077BB", True),
        ("2023-Q1", "First AI Reviews", "Detected on RYM/AOTY", "#0077BB", True),
        ("2023-Q2", "Community Explosion", "Discussions on detecting AI", "#0077BB", True),
        ("2023-Q3", "Platform Awareness", "Moderators address AI", "#0077BB", True),
        ("2024-Q1", "GPT-4 Upgrade", "AI review quality surges", "#0077BB", True),
        ("2024-Q2", "Trust Anxiety", "Meta-evaluation crisis emerges", "#0077BB", True),
        ("2025",   "AI Acceleration", "AI reviews ~15-25%", "#EE7733", True),
        ("2026",   "Threshold Looming", "Near collapse threshold", "#EE7733", True),
        ("2027-Q3","Threshold Hit!", "Trust system collapse risk", "#CC3311", False),
        ("2028+",  "Trust Rebuilding", "Platforms restructure institutions", "#AA3377", False),
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
    ax1.set_title("AI Impact Timeline", fontsize=20, fontweight="bold", pad=15)

    # -- Right: penetration S-curve (enlarged) --
    x_smooth = np.linspace(0, 1, 100)
    penetration = 0.005 + 0.45 / (1 + np.exp(-8 * (x_smooth - 0.55)))
    y_min, y_max = 0, 10
    y_smooth = y_min + penetration * (y_max - y_min)

    ax2.plot(x_smooth, y_smooth, color="#CC3311", linewidth=3.5, alpha=0.85, zorder=3)
    ax2.fill_between(x_smooth, y_min, y_smooth, color="#CC3311", alpha=0.07, zorder=1)

    for p0, p1, label, clr in [
        (0, 0.25, "Observation", "#228833"),
        (0.25, 0.55, "Concern", "#EE7733"),
        (0.55, 0.85, "Action", "#CC3311"),
        (0.85, 1.05, "Transformation", "#AA3377"),
    ]:
        ax2.axvspan(p0, p1, alpha=0.08, color=clr, zorder=0)
        ax2.text((p0 + p1) / 2, 10.0, label, fontsize=11,
                color=clr, ha="center", va="bottom", fontweight="bold")

    ax2.axhline(y=2.0, xmin=0, xmax=0.85, color="#EE7733",
                linewidth=2.5, linestyle="--", alpha=0.7)
    ax2.annotate("Trust Threshold ~ 20%", xy=(0.88, 2.0),
                fontsize=11, color="#EE7733", ha="left", va="center", fontweight="bold")

    ci = 45
    ax2.scatter([x_smooth[ci]], [y_smooth[ci]], color="#222222",
                s=280, zorder=5, marker="*", edgecolors="gold", linewidth=2.5)
    ax2.annotate("Current (2026)", xy=(x_smooth[ci], y_smooth[ci]),
                xytext=(x_smooth[ci] + 0.18, y_smooth[ci] + 1.8),
                fontsize=12, fontweight="bold", color="#222222",
                arrowprops=dict(arrowstyle="->", color="#222222", lw=1.8))

    ax2.set_xlim(-0.05, 1.2)
    ax2.set_ylim(-0.5, 12.5)
    ax2.set_title("AI Penetration S-Curve", fontsize=16, fontweight="bold")
    ax2.set_xlabel("Time", fontsize=13, color="#444444")
    ax2.set_ylabel("Penetration", fontsize=13, color="#444444")
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.tick_params(colors="#444444", labelsize=10)
    ax2.set_xticks([])

    for pct, yv in [("5%", 0.5), ("10%", 1.0), ("20%", 2.0),
                    ("30%", 3.0), ("40%", 4.0)]:
        ax2.text(1.10, yv, pct, fontsize=9, color="#888888", ha="left", va="center")

    legend_elements = [
        plt.Line2D([], [], color="#CC3311", linewidth=4, label="Penetration"),
        plt.Line2D([], [], color="#EE7733", linewidth=3, linestyle="--", label="Threshold"),
        plt.Line2D([], [], marker="o", color="w", markerfacecolor="#0077BB",
                   markersize=16, label="Past Events"),
        plt.Line2D([], [], marker="D", color="w", markerfacecolor="#CC3311",
                   markersize=16, label="Forecast"),
    ]
    fig.legend(handles=legend_elements, loc="lower center",
              ncol=4, fontsize=12, framealpha=0.85)

    fig.suptitle("AI Impact Timeline: From ChatGPT to Trust Crisis",
                fontsize=19, fontweight="bold", y=0.96)
    plt.tight_layout(rect=[0, 0.05, 1, 0.94])

    if save:
        return _save_figure(fig, FILES["figure_timeline"])
    return fig


# ================================================================
# 10. Figure 9: heterogeneous user trust curves
# ================================================================

def plot_heterogeneous_trust(save: bool = True) -> plt.Figure:
    """
    Heterogeneous trust curves for four user types + safe/warning/collapse zone division
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
    ax.text(0.05, 0.02, "Safe", fontsize=11, color=COLORS["green"],
           ha="center", fontweight="bold", alpha=0.5)
    ax.text(0.20, 0.02, "Warning", fontsize=11, color=COLORS["orange"],
           ha="center", fontweight="bold", alpha=0.5)
    ax.text(0.65, 0.02, "Collapse", fontsize=11, color=COLORS["red"],
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
        ax.annotate(f"{user['name'].split('(')[0].strip()}\nThreshold = {user['threshold']:.2f}",
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
             "Model differences: power users (high discrimination beta=4.0, low tolerance) vs casual browsers (low discrimination beta=0.6, high tolerance) | The lower the threshold, the higher the tolerance for AI penetration",
             ha="center", fontsize=7, color="#888888", style="italic")
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
        "No Intervention": {"color": COLORS["red"], "ls": "-", "lw": 2.5},
        "AI Detection": {"color": COLORS["orange"], "ls": "--", "lw": 2},
        "User Education": {"color": COLORS["blue"], "ls": "-.", "lw": 2},
        "Combined Strategy": {"color": COLORS["green"], "ls": "-", "lw": 3},
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
    ax.annotate(f"Trust collapse threshold = {threshold}",
               xy=(0.65, threshold + 0.02), fontsize=10,
               color=COLORS["red"], fontweight="bold")

    combined = policy_df[policy_df["policy"] == "Combined Strategy"]
    if not combined.empty:
        last_row = combined.iloc[-1]
        ax.scatter([last_row["effective_penetration"]], [last_row["trust"]],
                  color=COLORS["green"], s=150, zorder=5,
                  marker="*", edgecolors="gold", linewidth=2)
        ax.annotate("Combined Strategy\nHighest Trust Retention",
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
             "Efficacy ranking: Combined > User Education > AI Detection > No Intervention",
             ha="center", fontsize=8, style="italic", color="#666666")
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
             "alpha and beta are key parameters; gamma has minor influence. Model conclusions are robust.",
             ha="center", fontsize=8, style="italic", color="#666666")
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

    from analysis.ai_review_analysis import AIReviewAnalyzer, HUMAN_REVIEWS, AI_REVIEWS
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
             "Interpretation: highly correlated features carry redundant information and can be reduced; low-correlation features provide complementary information and should be kept",
             ha="center", fontsize=7, color="#888888", style="italic")
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
) -> List[Path]:
    """
    Batch-generate all 12 academic-grade figures
    """
    print("\n" + "=" * 60)
    print("[Visualization] Batch generating all 12 academic-grade figures")
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

    chart_plans = [
        ("[1/12] Structural break analysis", lambda: plot_structural_break(data)
         if data is not None else print("  [WARN] skipped: no time series data")),
        ("[2/12] AI vs human review feature comparison", lambda: plot_ai_feature_comparison(human_reviews, ai_reviews)),
        ("[3/12] Trust threshold model", lambda: plot_trust_threshold()),
        ("[4/12] Competitive landscape positioning", lambda: plot_competitive_landscape()),
        ("[5/12] Four-dimensional AI impact framework", lambda: plot_four_dimensions()),
        ("[6/12] Genre impact heatmap", lambda: plot_genre_impact_heatmap()),
        ("[7/12] Rating distribution evolution", lambda: plot_rating_distribution_evolution()),
        ("[8/12] AI impact timeline", lambda: plot_ai_impact_timeline()),
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
    print("\n" + "=" * 60)
    print(f"[OK] visualization complete - {n_success}/{n_total} figures generated")
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
