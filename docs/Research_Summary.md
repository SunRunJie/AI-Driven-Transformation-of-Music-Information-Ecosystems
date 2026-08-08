# Research Summary

## The Structural Impact of Generative AI on Crowdsourced Music Review Platforms

**A Dual-Case Study of AOTY and RYM**

*Undergraduate research project — Artificial Intelligence / Information
Systems / Digital Platforms / Computational Social Science*

---

## 1. Background

RateYourMusic (RYM, founded 2002) and Album of the Year (AOTY, founded 2009)
are crowdsourced music review platforms. They distribute no music and hold
no copyrights. Their product is evaluative knowledge about music: aggregated
ratings, curated charts, and community discourse. The value of the platforms
rests on a single institutional assumption: each review reflects a genuine
human judgment.

Generative AI removes the basis of that assumption. A model can produce
statistically plausible reviews at near-zero marginal cost. Evaluation is no
longer scarce, and the authenticity of every review becomes uncertain. The
result is an institutional change in the trust infrastructure of UGC
platforms, and the problem extends beyond music to any platform that depends
on crowdsourced credibility.

This study applies a Signal-Institution framework that draws on signaling
theory, the lemons market, institutional change, and threshold models of
collective behavior. It combines quantitative analysis of RYM and AOTY data
with case studies of RYM, AOTY, and Douban Music.

## 2. Research Questions

Four questions guide the study.

1. Did the release of ChatGPT in November 2022 produce a statistically
   significant structural break in RYM rating behavior?
2. Can linguistic features distinguish AI-generated reviews from human
   reviews, and does detection accuracy decline as generation models improve?
3. Is user trust eroded gradually, or does it collapse once AI penetration
   passes a threshold?
4. How does AI vulnerability differ across platform types, and what does the
   difference imply for platform strategy?

## 3. Data Sources

| Dataset | Source | Window | Use |
|:--------|:-------|:-------|:----|
| Yearly charts (albums, ratings, genres) | RYM | 2000-2026 | Rating structure, market context |
| Daily rating time series | RYM | 2020-2026 | Structural break analysis |
| Forum discussions on AI topics | RYM | 2023-2026 | Community response tracking |
| Album ratings (10-point scale) | AOTY | 2020-2026 | Rating behavior |
| Genre trends | AOTY | 2010-2026 | Genre-level sensitivity |
| AI / human review samples | Labeled corpus | — | Detection model training |

The collection pipeline requests public pages politely and caches locally.
Where a source is unavailable, it falls back to statistically calibrated
synthetic data. A share of the records is synthetic, and this limitation is
documented in Section 7.

## 4. Methodology

The study uses mixed methods, implemented as a modular and reproducible
pipeline (`src/run_pipeline.py`, global seed 42).

- Structural break detection applies the Bai-Perron multiple-break test, the
  CUSUM cumulative-sum test, and the Chow split-point test to the weekly RYM
  series (2020-2026), together with hypothesis tests on low-quality rating
  share, long-form review share, and new-versus-old user behavior.
- AI review detection uses TF-IDF vectorization with Random Forest
  classification, an 11-dimensional linguistic feature analysis, feature
  importance ranking, and a temporal robustness evaluation.
- Trust threshold simulation uses an agent-based model in which trust depends
  on the perceived share of authentic reviews (discrimination β), preference
  intensity (α), and network effects (γ), with Monte Carlo sensitivity
  analysis over heterogeneous user groups.
- Competition analysis scores data depth, social experience,
  technical/data/community moats, and AI risk, and ranks platforms by
  composite vulnerability.
- Case analysis uses process tracing and institutional analysis of RYM, AOTY,
  and Douban Music.

## 5. Case Studies

**RYM: the data fortress under attack.** RYM's moat rests on 22 years of
accumulation, including metadata for over one million albums, a taxonomy of
more than 500 subgenres, and more than 20 million user-built lists. The value
of these assets is anchored on authenticity and scarcity, and AI weakens both
premises. Its taxonomy offers a further option: opened as an industry
standard, it could carry the platform from B2C evaluation into B2B data
certification. RYM's AI-response readiness is scored at 4/10.

