"""
The "Trust Threshold Hypothesis" scenario model
=================================================

This module formalizes a theoretical mechanism. Its default parameters are
not calibrated to RYM, AOTY, or user-level observations, so numerical
thresholds are scenario outputs rather than estimates or forecasts.

Core idea:
  The credibility of a UGC information platform does not decline linearly;
  there is a critical point - when the perceived proportion of "trustworthy
  ratings" falls below a certain threshold, the reference value of the entire
  rating system collapses in a phase transition.

Model assumptions:
  1. User trust in platform ratings depends on the "perceived proportion of
     real ratings"
  2. Users cannot perfectly distinguish AI and human ratings, but can infer
     through some signals
  3. When trust falls below a certain threshold, users stop using ratings as
     a basis for decisions
  4. There is a network effect: fewer trusting users -> higher proportion of
     remaining AI ratings -> accelerated collapse

Theoretical support:
  - Signaling theory (Spence, 1973): ratings as signals, AI ratings are
    "false signals"
  - Market for lemons (Akerlof, 1970): when quality cannot be distinguished,
    good goods exit the market
  - Institutional trust (North, 1990): the institutional function of the
    platform as trust infrastructure
  - Critical mass theory (Granovetter, 1978): nonlinear phase transitions in
    collective behavior

Testable implications:
  Implication 1: AI penetration and user trust follow an S-shaped curve
  relationship
  Implication 2: User churn is not gradual but accelerates after reaching a
  critical point
  Implication 3: Different user groups (experienced vs new users) have
  different trust thresholds
"""

import warnings
from typing import Dict, List, Optional, Tuple

import sys
from pathlib import Path

_SRC = str(Path(__file__).resolve().parent.parent)
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

import numpy as np
import pandas as pd

from config import TRUST_MODEL_PARAMS, RANDOM_SEED

warnings.filterwarnings("ignore")


# ============================================================
# Trust threshold model
# ============================================================

