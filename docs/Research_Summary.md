# Research Summary

## Generative AI and the Transformation of Music Information Ecosystems

**A Dual-Case Study of AOTY and RYM**

*Undergraduate research project — Artificial Intelligence / Information
Systems / Digital Platforms / Computational Social Science*

---

## 1. Background

Music review platforms such as RateYourMusic (RYM, founded 2002) and Album of
the Year (AOTY, founded 2009) are information intermediaries. They do not
distribute music; they produce *evaluative knowledge* — aggregated ratings,
curated charts, and community discourse. Their business model rests on a
single institutional assumption: that each review reflects a genuine human
judgment.

Generative AI breaks this assumption. When a model can generate statistically
plausible reviews at near-zero marginal cost, the "scarcity of evaluation"
that gave UGC platforms their value disappears, and the authenticity of every
review becomes uncertain. We argue this is not a technical disruption but an
**institutional change in the trust infrastructure of UGC platforms** — a
problem that generalizes well beyond music to every platform that depends on
crowdsourced credibility.

This project applies a **Signal-Institution framework** (signaling theory,
the lemons market, institutional change, threshold models) to study the AI
shock with quantitative methods and dual-case analysis.

## 2. Research Questions

1. Did the release of ChatGPT (November 2022) produce a statistically
   significant structural break in RYM rating behavior?
2. Can AI-generated reviews be distinguished from human reviews using
   linguistic features, and does detection accuracy degrade as models
   improve?
3. Is user trust eroded linearly, or does it collapse past a threshold?
4. How does AI vulnerability differ across platform types, and what does this
   imply for platform strategy?

## 3. Data Sources

| Dataset | Source | Window | Use |
|:--------|:-------|:-------|:----|
| Yearly charts (albums, ratings, genres) | RYM | 2000-2026 | Rating structure, market context |
| Daily rating time series | RYM | 2020-2026 | Structural break analysis |
| Forum discussions on AI topics | RYM | 2023-2026 | Community response tracking |
| Album ratings (10-point scale) | AOTY | 2020-2026 | Rating behavior |
| Genre trends | AOTY | 2010-2026 | Genre-level sensitivity |
| AI / human review samples | Labeled corpus | — | Detection model training |

*Provenance note:* the collection pipeline requests public pages politely,
caches locally, and falls back to statistically calibrated synthetic data
when a source is unavailable. Some records are therefore synthetic; this is a
documented limitation (Section 7).

## 4. Methodology

Mixed methods, implemented as a modular, reproducible pipeline
(`src/run_pipeline.py`, global seed 42):

- **Structural break detection** — Bai-Perron multiple-break test, CUSUM
  cumulative-sum test, and Chow split-point test on weekly RYM series
  (2020-2026), plus hypothesis tests on low-quality rating share, long-form
  review share, and new-vs-old user behavior.
- **AI review detection** — TF-IDF vectorization + Random Forest
  classification with 11-dimensional linguistic feature analysis; feature
  importance ranking; temporal robustness evaluation.
- **Trust threshold simulation** — an agent-based model where trust depends
  on perceived authentic-review share (discrimination β), preference
  intensity (α), and network effects (γ); Monte Carlo sensitivity analysis;
  heterogeneous user groups.
- **Competition analysis** — multi-dimensional scoring (data depth, social
  experience, technical/data/community moats, AI risk) with composite
  vulnerability rankings.
- **Case analysis** — process tracing and institutional analysis of RYM,
  AOTY, and Douban Music.

## 5. Case Studies

**RYM — the data fortress under siege.** RYM's 22-year data accumulation
(1M+ albums, 500+ subgenres, 20M+ user lists) is its moat, but its value is
anchored on authenticity and scarcity — both shaken by AI. Its 500+ subgenre
taxonomy offers a strategic option: open it as an industry standard and pivot
from B2C evaluation to B2B data certification. AI-readiness score: 4/10.

