# Research Notes

## 1. Evidence Classes

The repository uses four evidence classes.

1. **Observed archive:** documented third-party observations from public AOTY
   or RYM pages.
2. **Collection log:** request URL, time, status, and challenge information.
3. **Controlled corpus or benchmark:** fixed material used to test code and
   compare features.
4. **Scenario:** conditional outputs determined by stated assumptions.

Each figure prints its class. Cross-sectional archive results can support
descriptive claims. Structural change requires repeated observations.

## 2. Structural Proposition

The project proposes that generative AI changes the scarcity structure of
crowdsourced evaluation. Review-like text becomes cheaper to produce, while
credible provenance, contribution history, and documented ranking rules become
more consequential to information trust.

The proposition contains four measurable links:

1. lower production cost may change review volume, style, and provenance;
2. provenance uncertainty may change how users read and weight reviews;
3. changes in attention may affect detailed reviewers and taxonomy
   contributors before they appear in aggregate traffic;
4. platform responses may shift from text-level detection toward provenance,
   ranking design, behavioral controls, human review, and appeals.

The observed archives describe the platform structures on which these links
could operate. A causal estimate requires repeated observations, contributor
behavior, and records of platform-rule changes.

## 3. Observed Archives

`src/analysis/observed_archive_analysis.py` loads and standardizes:

- 32,358 AOTY album records covering releases through October 2020;
- 5,000 high-rated AOTY albums from a file updated on 2024-10-20;
- 5,000 popular RYM albums collected on 2022-03-11;
- 116,384 published critic excerpts in the AOTY/Metacritic training archive.

The source manifest records URLs, publishers, dates, license status,
limitations, and SHA-256 hashes. The RYM publisher gives no license. Raw-file
redistribution needs a separate check.

## 4. Cross-Platform Matching

Artist and title strings are normalized with Unicode decomposition, ASCII
folding, lowercasing, and removal of non-alphanumeric characters. Release year
is part of the key. Exact matches are deduplicated; fuzzy matches are excluded.

The resulting file contains 4,102 matches. AOTY user scores are divided by 20
to place them on RYM's 0-5 scale.

Key results:

- Pearson correlation: 0.9096;
- Spearman correlation: 0.8361;
- mean AOTY-minus-RYM difference: +0.3318;
- median difference: +0.3400;
- share within 0.5 points: 87.37%.

The AOTY archive ends in 2020 and the RYM snapshot was collected in 2022.
Ratings could have changed between snapshots. The association is descriptive.

## 5. Attention and Review Participation

The AOTY top-5,000 file represents 6,277,268 ratings; median ratings per album
are 482. Its rating-count Gini coefficient is 0.6169 and its top 1% account for
12.29% of represented ratings.

The RYM popular file represents 30,418,504 ratings and 506,510 written reviews;
median ratings per album are 3,973. Its rating-count Gini is 0.4005, its top 1%
account for 6.80% of represented ratings, and the median review-to-rating ratio
is 1.652%.

The AOTY file is selected by high user score and the RYM file by popularity.
Raw totals cannot be read as platform size or market share.

## 6. Genre Analysis

Genre strings are split on comma-space delimiters. The chart retains the
twelve shared genres with the largest minimum album count across both files.
For each genre it reports:

- AOTY median user score and rating count;
- RYM median user score, rating count, and reviews per 100 ratings;
- album coverage in each snapshot.

Cell colour is standardized within each metric. Printed values remain in
their original units.

## 7. Text Comparison

The critic sample is drawn deterministically from published review excerpts.
Eligible excerpts contain 120 to 600 characters; one excerpt is sampled per
publication before the final source-diverse sample is drawn. The comparison
group contains 15 fixed, manually authored assistant-style controls. These
controls are not outputs from a documented generative model.

Five-fold stratified out-of-fold predictions give 0.9667 accuracy and 0.9956
AUC. The metrics describe separation between the two constructed groups. The
sample is small and deliberately contrasted, so it supports feature and
pipeline inspection only. It provides no estimate of AI prevalence or
generated-text detector accuracy.

The feature chart uses standardized mean differences. This avoids unstable
percentage changes when a group mean is close to zero.

## 8. Structural-Change Methods

`CHATGPT_RELEASE_DATE = 2022-11-01` is a prespecified candidate date.

- The Welch test compares pre/post means without equal-variance assumptions.
- The Chow test compares pooled and split `y = intercept + beta * time`
  regressions.
- The CUSUM diagnostic detrends the series and uses a permutation-bootstrap
  p-value.
- Dynamic programming minimizes segmented linear-regression SSE; BIC selects
  up to three breaks.

The segmentation is accurately described as Bai-Perron-style least-squares
segmentation. SupF, UDmax, robust covariance corrections, and breakpoint
confidence intervals are not implemented.

The empirical archives contain no repeated rating timestamps. Structural
tests return `not_testable` in default mode. Demo mode uses an
explicitly synthetic series with known breaks.

## 9. Scenario Modules

Trust, policy, four-dimension, and platform-positioning outputs depend on
selected parameters or ordinal scores. Sensitivity plots show how scenario
outputs move when assumptions change. The values do not estimate platform
thresholds, policy effects, current AI penetration, or organizational
readiness.

## 10. Reproducible Commands

```powershell
# Download archives and verify checksums
py src\data_collection\download_archived_datasets.py

# Rebuild observed matches, genre tables, and summary statistics
py src\analysis\observed_archive_analysis.py

# Default analysis with observed archives and provenance checks
py -3.12 src\run_pipeline.py

# Attempt live public-page collection
py -3.12 src\run_pipeline.py --collect

# Explicit synthetic method demonstration
py -3.12 src\run_pipeline.py --demo

# Generate all twelve analysis figures
py -3.12 src\run_complete_analysis.py
```

## 11. Next Data Requirement

The next decisive dataset is a dated panel. It should repeat the same albums
or users across snapshots, preserve rating and review counts, record platform
rule changes, and document exclusions before analysis. That design would make
the November 2022 break test meaningful and allow alternative explanations
such as catalog mix, cohort turnover, seasonality, and ranking changes to be
tested directly.
