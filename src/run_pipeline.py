#!/usr/bin/env python
"""
One-click data analysis pipeline
================================

Running this script completes:
  1. Data collection (RYM + AOTY)
  2. Data preprocessing and integration
  3. Time-series structural break analysis
  4. AI review detection and feature analysis
  5. Trust threshold model simulation
  6. Analyst-coded platform comparison
  7. Generate all visualization figures
  8. Export a results digest (key statistics + figure inventory)

Usage:
  python src/run_pipeline.py

Design principles:
  - Modular: each stage can be re-run independently
  - Fault-tolerant: failure of one stage does not affect the rest
  - Reproducible: all random operations use a fixed seed
  - Incremental: prefer using cached data where possible
"""

import sys
import time
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

# Make the src root importable so that `from config import ...`
# and the sibling subpackage imports resolve
_SRC = str(Path(__file__).resolve().parent)
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

import numpy as np
import pandas as pd

from config import (
    RANDOM_SEED, CHATGPT_RELEASE_DATE, YEAR_RANGE,
    RAW_DIR, PROCESSED_DIR, FIGURES_DIR, ANALYSIS_FIGURES_DIR, REPORT_DIR,
    FILES, print_banner
)


class ResearchPipeline:
    """Research data analysis pipeline - end-to-end execution"""

    def __init__(self, mode: str = "empirical", collect: bool = False):
        if mode not in {"empirical", "demo"}:
            raise ValueError("mode must be 'empirical' or 'demo'")
        self.mode = mode
        self.collect = collect
        self.rng = np.random.default_rng(RANDOM_SEED)
        self.start_time = None
        self.results = {}
        self.datasets = {}

    def run(self):
        """Run the full pipeline"""
        self.start_time = time.time()

        print_banner()
        print(f"\n[INFO] Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"[INFO] Data directory: {RAW_DIR}")
        print(f"[INFO] Output directory: {ANALYSIS_FIGURES_DIR}")
        print(f"[INFO] Evidence mode: {self.mode}")
        print("=" * 60)

        # Stage 1: data collection is explicit because it has external side
        # effects and may be blocked or rate-limited.
        if self.collect:
            self.stage_data_collection()
        else:
            print("\n[INFO] Stage 1/8 skipped: pass --collect to request public pages")

        # Stage 2: data preprocessing
        self.stage_preprocessing()

        # Stage 3: time-series structural break analysis
        self.stage_structural_break()

        # Stage 4: AI review detection
        self.stage_ai_detection()

        # Stage 5: trust threshold model
        self.stage_trust_model()

        # Stage 6: competitive landscape analysis
        self.stage_competitive_analysis()

        # Stage 7: visualization
        self.stage_visualization()

        # Stage 8: results digest export
        self.stage_report()

        # Done
        elapsed = time.time() - self.start_time
        print("\n" + "=" * 60)
        print(f"[OK] All analysis complete! Total time: {elapsed:.1f}s ({elapsed/60:.1f}min)")
        print(f"[INFO] All figures saved to: {ANALYSIS_FIGURES_DIR}")
        print(f"[INFO] All data saved to: {RAW_DIR} and {PROCESSED_DIR}")
        print("=" * 60)

    # ----------------------------------------------------------
    # Stage 1: data collection
    # ----------------------------------------------------------

    def stage_data_collection(self):
        """Data collection stage"""
        print("\n" + "=" * 60)
        print("=== Stage 1/8: Data Collection")
        print("=" * 60)

        try:
            from data_collection.rym_scraper import RYMDataCollector
            from data_collection.aoty_scraper import AOTYDataCollector

            # RYM data
            print("\n[INFO] 1.1 RYM data collection")
            rym = RYMDataCollector(delay=2.0, use_cache=True)
            rym_data = rym.generate_full_dataset()
            self.datasets.update(rym_data)
            self.results["rym_collection"] = {
                name: len(df) for name, df in rym_data.items()
            }

            # AOTY data
            print("\n[INFO] 1.2 AOTY data collection")
            aoty = AOTYDataCollector(delay=2.0, use_cache=True)
            aoty_data = aoty.generate_full_dataset()
            self.datasets.update(aoty_data)
            self.results["aoty_collection"] = {
                name: len(df) for name, df in aoty_data.items()
            }

            print("\n[OK] Data collection complete")
        except Exception as e:
            print(f"[WARN] Data collection stage failed: {e}")
            print("  Continuing with the provenance audit of existing data...")

    # ----------------------------------------------------------
    # Stage 2: preprocessing
    # ----------------------------------------------------------

    def stage_preprocessing(self):
        """Data preprocessing stage"""
        print("\n" + "=" * 60)
        print("=== Stage 2/8: Data Preprocessing")
        print("=" * 60)

        try:
            from analysis.observed_archive_analysis import load_observed_archives

            archives = load_observed_archives(export=True)
            self.datasets["observed_archives"] = archives
            self.results["observed_archives"] = archives["summary"]
            source_counts = archives["summary"]["sources"]
            print(
                "  [OK] Observed archives loaded: "
                f"AOTY history {source_counts['aoty_history_rows']:,}, "
                f"AOTY snapshot {source_counts['aoty_top5000_rows']:,}, "
                f"RYM snapshot {source_counts['rym_top5000_rows']:,} rows"
            )
        except Exception as e:
            print(f"[WARN] Observed archive integration failed: {e}")
            self.results["observed_archives"] = {
                "status": "unavailable",
                "reason": str(e),
            }

        try:
            from preprocessing.data_preprocessing import DataPreprocessor

            preprocessor = DataPreprocessor(empirical_only=self.mode == "empirical")
            merged_data, quality_report = preprocessor.run_pipeline()

            self.datasets["merged"] = merged_data
            self.results["quality_report"] = quality_report

            if merged_data.empty and self.mode == "demo":
                print("\n[INFO] Demo mode: generating an explicitly synthetic benchmark...")
                merged_data = self._generate_comprehensive_dataset()
                self.datasets["merged"] = merged_data

                path = PROCESSED_DIR / "demo_synthetic_ratings.csv"
                merged_data.to_csv(path, index=False, encoding="utf-8-sig")
                print(f"  [OK] Demo dataset saved: {path}")
            elif merged_data.empty:
                self.results["evidence_status"] = {
                    "status": "descriptive_archives_available",
                    "reason": (
                        "observed cross-sectional archives are available, but no repeated "
                        "platform time series can support a structural-break estimate"
                    ),
                }

        except Exception as e:
            print(f"[WARN] Preprocessing stage failed: {e}")
            self.datasets["merged"] = pd.DataFrame()
            self.results["evidence_status"] = {
                "status": "failed",
                "reason": str(e),
            }

    def _generate_comprehensive_dataset(self) -> pd.DataFrame:
        """Generate a comprehensive synthetic dataset (to demonstrate the analysis framework)"""
        print("\n  [INFO] Generating comprehensive synthetic dataset...")

        # Time-series data (2020-2026, weekly frequency)
        dates = pd.date_range(start="2020-01-01", end="2026-07-01", freq="7D")
        n = len(dates)
        chatgpt_idx = dates.searchsorted(pd.Timestamp(CHATGPT_RELEASE_DATE))

        # Rating metric - simulating a structural break
        ratings = np.where(
            dates < pd.Timestamp(CHATGPT_RELEASE_DATE),
            3.5 + 0.3 * self.rng.standard_normal(n),
            3.2 + 0.5 * self.rng.standard_normal(n)  # increased variance
        )

        # Rating counts - increase notably after the AI shock
        counts = np.where(
            dates < pd.Timestamp(CHATGPT_RELEASE_DATE),
            self.rng.poisson(80, n),
            self.rng.poisson(120, n)
        )

        # AI penetration rate estimate
        ai_ratio = np.zeros(n)
        for i in range(chatgpt_idx, n):
            days_since = i - chatgpt_idx
            if days_since < 8:
                ai_ratio[i] = self.rng.uniform(0.005, 0.02)
            elif days_since < 26:
                ai_ratio[i] = self.rng.uniform(0.02, 0.08)
            elif days_since < 52:
                ai_ratio[i] = self.rng.uniform(0.06, 0.15)
            elif days_since < 104:
                ai_ratio[i] = self.rng.uniform(0.12, 0.25)
            else:
                ai_ratio[i] = self.rng.uniform(0.20, 0.35)

        df_ts = pd.DataFrame({
            "date": dates,
            "avg_rating": np.clip(ratings, 1, 5),
            "rating_count": counts.astype(float),
            "review_ratio": np.clip(
                0.3 + 0.05 * self.rng.standard_normal(n), 0.05, 0.5
            ),
            "estimated_ai_ratio": ai_ratio,
        })

        # User rating data
        n_ratings = 5000
        timestamps = pd.date_range("2020-01-01", "2026-07-01", periods=n_ratings)
        user_ratings = np.zeros(n_ratings)

        for i, ts in enumerate(timestamps):
            if ts < pd.Timestamp(CHATGPT_RELEASE_DATE):
                user_ratings[i] = np.clip(self.rng.normal(3.5, 0.8), 1, 5)
            else:
                if self.rng.random() < 0.2:
                    user_ratings[i] = np.clip(self.rng.normal(3.3, 0.4), 1, 5)
                else:
                    user_ratings[i] = np.clip(self.rng.normal(3.3, 0.9), 1, 5)

        df_ratings = pd.DataFrame({
            "date": timestamps,
            "rating": user_ratings.round(2),
            "has_review": self.rng.choice([True, False], n_ratings, p=[0.25, 0.75]),
            "user_age_days": np.where(
                timestamps < pd.Timestamp(CHATGPT_RELEASE_DATE),
                self.rng.exponential(800, n_ratings),
                self.rng.exponential(300, n_ratings)
            ).astype(int),
            "is_verified_user": self.rng.choice([True, False], n_ratings, p=[0.6, 0.4]),
            "source_dataset": "comprehensive_synthetic",
            "is_synthetic": True,
            "provenance_status": "illustrative_simulation",
        })

        return df_ratings

    # ----------------------------------------------------------
    # Stage 3: structural break analysis
    # ----------------------------------------------------------

    def stage_structural_break(self):
        """Time-series structural break analysis"""
        print("\n" + "=" * 60)
        print("=== Stage 3/8: Time-Series Structural Break Analysis")
        print("=" * 60)

        try:
            from analysis.structural_break_analysis import run_full_analysis

            data = self.datasets.get("merged")
            if data is not None and not data.empty and "date" in data.columns:
                results = run_full_analysis(
                    data,
                    allow_non_empirical=self.mode == "demo",
                )
                self.results["structural_break"] = results
            else:
                reason = "no empirical time series passed the provenance gate"
                print(f"[WARN] Structural break analysis not testable: {reason}")
                self.results["structural_break"] = {
                    "status": "not_testable",
                    "reason": reason,
                }

        except Exception as e:
            print(f"[WARN] Structural break analysis failed: {e}")

    # ----------------------------------------------------------
    # Stage 4: AI review detection
    # ----------------------------------------------------------

    def stage_ai_detection(self):
        """AI review detection and feature analysis"""
        print("\n" + "=" * 60)
        print("=== Stage 4/8: AI Review Detection and Feature Analysis")
        print("=" * 60)

        try:
            from analysis.ai_review_analysis import AIReviewAnalyzer, HUMAN_REVIEWS, AI_REVIEWS

            analyzer = AIReviewAnalyzer()
            results = analyzer.run_full_analysis()
            self.results["ai_detection"] = results

        except Exception as e:
            print(f"[WARN] AI detection stage failed: {e}")

    # ----------------------------------------------------------
    # Stage 5: trust threshold model
    # ----------------------------------------------------------

    def stage_trust_model(self):
        """Trust threshold model"""
        print("\n" + "=" * 60)
        print("=== Stage 5/8: Trust Threshold Model Analysis")
        print("=" * 60)

        try:
            from analysis.trust_threshold_analysis import TrustThresholdModel

            model = TrustThresholdModel()
            results = model.full_analysis()
            self.results["trust_model"] = results

            self.results["trust_model_status"] = {
                "status": "scenario_model",
                "reason": "parameters are assumptions and have not been calibrated to platform observations",
            }

        except Exception as e:
            print(f"[WARN] Trust threshold model failed: {e}")

    # ----------------------------------------------------------
    # Stage 6: competitive landscape analysis
    # ----------------------------------------------------------

    def stage_competitive_analysis(self):
        """Quantitative competitive landscape analysis"""
        print("\n" + "=" * 60)
        print("=== Stage 6/8: Analyst-Coded Platform Comparison")
        print("=" * 60)

        try:
            from analysis.platform_competition_analysis import CompetitiveAnalyzer

            analyzer = CompetitiveAnalyzer()
            results = analyzer.run_full_analysis()
            self.results["competitive"] = results

        except Exception as e:
            print(f"[WARN] Competitive landscape analysis failed: {e}")

    # ----------------------------------------------------------
    # Stage 7: visualization
    # ----------------------------------------------------------

    def stage_visualization(self):
        """Generate all visualization figures"""
        print("\n" + "=" * 60)
        print("=== Stage 7/8: Generate Visualization Figures")
        print("=" * 60)

        try:
            from visualization import generate_all_figures

            data = self.datasets.get("merged")
            generated = generate_all_figures(
                data=data,
                observed_archives=self.datasets.get("observed_archives"),
            )
            self.results["figures"] = [str(p) for p in generated]

        except Exception as e:
            print(f"[WARN] Visualization stage failed: {e}")
            import traceback
            traceback.print_exc()

    # ----------------------------------------------------------
    # Stage 8: results digest
    # ----------------------------------------------------------

    def stage_report(self):
        """Export a results digest: key statistics + figure inventory

        The narrative research report (docs/Research_Report.md) is authored
        by hand. This stage only exports the reproducible evidence produced
        by the pipeline (statistics and figures), so the numbers in the
        report can always be traced back to a script run.
        """
        print("\n" + "=" * 60)
        print("=== Stage 8/8: Export Results Digest")
        print("=" * 60)

        try:
            digest_path = REPORT_DIR / FILES["results_digest"]

            def pct(value):
                return f"{value:.1%}" if isinstance(value, (int, float)) else "N/A"

            with open(digest_path, "w", encoding="utf-8") as f:
                f.write("# Analysis Results Digest (auto-generated)\n\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write("This file is produced by the pipeline and lists the reproducible "
                        "evidence (key statistics and figures). The narrative research "
                        "report is authored separately in `docs/Research_Report.md`.\n\n")

                f.write("## Evidence status\n\n")
                f.write(f"- Pipeline mode: {self.mode}\n")
                evidence = self.results.get("evidence_status", {})
                if evidence:
                    f.write(f"- Empirical status: {evidence.get('status')}\n")
                    f.write(f"- Reason: {evidence.get('reason')}\n")
                else:
                    f.write("- Empirical status: available\n")
                f.write("- Trust and competition outputs are assumption-driven scenario analyses.\n\n")

                observed = self.results.get("observed_archives", {}) or {}
                cross = observed.get("cross_platform", {}) or {}
                attention = observed.get("attention", {}) or {}
                critic_user = observed.get("aoty_critic_user", {}) or {}
                if cross:
                    f.write("## 1. Observed archive evidence\n\n")
                    f.write("- Sources: third-party AOTY and RYM archive snapshots with documented dates.\n")
                    f.write(f"- Exact artist-title-year matches: {cross.get('exact_matches', 'N/A'):,}\n")
                    f.write(f"- AOTY-RYM user-score Pearson correlation: {cross.get('pearson_r', float('nan')):.3f}\n")
                    f.write(f"- Share of matched albums within 0.5 points on a 0-5 scale: {pct(cross.get('share_within_half_point'))}\n")
                    f.write(f"- AOTY critic-user pairs: {critic_user.get('n', 'N/A'):,}; Pearson r = {critic_user.get('pearson_r', float('nan')):.3f}\n")
                    f.write(f"- RYM ratings represented in its top-5,000 snapshot: {attention.get('rym_top5000_total_ratings', 'N/A'):,}\n")
                    f.write("- These are selected cross-sections, so totals are not platform-size estimates and do not identify post-2022 change.\n\n")

                # Structural break analysis
                sb = self.results.get("structural_break", {}) or {}
                summary = sb.get("summary", {}) or {}
                if summary:
                    f.write("## 2. Structural break analysis\n\n")
                    f.write(f"- Metrics analyzed: {summary.get('total_metrics_analyzed', 'N/A')}\n")
                    f.write(f"- Significant breaks: {summary.get('significant_breaks', 'N/A')} "
                            f"({summary.get('break_detection_rate', 'N/A')}%)\n\n")
                elif sb.get("status") == "not_testable":
                    f.write("## 2. Structural break analysis\n\n")
                    f.write(f"- Status: not testable\n- Reason: {sb.get('reason')}\n\n")

                # AI review detection
                ai = self.results.get("ai_detection", {}) or {}
                model = ai.get("model", {}) or {}
                if model:
                    f.write("## 3. AI review detection\n\n")
                    f.write("- Data basis: 15 observed critic excerpts and 15 controlled AI-style texts; no external validation\n")
                    f.write(f"- Cross-validated accuracy: {pct(model.get('accuracy'))}\n")
                    auc = model.get("auc")
                    auc_text = f"{auc:.3f}" if isinstance(auc, (int, float)) else "N/A"
                    f.write(f"- Cross-validated AUC: {auc_text}\n\n")

                # Trust threshold model
                tm = self.results.get("trust_model", {}) or {}
                cp = tm.get("collapse_point", {}) or {}
                if cp:
                    f.write("## 4. Trust threshold model\n\n")
                    f.write("- Data basis: uncalibrated scenario assumptions\n")
                    f.write(f"- Assumption-implied threshold crossing: "
                            f"{pct(cp.get('collapse_penetration'))}\n\n")

                # Figure inventory
                f.write("## 5. Generated figures\n\n")
                figures = sorted(ANALYSIS_FIGURES_DIR.glob("*.png"))
                if figures:
                    for p in figures:
                        f.write(f"- {p.name} ({p.stat().st_size // 1024}KB)\n")
                else:
                    f.write("(none)\n")

            self.results["report_path"] = str(digest_path)
            print(f"  [OK] Results digest saved: {digest_path}")

        except Exception as e:
            print(f"[WARN] Results digest generation failed: {e}")
            self._generate_minimal_report()

    def _generate_minimal_report(self):
        """Fallback: minimal results digest when the full export fails"""
        print("\n  Generating a minimal results digest...")
        digest_path = FIGURES_DIR.parent / FILES["results_digest"]

        with open(digest_path, "w", encoding="utf-8") as f:
            f.write("# Analysis Results Digest (auto-generated, minimal)\n\n")
            f.write(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("## Analysis Modules\n\n")
            for module in ["Data Collection", "Data Preprocessing", "Time-Series Structural Break Analysis",
                          "AI Review Detection", "Trust Threshold Model", "Competitive Landscape Analysis",
                          "Visualization"]:
                f.write(f"- {module}\n")

            f.write("\n## Generated Files\n\n")
            f.write(f"### Figures ({ANALYSIS_FIGURES_DIR})\n")
            for p in ANALYSIS_FIGURES_DIR.glob("*.png"):
                f.write(f"- {p.name}\n")

        print(f"  [OK] Results digest saved: {digest_path}")


# ============================================================
# Entry point
# ============================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the music ecosystem research pipeline")
    parser.add_argument(
        "--demo",
        action="store_true",
        help="run an explicitly synthetic demonstration instead of empirical mode",
    )
    parser.add_argument(
        "--collect",
        action="store_true",
        help="attempt live public-page collection before preprocessing",
    )
    args = parser.parse_args()
    pipeline = ResearchPipeline(
        mode="demo" if args.demo else "empirical",
        collect=args.collect,
    )
    pipeline.run()