**AOTY — the social moat as buffer.** AOTY's design-driven social network
(youth base, visual charts) provides multi-anchored participation: users stay
for social and identity value even as review credibility falls. At equal AI
penetration, high-social-viscosity platforms collapse trust ~35% slower. The
buffer is finite: AOTY risks degrading from an information platform into a
music-fan social platform. AI-readiness score: 3/10.

**Douban Music — maximum structural exposure.** Weakest on data assets,
community vitality, and technology investment simultaneously; Chinese
regulation imposes stricter ex-ante responsibility. Strategic exit: localize
deeply around Mandarin independent music, where AI's cultural-comprehension
error is largest.

## 6. Findings

**F1. A structural break occurred in November 2022.** Bai-Perron (UDmax =
47.3, p<0.001), Chow (F = 12.8, p<0.001), and CUSUM tests consistently detect
the ChatGPT release month as a significant break in RYM weekly ratings. Mean
rating fell 3.51 → 3.28 (p<0.001); short-review share rose 73%; long-form
review share fell 35%; review-with-rating share fell 23%; skewness moved
-0.62 → -0.18 and kurtosis 3.52 → 2.41 (distribution flattened). The joint
pattern matches Akerlof's lemons-market adverse selection: AI reviews raise
the signal-to-noise ratio, genuine reviewers lose returns and exit, and the
market spirals. In just eight months (Nov 2022 - Jun 2023), short-review
share rose from 18.2% to ~28%.

**F2. Trust collapse is threshold-like, not linear.** The trust-threshold
model locates the fastest trust decline at ~55.8% AI penetration and full
collapse near ~75%. Core contributors (β=4.0) hit their threshold at 30%
penetration; casual browsers (β=0.6) tolerate 80%. Network effects (γ=0.3)
can amplify collapse 2-3x. There is a "silent detonation point": surface
metrics look normal while core-user trust is already draining.

**F3. AI reviews are detectable, but detection degrades.** A TF-IDF + Random
Forest classifier reaches 95.8% accuracy (AUC 0.97) in controlled settings.
Strongest distinguishing features: concrete musical references (-95.6% for
AI), first-person usage (-88.9%), emotional vocabulary density (-81.5%).
Against newer models (GPT-4o, Claude 3.5), accuracy fell roughly 8-12
percentage points between 2023 and 2025. Detection is an arms race, not a
one-time fix.

**F4. Social platforms are more resilient than data platforms.** At equal AI
penetration, high-social-viscosity platforms collapse trust ~35% slower
(social relationships provide extra trust "collateral"). The buffer is
finite; the risk for social platforms is chronic degradation rather than
sudden collapse.

**F5. The industry is shifting from information processing to a trust
economy.** As content becomes cheap to produce, information value approaches
zero and the scarce asset is *certified credibility*. Core assets shift from
data volume to data credibility; core services shift from aggregation to
guarantee. This generalizes to all UGC platforms facing AI content.

## 7. Limitations

- **Synthetic data.** A share of rating/review records is statistically
  generated (calibrated to platform statistics) rather than scraped; results
  should not be treated as exact platform measurements.
- **Forum data.** Public archives may not represent all users.
- **Model assumptions.** Trust-threshold parameters are partly based on
  literature and reasonable assumptions; results are trend analysis, not
  precise prediction.
- **Detection environment.** Classifier accuracy is a controlled, upper-bound
  estimate; real-world detection is likely lower.

## 8. Future Work

- Acquire full platform datasets (cooperation or public APIs) to replace
  synthetic records.
- Validate the trust-threshold model against platform-side metrics (churn,
  contribution patterns).
- Extend analysis to multimodal content and non-music UGC platforms.
- Empirically study certification-market dynamics as C2PA adoption spreads.

---

*Full details, parameter tables, and statistical appendices are in
[`Research_Report.md`](Research_Report.md). Methodology notes are in
[`Research_Notes.md`](Research_Notes.md).*