class TrustThresholdModel:
    """
    Trust threshold model - quantitative analysis of AI penetration vs
    platform credibility

    Core equation:
      Trust T(p) = 1 / (1 + exp(beta * (p - alpha)))
        where p = AI content penetration
              alpha = inflection point parameter
              beta = transition steepness

      Network effect correction:
      T_net(p) = T(p) * (1 - gamma * (1 - T(p)))
        where gamma = network effect strength

      When T(p) < tau (trust threshold) -> collapse is triggered
    """

    def __init__(self, params: Optional[Dict] = None):
        """
        Parameters:
        -----------
        params : dict, optional
          Model parameter overrides:
          - alpha: user preference strength for real ratings (default 0.7)
          - beta: signal-to-noise ratio - user discrimination ability
            (default 2.0)
          - gamma: network effect strength (default 0.3)
          - trust_threshold: trust threshold (default 0.4)
        """
        self.params = TRUST_MODEL_PARAMS.copy()
        if params:
            self.params.update(params)
        self.rng = np.random.default_rng(RANDOM_SEED)

    # ----------------------------------------------------------
    # Core functions
    # ----------------------------------------------------------

    def user_trust_function(self, ai_penetration_rate: float) -> float:
        """
        User trust function

        Input: AI content penetration (0-1)
        Output: user trust in the platform (0-1)

        Characteristics:
        - At low penetration: trust is close to 1 (users trust by default)
        - At high penetration: trust is close to 0 (users completely lose
          trust)
        - Near the threshold: rapid decline (phase transition behavior)
        """
        a = self.params["alpha"]
        b = self.params["beta"]
        c = self.params["gamma"]

        # Sigmoid logistic function
        trust = 1.0 / (1.0 + np.exp(b * (ai_penetration_rate - a)))

        # Network effect: the lower the trust, the more users tend to leave
        trust_net = trust * (1 - c * (1 - trust))

        return float(np.clip(trust_net, 0, 1))

    def trust_derivative(self, ai_penetration_rate: float) -> float:
        """
        Derivative of trust with respect to AI penetration
        Measures the sensitivity of trust to changes in AI penetration

        At the peak -> the point where trust collapses fastest
        """
        a = self.params["alpha"]
        b = self.params["beta"]
        c = self.params["gamma"]

        p = ai_penetration_rate
        exp_term = np.exp(b * (p - a))
        base_deriv = -b * exp_term / (1 + exp_term) ** 2

        # Network effect correction
        trust = 1.0 / (1.0 + exp_term)
        net_deriv = base_deriv * (1 - c * (1 - 2 * trust))

        return float(net_deriv)

    # ----------------------------------------------------------
    # Critical point computation
    # ----------------------------------------------------------

    def find_critical_point(self) -> Dict:
        """
        Find the "collapse critical point" - the position where the trust
        derivative is smallest (fastest decline)

        Returns:
        --------
        dict - penetration, trust, and decline rate at the critical point
        """
        penetration_values = np.linspace(0, 1, 10000)
        derivatives = np.array([self.trust_derivative(p)
                               for p in penetration_values])
        min_idx = np.argmin(derivatives)

        critical_penetration = penetration_values[min_idx]
        critical_trust = self.user_trust_function(critical_penetration)

        return {
            "critical_penetration": float(critical_penetration),
            "critical_trust": float(critical_trust),
            "max_derivative": float(derivatives[min_idx]),
            "interpretation": (
                f"Under the supplied assumptions, the modeled curve is steepest at "
                f"penetration {critical_penetration:.0%} ({derivatives[min_idx]:.2f}), "
                f"with modeled trust {critical_trust:.2f}"
            ),
        }

    def find_collapse_point(self, n_steps: int = 10000) -> Dict:
        """
        Find the trust collapse point (penetration at which trust falls below
        the threshold)

        Returns:
        --------
        dict - collapse point information
        """
        penetration_values = np.linspace(0, 1, n_steps)
        trust_values = np.array([self.user_trust_function(p)
                                for p in penetration_values])

        threshold = self.params["trust_threshold"]
        below_threshold = trust_values < threshold

        if not below_threshold.any():
            return {
                "collapse_exists": False,
                "message": f"With the current parameters, trust does not fall below the threshold {threshold}",
            }

        collapse_idx = np.where(below_threshold)[0][0]
        collapse_penetration = penetration_values[collapse_idx]
        collapse_trust = trust_values[collapse_idx]

        return {
            "collapse_exists": True,
            "collapse_penetration": float(collapse_penetration),
            "collapse_trust": float(collapse_trust),
            "threshold": threshold,
            "interpretation": (
                f"Under the supplied assumptions, modeled trust first crosses "
                f"the arbitrary reference threshold {threshold} at penetration "
                f"{collapse_penetration:.1%}"
            ),
        }

    # ----------------------------------------------------------
    # Dynamic simulation
    # ----------------------------------------------------------

    def simulate_dynamics(self,
                          ai_growth_rate: float = 0.03,
                          initial_penetration: float = 0.01,
                          time_steps: int = 100,
                          user_sensitivity: float = 1.0) -> pd.DataFrame:
        """
        Simulate the dynamic evolution of trust

        Parameters:
        -----------
        ai_growth_rate : float - AI penetration growth rate per step
        initial_penetration : float - initial AI penetration
        time_steps : int - number of simulation steps
        user_sensitivity : float - user sensitivity to declines in trust

        Returns:
        --------
        pd.DataFrame - indicator values at each step
        """
        penetration = initial_penetration
        trust = 1.0
        user_activity = 1.0

        history = []

        for t in range(time_steps):
            # Trust depends on the current penetration
            trust = self.user_trust_function(penetration)

            # User activity is affected by trust
            user_activity = max(0.01, trust ** user_sensitivity)

            # AI penetration grows (growth rate is affected by user activity)
            growth = ai_growth_rate * user_activity
            penetration = min(1.0, penetration * (1 + growth))

            # If trust is below the threshold and still declining, accelerate
            # the collapse
            if trust < self.params["trust_threshold"]:
                user_activity *= 0.85  # Users churn faster

            history.append({
                "time": t,
                "ai_penetration": penetration,
                "trust": trust,
                "user_activity": user_activity,
                "is_crashed": trust < self.params["trust_threshold"],
            })

        return pd.DataFrame(history)

    def simulate_multiple_scenarios(self) -> Dict[str, pd.DataFrame]:
        """
        Simulate trust evolution across multiple scenarios

        Scenarios:
        1. Baseline scenario: default parameters
        2. High discrimination scenario: users have strong discrimination
           ability (high beta)
        3. Low discrimination scenario: users have weak discrimination
           ability (low beta)
        4. Strong network effect scenario: users influence each other
           strongly (high gamma)
        5. High growth scenario: fast AI content growth
        """
        scenarios = {
            "Baseline scenario": {"ai_growth_rate": 0.03},
            "High discrimination (beta=4)": {"ai_growth_rate": 0.03},
            "Low discrimination (beta=1)": {"ai_growth_rate": 0.03},
            "Strong network effect (gamma=0.6)": {"ai_growth_rate": 0.03},
            "Fast AI content growth": {"ai_growth_rate": 0.06},
        }

        results = {}
        for name, kwargs in scenarios.items():
            # Adjust parameters
            model_copy = TrustThresholdModel(self.params.copy())
            if "beta=4" in name:
                model_copy.params["beta"] = 4.0
            elif "beta=1" in name:
                model_copy.params["beta"] = 1.0
            if "gamma=0.6" in name:
                model_copy.params["gamma"] = 0.6

            df = model_copy.simulate_dynamics(**kwargs)
            df["scenario"] = name
            results[name] = df

        return results

    # ----------------------------------------------------------
    # User heterogeneity analysis
    # ----------------------------------------------------------

    def heterogeneous_users(self) -> pd.DataFrame:
        """
        Simulate heterogeneous trust thresholds across different user groups

        Different user groups:
        - Experienced users: strong discrimination ability (high beta),
          high threshold
        - Regular users: moderate discrimination ability
        - New users: weak discrimination ability (low beta), low threshold
        - Casual users: do not care much about authenticity
        """
        user_types = [
            {"name": "Experienced music fans", "alpha": 0.6, "beta": 4.0, "threshold": 0.5},
            {"name": "Regular users", "alpha": 0.7, "beta": 2.0, "threshold": 0.4},
            {"name": "Newly registered users", "alpha": 0.8, "beta": 1.0, "threshold": 0.3},
            {"name": "Casual browsers", "alpha": 0.9, "beta": 0.5, "threshold": 0.2},
        ]

        penetration_range = np.linspace(0, 1, 100)

        rows = []
        for user in user_types:
            model = TrustThresholdModel({
                "alpha": user["alpha"],
                "beta": user["beta"],
                "trust_threshold": user["threshold"],
            })
            for p in penetration_range:
                trust = model.user_trust_function(p)
                rows.append({
                    "user_type": user["name"],
                    "ai_penetration": p,
                    "trust": trust,
                    "threshold": user["threshold"],
                    "is_crashed": trust < user["threshold"],
                })

        return pd.DataFrame(rows)

    # ----------------------------------------------------------
    # Policy intervention simulation
    # ----------------------------------------------------------

    def simulate_policy_intervention(self) -> pd.DataFrame:
        """
        Simulate the effect of different policy interventions

        Interventions:
        1. No intervention: AI grows naturally
        2. Content detection: reduce AI penetration by 20%
        3. User education: improve user discrimination ability (beta+0.5)
        4. Dual intervention: detection + education
        """
        policies = {
            "No intervention": {"penetration_multiplier": 1.0, "beta_boost": 0},
            "AI content detection": {"penetration_multiplier": 0.7, "beta_boost": 0},
            "User education program": {"penetration_multiplier": 1.0, "beta_boost": 0.5},
            "Dual intervention (detection + education)": {"penetration_multiplier": 0.7, "beta_boost": 0.5},
        }

        penetration_range = np.linspace(0, 1, 100)

        rows = []
        for policy_name, policy_params in policies.items():
            model_params = self.params.copy()
            model_params["beta"] += policy_params["beta_boost"]

            model = TrustThresholdModel(model_params)
            for p in penetration_range:
                effective_p = p * policy_params["penetration_multiplier"]
                trust = model.user_trust_function(effective_p)
                rows.append({
                    "policy": policy_name,
                    "effective_penetration": effective_p,
                    "trust": trust,
                    "threshold": model.params["trust_threshold"],
                })

        return pd.DataFrame(rows)

    # ----------------------------------------------------------
    # Full analysis
    # ----------------------------------------------------------

    def full_analysis(self) -> Dict:
        """Run the full trust threshold analysis"""
        print("\n" + "=" * 60)
        print("Trust threshold model analysis - start")
        print("=" * 60)
        print(f"\nModel parameters:")
        for k, v in self.params.items():
            print(f"  {k} = {v}")

        results = {
            "evidence_status": {
                "class": "assumption-driven scenario model",
                "calibrated": False,
                "forecast": False,
            }
        }

        # 1. Critical point analysis
        print("\n[Phase 1] Critical point analysis...")
        results["critical_point"] = self.find_critical_point()
        results["collapse_point"] = self.find_collapse_point()
        print(f"  Critical point: {results['critical_point']['interpretation']}")
        if results["collapse_point"].get("collapse_exists"):
            print(f"  Reference crossing: {results['collapse_point']['interpretation']}")

        # 2. Dynamic simulation
        print("\n[Phase 2] Dynamic simulation...")
        results["dynamics"] = self.simulate_dynamics()
        final_state = results["dynamics"].iloc[-1]
        print(f"  Final state: AI penetration={final_state['ai_penetration']:.2%}, "
              f"trust={final_state['trust']:.3f}, "
              f"{'below' if final_state['is_crashed'] else 'above'} reference")

        # 3. Multi-scenario comparison
        print("\n[Phase 3] Multi-scenario comparison...")
        results["scenarios"] = self.simulate_multiple_scenarios()
        for name, df in results["scenarios"].items():
            final = df.iloc[-1]
            status = "above reference" if not final["is_crashed"] else "below reference"
            print(f"  {name}: final trust={final['trust']:.3f} [{status}]")

        # 4. User heterogeneity
        print("\n[Phase 4] User heterogeneity analysis...")
        results["heterogeneous"] = self.heterogeneous_users()
        user_summary = results["heterogeneous"].groupby("user_type").agg({
            "trust": "mean",
            "is_crashed": "sum",
        })
        print(user_summary.to_string())

        # 5. Policy intervention
        print("\n[Phase 5] Policy intervention simulation...")
        results["policy"] = self.simulate_policy_intervention()
        policy_summary = results["policy"].groupby("policy").agg({
            "trust": "mean",
        })
        print(policy_summary.to_string())

        # 6. Trust curve numeric table
        print("\n[Phase 6] Trust curve key points...")
        print(f"\nTrust curve values:")
        for p in [0.01, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30,
                  0.35, 0.40, 0.45, 0.50, 0.60, 0.80]:
            t = self.user_trust_function(p)
            deriv = self.trust_derivative(p)
            status = "above reference" if t > self.params["trust_threshold"] else "below reference"
            print(f"  AI penetration={p:.0%} -> trust={t:.4f} "
                  f"(decline rate={deriv:.2f}) [{status}]")

        print("\n" + "=" * 60)
        print("Trust threshold model analysis complete")
        print("=" * 60)

        return results


