"""
Assumption-driven competitive landscape analysis
=================================================

Research questions:
  1. What is the strategic positioning of RYM/AOTY among music information service platforms?
  2. How much do the effects of the AI disruption differ across platform types?
  3. Who is the most vulnerable? Who has a moat?

Analytical methods:
  - Competitive positioning matrix (data depth x social experience)
  - AI disruption risk scoring
  - Platform capability radar chart
  - Strategic grouping analysis
"""

import warnings
from typing import Dict, List, Optional

import sys
from pathlib import Path

_SRC = str(Path(__file__).resolve().parent.parent)
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

import numpy as np
import pandas as pd

from config import RANDOM_SEED

warnings.filterwarnings("ignore")


# ============================================================
# Platform data
# ============================================================

# Analyst-coded ordinal inputs for scenario exploration. These values are not
# observations, audited platform metrics, or externally validated rankings.
PLATFORM_DATA = {
    "RYM": {
        "data_depth": 9.5,          # database size, metadata granularity
        "social_engagement": 7.0,    # community interaction, UGC activity
        "monthly_users_m": 5,       # monthly active users (millions)
        "founded_year": 2002,
        "business_model": "Advertising + subscription + data licensing",
        "ai_risk_score": 9.0,       # AI disruption risk (1-10)
        "content_moderation": 4.0,  # content moderation capability
        "brand_trust": 8.0,         # brand trust
        "technical_moat": 6.0,      # technical moat
        "data_moat": 9.5,           # data moat
        "community_moat": 8.5,      # community moat
        "description": "The IMDb of the music world - a database-driven encyclopedia of ratings",
    },
    "AOTY": {
        "data_depth": 7.0,
        "social_engagement": 8.5,
        "monthly_users_m": 3,
        "founded_year": 2009,
        "business_model": "Advertising + Premium subscription",
        "ai_risk_score": 8.5,
        "content_moderation": 5.0,
        "brand_trust": 7.0,
        "technical_moat": 5.5,
        "data_moat": 7.0,
        "community_moat": 8.0,
        "description": "The socialization of ratings - a design-driven rating community",
    },
    "Pitchfork": {
        "data_depth": 5.0,
        "social_engagement": 3.0,
        "monthly_users_m": 2,
        "founded_year": 1996,
        "business_model": "Professional media + advertising",
        "ai_risk_score": 6.5,
        "content_moderation": 8.0,
        "brand_trust": 9.0,
        "technical_moat": 3.0,
        "data_moat": 4.0,
        "community_moat": 7.0,
        "description": "Professional music criticism media - the authority of editorial curation",
    },
    "Discogs": {
        "data_depth": 9.0,
        "social_engagement": 5.0,
        "monthly_users_m": 15,
        "founded_year": 2000,
        "business_model": "Marketplace + database",
        "ai_risk_score": 5.0,
        "content_moderation": 6.0,
        "brand_trust": 8.5,
        "technical_moat": 5.0,
        "data_moat": 9.0,
        "community_moat": 7.0,
        "description": "A database and marketplace for music collectors",
    },
    "Spotify": {
        "data_depth": 3.0,
        "social_engagement": 4.0,
        "monthly_users_m": 500,
        "founded_year": 2006,
        "business_model": "Streaming subscription",
        "ai_risk_score": 4.0,
        "content_moderation": 7.0,
        "brand_trust": 7.0,
        "technical_moat": 8.0,
        "data_moat": 6.0,
        "community_moat": 3.0,
        "description": "The world's largest streaming platform - driven by algorithmic recommendations",
    },
    "Bandcamp": {
        "data_depth": 5.5,
        "social_engagement": 7.5,
        "monthly_users_m": 50,
        "founded_year": 2008,
        "business_model": "Direct sales + community",
        "ai_risk_score": 6.0,
        "content_moderation": 5.0,
        "brand_trust": 8.0,
        "technical_moat": 4.0,
        "data_moat": 5.0,
        "community_moat": 8.0,
        "description": "An independent music direct-sales platform - creator-friendly",
    },
    "Douban Music": {
        "data_depth": 6.5,
        "social_engagement": 8.0,
        "monthly_users_m": 8,
        "founded_year": 2005,
        "business_model": "Community + ratings",
        "ai_risk_score": 8.0,
        "content_moderation": 3.0,
        "brand_trust": 7.0,
        "technical_moat": 3.0,
        "data_moat": 6.0,
        "community_moat": 8.0,
        "description": "A Chinese music community - ratings and social features combined",
    },
    "Last.fm": {
        "data_depth": 8.0,
        "social_engagement": 6.0,
        "monthly_users_m": 20,
        "founded_year": 2002,
        "business_model": "Social + data",
        "ai_risk_score": 7.0,
        "content_moderation": 4.0,
        "brand_trust": 7.0,
        "technical_moat": 5.0,
        "data_moat": 7.5,
        "community_moat": 6.0,
        "description": "Music listening tracking + social network",
    },
}


