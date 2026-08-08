#!/usr/bin/env python
"""
Full Analysis Runner (Fast Version)
===================================
Skip the time-consuming web scraping and use synthetic data directly,
run all core analyses, generate all figures, and produce the report.
"""

import sys
from pathlib import Path

_SRC = str(Path(__file__).resolve().parent)
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

import numpy as np
import pandas as pd

from config import print_banner, CHATGPT_RELEASE_DATE, FIGURES_DIR, ANALYSIS_FIGURES_DIR, REPORT_META


def generate_base_data() -> pd.DataFrame:
    """Generate the base time series data"""
    rng = np.random.default_rng(42)
    dates = pd.date_range("2020-01-01", "2026-07-01", freq="7D")
    n = len(dates)

    metric = np.where(
        dates < pd.Timestamp(CHATGPT_RELEASE_DATE),
        3.5 + 0.3 * rng.standard_normal(n),
        3.2 + 0.5 * rng.standard_normal(n),
    )

    return pd.DataFrame({
        "date": dates,
        "avg_rating": np.clip(metric, 1, 5),
        "rating_count": rng.poisson(100, n).astype(float),
        "review_ratio": np.clip(0.3 + 0.1 * rng.standard_normal(n), 0.05, 0.6),
    })


def main():
    # Initialize matplotlib fonts (must be after seaborn)
    import matplotlib.pyplot as plt

    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] = ['Times New Roman', 'SimSun']
    plt.rcParams['mathtext.fontset'] = 'stix'
    plt.rcParams['axes.unicode_minus'] = False

    print_banner()
    print("\n" + "=" * 60)
    print("[INFO] Starting the full analysis pipeline (fast mode)")
    print("=" * 60)

    data = generate_base_data()

    # ============================================================
    # 1. Time series structural breakpoint analysis
    # ============================================================
    print("\n" + "=" * 60)
    print("== 1/6: Structural breakpoint analysis")
    print("=" * 60)

    from analysis.structural_break_analysis import run_full_analysis
    break_results = run_full_analysis(data)

    # ============================================================
    # 2. AI review detection and feature analysis
    # ============================================================
    print("\n" + "=" * 60)
    print("== 2/6: AI review detection and feature analysis")
    print("=" * 60)

    from analysis.ai_review_analysis import AIReviewAnalyzer
    ai = AIReviewAnalyzer()
    ai_results = ai.run_full_analysis()

    # ============================================================
    # 3. Trust threshold model
    # ============================================================
    print("\n" + "=" * 60)
    print("== 3/6: Trust threshold model")
    print("=" * 60)

    from analysis.trust_threshold_analysis import TrustThresholdModel, estimate_time_to_collapse
    model = TrustThresholdModel()
    trust_results = model.full_analysis()
    timeline = estimate_time_to_collapse(model)

    # ============================================================
    # 4. Competitive landscape analysis
    # ============================================================
    print("\n" + "=" * 60)
    print("== 4/6: Competitive landscape analysis")
    print("=" * 60)

    from analysis.platform_competition_analysis import CompetitiveAnalyzer
    ca = CompetitiveAnalyzer()
    comp_results = ca.run_full_analysis()

    # ============================================================
    # 5. Visualization
    # ============================================================
    print("\n" + "=" * 60)
    print("== 5/6: Generate visualization figures")
    print("=" * 60)

    from visualization import (
        generate_all_figures, plot_structural_break
    )

    # Generate all standard figures
    generated = generate_all_figures(data=data)

    # Additionally generate the structural break plot (using our data)
    plot_structural_break(data, metric_col="avg_rating", save=True)

    # List all figures
    print(f"\n[INFO] Figure list ({ANALYSIS_FIGURES_DIR}):")
    for p in sorted(ANALYSIS_FIGURES_DIR.glob("*.png")):
        print(f"  - {p.name} ({p.stat().st_size // 1024}KB)")

    # ============================================================
    # 6. Report
    # ============================================================
    print("\n" + "=" * 60)
    print("== 6/6: Generate the analysis report")
    print("=" * 60)

    from report_generator import generate_report

    all_results = {
        "structural_break": break_results,
        "ai_detection": ai_results,
        "trust_model": trust_results,
        "collapse_timeline": timeline,
        "competitive": comp_results,
    }

    report_path = generate_report(all_results)
    print(f"\n[INFO] Report saved: {report_path}")

    # ============================================================
    # Done
    # ============================================================
    print("\n" + "=" * 60)
    print("[OK] All analyses complete!")
    print("=" * 60)

    # Final statistics
    n_figures = len(list(ANALYSIS_FIGURES_DIR.glob("*.png")))
    print(f"\n" + "=" * 60)
    print(f"[DONE] All analyses complete!")
    print(f"=" * 60)
    print(f"\nAcademic-grade figure count: {n_figures} (target: 12)")
    print(f"Figure directory: {ANALYSIS_FIGURES_DIR}")
    print(f"Report file: {report_path}")

    # Print the figure list
    print(f"\nFigure list:")
    for p in sorted(ANALYSIS_FIGURES_DIR.glob("*.png")):
        if "font" not in p.name.lower():
            print(f"  - {p.name} ({p.stat().st_size // 1024}KB)")

    # Report preview
    if report_path.exists():
        content = report_path.read_text(encoding="utf-8")
        lines = content.split("\n")[:30]
        print(f"\nReport section preview:")
        for line in lines:
            if line.startswith("## "):
                print(f"  {line.strip()}")

    print(f"\nFont configuration: Chinese = SimSun, English/numbers = Times New Roman")
    print(f"Version: {REPORT_META['version']}")

    return all_results


if __name__ == "__main__":
    results = main()