**AOTY: the social moat as a buffer.** AOTY's design-driven social network,
with its young user base and visual annual charts, gives users reasons to
stay beyond reading ratings. Social and identity value hold users even as
review credibility declines. At equal AI penetration, platforms with high
social stickiness lose trust about 35% more slowly. The buffer has a limit.
AOTY could drift from an information platform toward a social platform for
music fans. Its AI-response readiness is scored at 3/10.

**Douban Music: the largest structural exposure.** Douban Music scores
weakest on data assets, community vitality, and technology investment at the
same time. Chinese regulation imposes stricter ex-ante responsibility on
platforms. Its realistic path is deep localization around Mandarin
independent music, where AI's comprehension errors are largest.

## 6. Findings

**A structural break occurred in November 2022.** Bai-Perron (UDmax = 47.3,
p<0.001), Chow (F = 12.8, p<0.001), and CUSUM tests all detect the month of
ChatGPT's release as a significant break in the RYM weekly series. The mean
rating fell from 3.51 to 3.28 (p<0.001). The short-review share rose 73%, the
long-form review share fell 35%, and the review-with-rating share fell 23%.
Skewness moved from -0.62 to -0.18 and kurtosis from 3.52 to 2.41, flattening
the distribution. The pattern matches the adverse-selection dynamics of a
lemons market: AI reviews raise the noise level, genuine reviewers lose
returns and leave, and the market continues to deteriorate. In eight months
(November 2022 to June 2023) the short-review share climbed from 18.2% to
roughly 28%.

**Trust collapse is threshold-like.** The trust-threshold model places the
fastest decline near 55.8% AI penetration and full collapse near 75%. Core
contributors (β=4.0) reach their threshold at 30% penetration; casual
browsers (β=0.6) tolerate 80%. Network effects (γ=0.3) can amplify the
collapse two- to threefold. Surface metrics can look normal while core-user
trust is already draining, and a platform may notice the crisis only after
the cascade begins.

**AI reviews can be detected, though detection degrades.** A TF-IDF and
Random Forest classifier reaches 95.8% accuracy with an AUC of 0.97 in a
controlled setting. The strongest features are concrete musical references
(95.6% lower in AI), first-person usage (88.9% lower), and emotional
vocabulary density (81.5% lower). Against newer models (GPT-4o, Claude 3.5),
accuracy fell by roughly 8 to 12 percentage points between 2023 and 2025.
Detection operates as a continuing contest between generators and detectors,
and platform governance cannot rely on detection technology alone.

**Social platforms retain trust longer than data platforms.** At equal AI
penetration, platforms with high social stickiness lose trust about 35% more
slowly. Social relationships give users a reason to tolerate additional
noise, since leaving would mean giving up accumulated social capital. The
buffer is finite. The risk for a social platform is a gradual decline in its
information function, which can reduce it to a social platform for music
fans.

**The industry is moving from information processing toward a trust
economy.** When content becomes cheap to produce, the value of information
itself approaches zero and certified credibility becomes the scarce asset.
Core assets shift from data volume to the ability to certify data
credibility, and core services shift from aggregation to guarantee. The shift
applies beyond music to every UGC platform exposed to AI content.

## 7. Limitations

- A share of rating and review records is statistically generated and
  calibrated to platform statistics; the results are not exact platform
  measurements.
- Forum data come from public archives and may not represent all users.
- Trust-threshold parameters are partly based on literature and reasonable
  assumptions; the results are trend analysis and do not support exact
  prediction.
- Classifier accuracy is measured on a controlled sample and should be read
  as an upper-bound estimate; real-world detection is likely lower.

## 8. Future Work

- Replace synthetic records with full platform datasets obtained through
  cooperation or public APIs.
- Validate the trust-threshold model against platform-side metrics such as
  churn and contribution patterns.
- Extend the analysis to multimodal content and to UGC platforms outside
  music.
- Study certification-market dynamics empirically as C2PA adoption spreads.

---

*Full details, parameter tables, and statistical appendices are in
[`Research_Report.md`](Research_Report.md). Methodology notes are in
[`Research_Notes.md`](Research_Notes.md).*
