# Figures

All figures referenced in the research report, organized into two groups:

- **Analysis figures (Figure 1-12)** — data visualizations produced by the
  analysis scripts (`src/visualization.py`), in `figures/analysis/`.
- **Illustrative figures (Figure A-L)** — conceptual diagrams used to explain
  the analytical framework, in `figures/decorative/` (provided as both
  Mermaid source and PNG).

## Directory layout

```
figures/
├── README.md        ← this file
├── analysis/        ← analysis figures (Figure 1-12)
└── decorative/      ← illustrative figures (Figure A-L, Mermaid + PNG)
```

## Analysis figures (Figure 1-12)

Located in `figures/analysis/`.

| # | File | Description | Method |
|:--|:-----|:------------|:-------|
| 1 | `ai_impact_timeline.png` | Serpentine timeline with AI penetration S-curve | Event history analysis |
| 2 | `structural_break_analysis.png` | Three-panel break analysis (series, rolling stats, CUSUM) | Bai-Perron + CUSUM + Chow |
| 3 | `ai_vs_human_review_features.png` | AI vs human review features (radar + diverging bars, 11 features) | TF-IDF + Random Forest |
| 4 | `rating_distribution_evolution.png` | Rating distribution before/after ChatGPT (KDE, K-S test) | KDE + K-S test |
| 5 | `trust_threshold_model.png` | S-shaped trust curve + multi-scenario Monte Carlo | Logistic phase transition + network effects |
| 6 | `heterogeneous_trust.png` | Heterogeneous trust curves for four user groups | Heterogeneity simulation |
| 7 | `four_dimensions_framework.png` | Four-dimensional impact assessment + priority matrix | Institutional logic framework |
| 8 | `policy_intervention.png` | Policy intervention comparison (4 strategies) | Scenario simulation |
| 9 | `genre_impact_heatmap.png` | Genre x impact-dimension heatmap | Genre sensitivity analysis |
| 10 | `competitive_landscape.png` | Four-quadrant bubble map (data depth x social experience) | Multi-dimensional competition analysis |
| 11 | `sensitivity_analysis.png` | alpha/beta/gamma parameter sensitivity | Monte Carlo sensitivity |
| 12 | `feature_correlation_heatmap.png` | Pearson correlation matrix across 11 linguistic features | Feature engineering |

## Illustrative figures (Figure A-L)

Located in `figures/decorative/`, provided as both `.mermaid` source and
`.png` renderings. Full placement guidance is in `docs/Research_Report.md`.

| # | PNG | Title |
|:--|:----|:------|
| A | `fig_value_chain.png` | Music information service value chain |
| B | `fig_evolution_timeline.png` | Evolution timeline (Web 1.0 to generative AI) |
| C | `fig_flywheel_compare.png` | UGC incentive structure comparison |
| D | `fig_lemons_market.png` | Lemons-market mechanism in review markets |
| E | `fig_heterogeneous_trust.png` | Heterogeneous trust curves |
| F | `fig_four_dimensions.png` | Four institutional logics of the AI shock |
| G | `fig_strategy_matrix.png` | Platform strategic response matrix |
| H | `fig_data_value_paradox.png` | Data asset revaluation |
| I | `fig_competitive_map.png` | Competitive positioning map |
| J | `fig_career_path.png` | Trust-economy career paths |
| K | `fig_trust_pyramid.png` | Trust literacy capability model |
| L | `fig_trust_curve.png` | Trust threshold curve (55.8% / 75% breakpoints) |

`figures/decorative/generate_decorative_figures.py` reproduces the PNG
renderings from the Mermaid sources.
