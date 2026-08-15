# Generative AI and Structural Change in Crowdsourced Music Information Platforms

**Evidence, mechanisms, and open questions from Album of the Year and Rate Your Music**

RunJie Sun  
School of Information Management, Nanjing University  
Version 1.0.0 - 16 August 2026

## Abstract

This study examines how generative AI may alter the institutional foundations of crowdsourced music-information platforms. Album of the Year (AOTY) and Rate Your Music (RYM) provide cases for studying the production of evaluative content, the allocation of visibility and rating weight, and the provenance of community knowledge. The empirical baseline uses three documented third-party archives: 32,358 historical AOTY album records, an AOTY high-rated snapshot of 5,000 albums, and an RYM popular-album snapshot of 5,000 albums. Across 4,102 exact artist-title-year matches, AOTY and RYM user scores correlate at 0.910, and 87.4% of matched scores differ by no more than 0.5 points on a common 0-5 scale. Rating attention is concentrated within both selected snapshots, while written reviews form a thin participation layer in the RYM archive. These observations identify structures through which low-cost generated contributions could affect information quality and trust. They do not establish that a post-2022 transformation has occurred. Controlled text comparison, synthetic structural-break tests, and governance scenarios are used to develop mechanisms and specify the evidence required for causal evaluation.

## Research question

When review-like prose becomes inexpensive to produce, which institutional resources sustain the credibility and value of crowdsourced music knowledge?

## Evidence architecture

The project separates four evidence classes:

1. **Observed archives:** dated third-party data used for descriptive estimates.
2. **Controlled comparison:** a deliberately contrasted text corpus used to inspect a classification pipeline.
3. **Synthetic method check:** known inputs used to verify structural-break procedures.
4. **Scenario:** outputs determined by stated parameters or analyst-coded scores.

The default empirical pipeline excludes synthetic and unknown-provenance rows. Longitudinal methods return `not_testable` when no repeated observed series exists.

## Evidence base

| Source | Rows used | Selection and date | Permitted use |
|---|---:|---|---|
| AOTY/Metacritic historical archive | 32,358 albums; 116,384 excerpts | Releases through October 2020 | Critic-user and cross-platform description |
| AOTY highest user-rated snapshot | 5,000 albums | Updated 20 October 2024 | Attention and genre structure |
| RYM most-popular snapshot | 5,000 albums | Collected 11 March 2022 | Ratings, reviews, genre, and matching |

Archive URLs, license status, limitations, and SHA-256 checksums are retained in `data/external/source_manifest.csv`.

## Selected findings

### Cross-platform agreement and calibration

Across 4,102 exact artist-title-year matches, AOTY and RYM user scores have Pearson correlation 0.910 and Spearman correlation 0.836. After AOTY scores are rescaled to a 0-5 scale, 87.4% of matches differ by no more than 0.5 points. The median AOTY score is 0.34 points higher. These estimates describe selected archives with different dates and sampling rules; they do not establish longitudinal stability.

### Attention and written participation

The rating-count Gini coefficient is 0.617 in the AOTY high-rated file and 0.400 in the RYM popular file. The RYM snapshot has a median review-to-rating ratio of 1.65%. These values describe concentration and participation within each selected file. They are not estimates of total platform size.

### Critic and user judgments

Across 32,358 AOTY historical album records, critic and user scores correlate at 0.536. Professional and community judgments overlap without collapsing into the same signal.

### Controlled text exercise

A five-fold out-of-fold TF-IDF classifier separates 15 published critic excerpts from 15 fixed assistant-style controls with 96.7% accuracy and AUC 0.996. The controls are not outputs from a documented generative model, and there is no external platform-user holdout. The exercise is not an AI detector evaluation or an estimate of AI-written review prevalence.

## Claims that remain open

- The study does not establish that ChatGPT caused a post-2022 change on AOTY or RYM.
- It does not estimate the prevalence of AI-written platform reviews.
- It does not forecast a calibrated trust-collapse threshold.
- It does not treat analyst-coded platform scores as observed organizational performance.

A causal timing claim requires repeated observations for the same albums or users, a record of ranking and interface changes, prespecified exclusions, and measures of contributor-level mechanisms.

## Reproducibility

Version 1.0.0 provides a Python 3.12.10 reference environment, a hash-locked dependency file, Conda and Docker entry points, an automated GitHub Actions check, fixed random seed 42, archive checksums, and explicit empirical, collection, and demonstration modes.

## Recommended citation

Sun, R. (2026). *Generative AI and structural change in crowdsourced music information platforms: Evidence, mechanisms, and open questions from AOTY and RYM* (Version 1.0.0) [Research report and software]. GitHub. https://github.com/SunRunJie/AI-Driven-Transformation-of-Music-Information-Ecosystems
