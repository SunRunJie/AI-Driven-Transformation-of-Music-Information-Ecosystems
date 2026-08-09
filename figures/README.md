# Figure Inventory

Every analysis figure prints its evidence class in the upper-right corner.
The current set combines observed archive results, a hybrid text comparison,
one synthetic method check, and explicit scenario analyses.

| Figure | Evidence class | Correct interpretation |
|:--|:--|:--|
| `structural_break_analysis.png` | Illustrative synthetic data | Method benchmark around a prespecified date |
| `rating_distribution_evolution.png` | Third-party observed archives | Score agreement and calibration across 4,102 exact AOTY-RYM matches |
| `ai_vs_human_review_features.png` | Observed human text + controlled AI text | Standardized feature differences in 15+15 texts |
| `feature_correlation_heatmap.png` | Observed human text + controlled AI text | Exploratory correlations in the same hybrid corpus |
| `trust_threshold_model.png` | Assumption-driven scenario | Logistic trust mechanism under default parameters |
| `heterogeneous_trust.png` | Assumption-driven scenario | Parameterized user-group differences |
| `policy_intervention.png` | Assumption-driven scenario | Outcomes implied by assumed intervention multipliers |
| `sensitivity_analysis.png` | Assumption-driven scenario | One-at-a-time parameter sensitivity |
| `competitive_landscape.png` | Assumption-driven scenario | Analyst-coded ordinal positioning rubric |
| `four_dimensions_framework.png` | Assumption-driven scenario | Analyst-coded strategic framework |
| `genre_impact_heatmap.png` | Third-party observed archives | Shared-genre score, attention, review density, and coverage profiles |
| `ai_impact_timeline.png` | Official dates + observed archives | Policy and AOTY product dates beside the available evidence base |

The structural-break and rating-distribution functions can accept future
empirical data. Their titles, sample sizes, and source notes come from the
input provenance. Platform claims are not hard-coded.

Files under `figures/decorative/` are conceptual illustrations and should not
be presented as quantitative results.
