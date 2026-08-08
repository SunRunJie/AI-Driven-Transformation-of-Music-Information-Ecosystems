# Research Notes

Notes on the methodology, data, and decisions behind this study. This document
is intended for readers who want to understand *how* the project was carried
out, not only what it found.

## 1. Project scope

This project studies how generative AI affects crowdsourced music review
platforms, using **RateYourMusic (RYM, founded 2002)** and **Album of the Year
(AOTY, founded 2009)** as dual cases. The object of study is the
*evaluative knowledge* these platforms produce — aggregated ratings, curated
charts, and community discourse — and the institutional trust on which that
knowledge depends.

The guiding framework is the **Signal-Institution framework**: the AI shock is
interpreted as an institutional change in the "trust infrastructure" of
user-generated-content (UGC) platforms, not merely a technical disruption.

## 2. Data sources and collection

### 2.1 Sources

| Dataset | Platform | Window | Purpose |
|:--------|:---------|:-------|:--------|
| `rym_yearly_charts_2000_2026.csv` | RYM | 2000-2026 | Album-level ratings, rating counts, genres |
| `rym_ratings_timeline.csv` | RYM | 2020-2026 | Daily rating aggregates for representative albums |
| `rym_forum_ai_discussions.csv` | RYM | 2023-2026 | Community discourse on AI-related topics |
| `aoty_album_ratings.csv` | AOTY | 2020-2026 | User ratings (10-point scale) |
| `aoty_genre_trends_2010_2026.csv` | AOTY | 2010-2026 | Genre-level rating trends |

### 2.2 Collection strategy

The scrapers in `src/data_collection/` follow a layered strategy:

1. **Polite requests** to public pages (bounded rate, configured delays).
2. **Local caching** of HTML responses (24-hour freshness window) to avoid
   repeated requests.
3. **Statistically calibrated synthetic generation** when a remote source is
   unavailable or parsing fails. Synthetic records are marked
   (`is_synthetic=True`, `source_dataset` column) and calibrated to known
   platform statistics (e.g., RYM's left-skewed ~3.3/5 mean rating; AOTY's
   ~7.2/10 distribution).

Because of step 3, **some records in `data/raw/` are synthetic**. This is a
deliberate, documented limitation (see Section 6), not an omission.

## 3. Methodology

### 3.1 Structural break analysis (`src/analysis/structural_break_analysis.py`)

Tests whether rating behavior changed significantly around the ChatGPT
release (2022-11-01):

- **CUSUM test** — cumulative deviations with bootstrap significance.
- **Chow test** — mean comparison around a specified break date with
  Levene's variance check and Cohen's *d* effect size.
- **Bai-Perron** — automatic multiple-breakpoint detection.
- **Hypothesis tests H1-H3** — low-quality rating share, long-form review
  share, and new-vs-old user behavior divergence.

### 3.2 AI review detection (`src/analysis/ai_review_analysis.py`)

Trains a TF-IDF + Random Forest classifier on labeled human/AI review samples,
extracts 11 linguistic feature families, ranks feature importance, and
evaluates how detection accuracy changes as models improve.

### 3.3 Trust threshold model (`src/analysis/trust_threshold_analysis.py`)

An agent-based model of trust: user trust depends on perceived share of
authentic reviews (discrimination β), preference intensity (α), and network
effects (γ). The model identifies the **critical penetration** where trust
declines fastest (~55.8%) and the **collapse point** (~75%), plus
heterogeneous thresholds across user types.

### 3.4 Platform competition analysis (`src/analysis/platform_competition_analysis.py`)

Scores platforms on data depth, social engagement, technical/data/community
moats, and AI risk, and derives composite vulnerability rankings.

### 3.5 Visualization and reporting

`src/visualization.py` produces all 12 analysis figures (300 dpi, academic
style). `src/report_generator.py` assembles the markdown report from pipeline
results.

## 4. Key parameters

All parameters are centralized in `src/config.py` (global seed `42`).
Notable values:

| Parameter | Value | Meaning |
|:----------|:------|:--------|
| `CHATGPT_RELEASE_DATE` | `2022-11-01` | Structural break date |
| `CUSUM_THRESHOLD` | `1.96` | 95% confidence threshold |
| `TRUST_MODEL_PARAMS` | α=0.7, β=2.0, γ=0.3, τ=0.4 | Trust model defaults |
| `TFIDF_MAX_FEATURES` | 2000 | Classifier feature budget |
| `RF_N_ESTIMATORS` | 500 | Random forest size |
| `RANDOM_SEED` | 42 | Global reproducibility seed |

## 5. Document decisions

This repository is the international research edition of a project that was
originally developed for a case-study competition. Two structuring decisions
were made during conversion:

1. **Only the final case study analysis is published.** An earlier,
   intermediate analysis draft was deliberately excluded to keep a single,
   authoritative version. The published report corresponds to the final
   analysis.
2. **Competition-specific career-planning material was not included** in the
   research report. The research conclusions, statistical appendices, and
   reference list are retained in full.

## 6. Limitations

- **Synthetic data.** A share of rating/review records is statistically
  generated rather than scraped. Domain-expert calibration mitigates but does
  not eliminate the gap to real platform data.
- **Forum discourse.** RYM forum data come from publicly accessible archives
  and may not represent all users.
- **Model assumptions.** Trust-threshold parameters are partly derived from
  literature and reasonable assumptions; results should be read as trend
  analysis, not precise prediction.
- **Detection environment.** Classifier accuracy is measured on a controlled
  sample and degrades against newer models; it is an upper-bound estimate of
  real-world detection performance.

## 7. Reproducibility checklist

- [x] Fixed global random seed (`RANDOM_SEED = 42`)
- [x] Preprocessing transformation log
- [x] Centralized configuration (`src/config.py`)
- [x] Modular pipeline (`src/run_pipeline.py`) with independent stages
- [x] Figures saved at 300 dpi
- [x] Methodology and parameters documented (this file + report appendix)
