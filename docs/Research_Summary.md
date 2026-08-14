# Research Summary

## Generative AI and Structural Change in Crowdsourced Music Information Platforms

This project studies how generative AI may change the institutional conditions
under which RateYourMusic (RYM) and Album of the Year (AOTY) produce and govern
crowdsourced music knowledge. It examines the cost of producing review-like
text, the allocation of rating weight and visibility, the provenance of
contributions, and the position of core contributors.

## Research Contribution

The central proposition is a shift in scarcity. Coherent review-like text has
become inexpensive to produce. Credible provenance, accountable contribution
histories, and documented ranking rules carry more of the burden of sustaining
information trust. This proposition links generative content
production to platform structure and generates measurable expectations about
review use, contributor retention, rating weights, and the value of historical
data.

The study contributes three elements: a theoretical account of how generative
AI can transmit through technology, platform rules, organizational response,
and information value; a reproducible comparative baseline for AOTY and RYM;
and an evidence-graded design for testing post-2022 structural change. The
current archives do not estimate AI-review prevalence or causal effects. They
identify the platform conditions through which such effects could operate.

## Evidence Base

Three documented third-party archives now supply real observations.

| Source | Rows used | Date or coverage | Role |
|:--|--:|:--|:--|
| AOTY/Metacritic ratings archive | 32,358 albums | Releases through 2020-10 | Critic-user comparison and AOTY-RYM matching |
| AOTY high-rated snapshot | 5,000 albums | Updated 2024-10-20 | Rating concentration and genre analysis |
| RYM popular snapshot | 5,000 albums | Collected 2022-03-11 | Rating, review, concentration, genre, and matching analysis |
| Published critic excerpts | 116,384 training rows | Historical archive | Deterministic human-text sample |

The five legacy raw CSVs contain 17,274 synthetic rows. They remain marked,
auditable, and excluded from empirical analysis. The synthetic weekly series
is used only to test structural-break code on a known input.

## Main Findings

Across 4,102 exact artist-title-year matches, AOTY and RYM user scores in the
selected archives have a Pearson correlation of 0.910 and a Spearman
correlation of 0.836. After both
scores are put on a 0-5 scale, 87.4% of matched albums lie within half a point.
AOTY's median score is 0.34 points higher. The communities share much of the
same rank order within this matched sample and use different score
calibrations. The differently dated archives do not establish stable agreement
over time.

Attention is concentrated within both selected files. In the AOTY high-rated
top-5,000 snapshot, the top 1% of albums receive 12.3% of represented ratings
and the rating-count Gini is
0.617. In the RYM popular snapshot, the corresponding values are 6.8% and
0.400. The files use different selection rules, so the values describe each
archive and should not be interpreted as a direct platform comparison.

Written reviews form a thin participation layer in the RYM snapshot. The
median album has 3,973 ratings and 72 reviews; the median review-to-rating
ratio is 1.65%. This pattern motivates separate measurement of contributor
retention and review quality alongside aggregate traffic.

AOTY critic and user scores correlate at 0.536 across 32,358 archived albums.
Their mean absolute gap is 7.64 points on the 0-100 scale. Community judgment
and professional criticism overlap without collapsing into the same signal.

The genre analysis uses twelve well-covered genres shared by both snapshots.
Art Rock carries high median scores and attention on both platforms, while RYM
review density ranges from 1.23 reviews per 100 ratings for Art Pop to 2.51
for Pop Rock. Genre should be treated as a sampling stratum in later detector
and retention studies.

## Controlled Text Study

The controlled corpus combines 15 published critic excerpts with 15 manually
authored assistant-style controls. Five-fold out-of-fold evaluation gives
96.7% accuracy and AUC 0.996. These metrics describe separation between two
small, deliberately contrasted groups. Average sentence length is 22.8 words
in the critic sample and 12.9 in the controls; lexical diversity is also
higher in the critic sample.

The exercise compares professional excerpts with constructed controls and has
no model-generated sample or platform-user holdout. It cannot estimate AI
prevalence or detector performance on RYM or AOTY.

## Methods

- Exact artist-title-year entity matching with duplicate-key removal.
- Pearson and Spearman score agreement, scale-difference analysis, Gini
  coefficients, top-share measures, and genre-level medians.
- A regression Chow test at a prespecified date.
- Detrended CUSUM with permutation-bootstrap inference.
- Bai-Perron-style dynamic-programming least-squares segmentation with BIC.
- Leakage-safe five-fold out-of-fold TF-IDF classification.
- Explicit trust, policy, and platform scenarios with sensitivity analysis.

The segmentation code implements the least-squares core associated with
Bai-Perron. It does not implement the full supF/UDmax test suite or breakpoint
confidence intervals.

## Open Empirical Claim

The project cannot yet show a post-November-2022 structural break in platform
behavior. The archives are cross-sections and do not record when individual
ratings were submitted. A dated panel of repeated album or user observations
is still required.

The structural argument currently combines a theory of changing production
conditions with observed platform characteristics: concentrated attention, a
thin written-review layer, and ranking rules that determine how low-count
scores enter charts. AOTY's public changelog documents changes to weighted
charts and rating export from 2025 to 2026. The changelog does not attribute
those changes to generative AI. A dated panel can test whether rating
distributions, review depth, contributor activity, or trust changed after the
release of widely available generative systems.

Full details are in [Research_Report.md](Research_Report.md),
[Research_Notes.md](Research_Notes.md), and
[`data/external/source_manifest.csv`](../data/external/source_manifest.csv).