# ============================================================
# Competitive landscape analyzer
# ============================================================

class CompetitiveAnalyzer:
    """Quantitative competitive landscape analyzer"""

    def __init__(self):
        self.df = pd.DataFrame.from_dict(PLATFORM_DATA, orient="index")
        self.df.index.name = "platform"
        self.df = self.df.reset_index()

    def get_platform_summary(self) -> pd.DataFrame:
        """Get a summary of the analyst-coded scenario inputs."""
        return self.df[[
            "platform", "data_depth", "social_engagement",
            "ai_risk_score", "business_model",
            "founded_year"
        ]].sort_values("ai_risk_score", ascending=False)

    # ----------------------------------------------------------
    # Strategic positioning analysis
    # ----------------------------------------------------------

    def strategic_grouping(self) -> Dict:
        """
        Strategic group analysis

        Groups platforms into four strategic groups based on data depth
        and social experience
        """
        df = self.df.copy()

        # Quartile grouping
        median_data = df["data_depth"].median()
        median_social = df["social_engagement"].median()

        groups = {
            "High data, high social (top right)": df[
                (df["data_depth"] >= median_data) &
                (df["social_engagement"] >= median_social)
            ]["platform"].tolist(),
            "High data, low social (bottom right)": df[
                (df["data_depth"] >= median_data) &
                (df["social_engagement"] < median_social)
            ]["platform"].tolist(),
            "Low data, high social (top left)": df[
                (df["data_depth"] < median_data) &
                (df["social_engagement"] >= median_social)
            ]["platform"].tolist(),
            "Low data, low social (bottom left)": df[
                (df["data_depth"] < median_data) &
                (df["social_engagement"] < median_social)
            ]["platform"].tolist(),
        }

        print("\n[INFO] Strategic group analysis:")
        for group, members in groups.items():
            print(f"  {group}: {', '.join(members)}")

        return groups

    # ----------------------------------------------------------
    # AI disruption risk assessment
    # ----------------------------------------------------------

    def ai_vulnerability_analysis(self) -> pd.DataFrame:
        """
        AI vulnerability analysis

        Assesses how vulnerable each platform is to the AI disruption
        Based on: AI risk score x (1 - defensive capability)
        """
        df = self.df.copy()

        # Combined defensive capability (normalized to 0-1)
        df["defense_score"] = (
            df["content_moderation"] * 0.3 +
            df["brand_trust"] * 0.3 +
            df["community_moat"] * 0.2 +
            df["technical_moat"] * 0.1 +
            df["data_moat"] * 0.1
        ) / 10

        # Vulnerability score
        df["vulnerability_score"] = df["ai_risk_score"] * (1 - df["defense_score"])
        df["vulnerability_level"] = pd.cut(
            df["vulnerability_score"],
            bins=[0, 2, 4, 6, 10],
            labels=["Low", "Medium-Low", "Medium-High", "High"],
        )

        result = df[[
            "platform", "ai_risk_score", "defense_score",
            "vulnerability_score", "vulnerability_level",
            "description"
        ]].sort_values("vulnerability_score", ascending=False)

        print("\n[SCENARIO] Scores under the selected vulnerability rubric:")
        for _, row in result.iterrows():
            print(f"  {row['platform']:10s} risk={row['ai_risk_score']:.1f} "
                  f"defense={row['defense_score']:.2f} "
                  f"vulnerability={row['vulnerability_score']:.2f} "
                  f"[{row['vulnerability_level']}]")

        return result

    # ----------------------------------------------------------
    # Moat analysis
    # ----------------------------------------------------------

    def moat_analysis(self) -> pd.DataFrame:
        """
        Moat analysis

        Assesses the competitive barrier structure of each platform
        """
        df = self.df.copy()

        moat_types = ["data_moat", "community_moat", "technical_moat", "brand_trust"]

        # Compute the overall moat score and structure
        df["total_moat"] = df[moat_types].sum(axis=1)

        # Moat structure (share of each dimension)
        for mt in moat_types:
            df[f"{mt}_share"] = df[mt] / df["total_moat"]

        result = df[["platform", "data_moat", "community_moat",
                     "technical_moat", "brand_trust", "total_moat"]].sort_values(
            "total_moat", ascending=False
        )

        print("\n[SCENARIO] Analyst-coded platform capability scores:")
        for _, row in result.iterrows():
            print(f"  {row['platform']:10s} total={row['total_moat']:.1f} "
                  f"(data={row['data_moat']:.1f} "
                  f"community={row['community_moat']:.1f} "
                  f"tech={row['technical_moat']:.1f} "
                  f"brand={row['brand_trust']:.1f})")

        return result

    # ----------------------------------------------------------
    # Competitive dynamics simulation
    # ----------------------------------------------------------

    def simulate_ai_impact_on_market(self) -> pd.DataFrame:
        """
        Simulates the effect of the AI disruption on the competitive landscape

        Assumptions:
        - The AI disruption weakens the data moat of UGC platforms (AI can generate
          large amounts of "pseudo data")
        - It strengthens the technical moat (AI detection capability is needed)
        - The community moat stays relatively stable (connections between real
          people are hard for AI to replicate)
        """
        df = self.df.copy()

        # Impact coefficients of the AI disruption on each moat
        impact = {
            "data_moat": 0.6,      # data moat is substantially weakened
            "community_moat": 0.9,  # community moat stays relatively stable
            "technical_moat": 1.3,  # technical moat becomes more important
            "brand_trust": 1.1,     # brand trust becomes more important
        }

        for moat, coefficient in impact.items():
            df[f"{moat}_post_ai"] = df[moat] * coefficient

        # Compute overall competitiveness before and after the impact
        moat_cols = ["data_moat", "community_moat", "technical_moat", "brand_trust"]
        post_cols = [f"{c}_post_ai" for c in moat_cols]

        df["pre_ai_total"] = df[moat_cols].sum(axis=1)
        df["post_ai_total"] = df[post_cols].sum(axis=1)
        df["competitive_change"] = df["post_ai_total"] - df["pre_ai_total"]
        df["competitive_change_pct"] = (
            df["competitive_change"] / df["pre_ai_total"] * 100
        )

        result = df[[
            "platform", "pre_ai_total", "post_ai_total",
            "competitive_change", "competitive_change_pct"
        ]].sort_values("competitive_change", ascending=False)

        print("\n[SCENARIO] Changes under the selected AI-impact multipliers:")
        for _, row in result.iterrows():
            print(f"  {row['platform']:10s} "
                  f"{row['pre_ai_total']:.1f} -> {row['post_ai_total']:.1f} "
                  f"({row['competitive_change_pct']:+.1f}%)")

        return result

    # ----------------------------------------------------------
    # Full analysis
    # ----------------------------------------------------------

    def run_full_analysis(self) -> Dict:
        """Run the complete competitive landscape analysis"""
        print("\n" + "=" * 60)
        print("[INFO] Analyst-coded platform comparison - start")
        print("=" * 60)

        results = {
            "evidence_status": {
                "class": "analyst-coded assumption-driven scenario",
                "observed_platform_metrics": False,
                "validated_ranking": False,
            }
        }

        # 1. Platform overview
        print("\n[Stage 1] Platform data summary...")
        results["summary"] = self.get_platform_summary()
        print(results["summary"].to_string(index=False))

        # 2. Strategic grouping
        print("\n[Stage 2] Strategic group analysis...")
        results["strategic_groups"] = self.strategic_grouping()

        # 3. AI vulnerability
        print("\n[Stage 3] AI vulnerability assessment...")
        results["vulnerability"] = self.ai_vulnerability_analysis()

        # 4. Moat analysis
        print("\n[Stage 4] Moat analysis...")
        results["moat"] = self.moat_analysis()

        # 5. Competitive dynamics simulation
        print("\n[Stage 5] Competitive dynamics under AI impact...")
        results["dynamics"] = self.simulate_ai_impact_on_market()

        # 6. Key conclusions
        print("\n[Stage 6] Key conclusions...")
        conclusions = self._generate_conclusions(results)
        results["conclusions"] = conclusions

        print("\n" + "=" * 60)
        print("[OK] Competitive landscape analysis complete")
        print("=" * 60)

        return results

    def _generate_conclusions(self, results: Dict) -> List[str]:
        """Generate analysis conclusions"""
        conclusions = [
            "1. Under the chosen rubric, data depth and social engagement define useful comparison dimensions.",
            "2. The assumed weights make community and moderation capacity offset some modeled AI vulnerability.",
            "3. Rankings are outputs of analyst-assigned scores and should be treated as hypotheses for validation.",
            "4. Claims about users, platform readiness, or actual risk require sourced platform metrics and documented coding procedures.",
        ]
        for c in conclusions:
            print(f"  {c}")
        return conclusions


# ============================================================
# Standalone run
# ============================================================

if __name__ == "__main__":
    analyzer = CompetitiveAnalyzer()
    results = analyzer.run_full_analysis()