# ============================================================
# Convenience functions
# ============================================================

def estimate_ai_penetration(growth_rate: float = 0.03,
                             months: int = 36) -> pd.DataFrame:
    """
    Estimate the future growth path of AI penetration

    Used to answer: at the current growth rate, when will the trust
    threshold be reached?
    """
    initial = 0.01  # Current estimated AI penetration is about 1%
    penetrations = [initial]

    for m in range(1, months + 1):
        penetrations.append(penetrations[-1] * (1 + growth_rate))

    df = pd.DataFrame({
        "month": range(months + 1),
        "date": pd.date_range("2026-07-01", periods=months + 1, freq="MS"),
        "penetration": penetrations,
    })

    return df


def estimate_time_to_collapse(model: TrustThresholdModel,
                               current_penetration: float = 0.01,
                               monthly_growth: float = 0.03) -> Dict:
    """
    Compute a conditional scenario timeline from explicit growth assumptions.

    This is not a forecast because neither current penetration nor monthly
    growth is estimated from platform observations.
    """
    collapse_point = model.find_collapse_point()
    if not collapse_point.get("collapse_exists"):
        return {"message": "Will not collapse under the current parameters"}

    target = collapse_point["collapse_penetration"]

    # Compute the number of months needed to reach the target
    months = 0
    p = current_penetration
    while p < target and months < 120:
        p *= (1 + monthly_growth)
        months += 1

    return {
        "evidence_class": "conditional uncalibrated scenario",
        "is_forecast": False,
        "current_penetration": current_penetration,
        "monthly_growth_rate": monthly_growth,
        "collapse_penetration": target,
        "estimated_months_to_collapse": months,
        "estimated_date": (
            pd.Timestamp("2026-07-01") + pd.DateOffset(months=months)
        ).strftime("%Y-%m"),
        "collapse_will_happen": months < 120,
        "urgency": (
            "Very high" if months < 12 else
            "High" if months < 24 else
            "Medium" if months < 48 else
            "Low"
        ),
    }


# ============================================================
# Standalone run
# ============================================================

if __name__ == "__main__":
    model = TrustThresholdModel()
    results = model.full_analysis()

    # Time estimation
    print("\n" + "=" * 50)
    print("Time to collapse estimate")
    print("=" * 50)
    timeline = estimate_time_to_collapse(model)
    for k, v in timeline.items():
        print(f"  {k}: {v}")
