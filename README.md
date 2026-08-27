# AI-Driven Transformation of Music Information Ecosystems

[**Explore the research website →**](https://sunrunjie.github.io/AI-Driven-Transformation-of-Music-Information-Ecosystems/)

[**Download the versioned research brief (PDF) →**](https://sunrunjie.github.io/AI-Driven-Transformation-of-Music-Information-Ecosystems/assets/research-brief-v1.0.0.pdf) · [**Cite this work →**](https://sunrunjie.github.io/AI-Driven-Transformation-of-Music-Information-Ecosystems/cite.html)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21955380.svg)](https://doi.org/10.5281/zenodo.21955380)

**Public release:** v1.0.0 · 16 August 2026

**Repository status:** the default branch contains unreleased revisions made after v1.0.0. The DOI identifies the frozen v1.0.0 release; cite later revisions by commit until the next version is archived. See [Versioning and Archival Releases](docs/ARCHIVING.md).

This project studies how generative AI may affect the trust, governance, and
knowledge-production functions of crowdsourced music-information platforms,
using RateYourMusic (RYM) and Album of the Year (AOTY) as motivating cases.

## Evidence Status

The repository now contains three documented third-party archives with real
AOTY and RYM observations. They support descriptive cross-platform, attention,
genre, and text analyses. None contains repeated rating timestamps, so the
post-2022 structural-break hypothesis remains open. The 17,274 legacy
synthetic rows remain marked and excluded from empirical analysis.

| File group | Rows | Current status | Permitted use |
|:--|--:|:--|:--|
| AOTY historical ratings | 32,358 | Third-party observed archive | Critic-user and cross-platform analysis |
| AOTY high-rated snapshot | 5,000 | Third-party observed snapshot | Attention and genre analysis |
| RYM popular snapshot | 5,000 | Third-party observed snapshot | Attention, review, genre, and matching analysis |
| Published critic excerpts | 116,384 | Archived published text | Reproducible human-text sample |
| RYM yearly charts | 2,700 | Synthetic | Parser/analysis demonstration only |
| RYM rating timeline | 11,870 | Synthetic | Time-series benchmark only |
| RYM forum discussions | 15 | Synthetic/template-generated | Demonstration only |
| AOTY album ratings | 2,400 | Synthetic | Demonstration only |
| AOTY genre trends | 289 | Synthetic | Scenario visualization only |
| Collection event logs | 8 | Audit metadata | Documents blocked collection attempts |

Live checks made in August 2026 returned `403 Forbidden` from RYM and a
Cloudflare verification page from AOTY, including when AOTY was rendered in a
real headless Chrome session. The collectors therefore record an unavailable
event and leave existing observation files untouched.

## What Is Implemented

- Auditable AOTY and RYM public-chart collectors with caching, source URLs,
  collection timestamps, challenge detection, and opt-in synthetic fixtures.
- A source manifest with URLs, snapshot dates, license status, limitations,
  and SHA-256 checksums, plus deterministic archive ingestion.
- Exact artist-title-year matching across AOTY and RYM, concentration
  statistics, genre profiles, and reproducible aggregate exports.
- Welch pre/post mean comparison, a standard regression Chow test, a
  bootstrap CUSUM diagnostic, and Bai-Perron-style dynamic-programming
  segmentation with BIC break-count selection.
- A controlled text-classification demonstration using 15 published critic
  excerpts and 15 assistant-style controls with leakage-safe cross-validation.
- Uncalibrated trust, policy, and platform-positioning scenario models.
- Twelve figures whose evidence class is printed directly on each image.

The multiple-break implementation captures the least-squares segmentation
core of Bai-Perron. It does **not** implement the full Bai-Perron inferential
suite such as supF/UDmax tests and confidence intervals.

## Running the Project

### Reference environment (Python 3.12.10)

For an exact, hash-verified installation:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --require-hashes -r requirements-lock.txt
```

The repository also provides `environment.yml`, a `Dockerfile`, and an automated reproducibility workflow. `requirements.txt` retains lower bounds for development; `requirements-lock.txt` is the release-verification environment.

Empirical mode is the default:

```powershell
python src\run_pipeline.py
```

The pipeline loads local external archives, writes aggregate audit outputs,
and generates observed figures. Structural-break hypotheses return
`not_testable` when no repeated empirical series is available.

Re-download the documented archives and verify their checksums with:

```powershell
python src\data_collection\download_archived_datasets.py
```

Attempt live public-page collection explicitly with:

```powershell
python src\run_pipeline.py --collect
```

Run the explicitly synthetic demonstration with:

```powershell
python src\run_pipeline.py --demo
```

Generate all scenario and benchmark figures with source notes:

```powershell
python src\run_complete_analysis.py
```

## Research Interpretation

The repository now supports four findings and boundaries:

1. AOTY and RYM user scores correlate at `r = 0.910` across 4,102 exact album
   matches; 87.4% differ by no more than 0.5 points on a common 0-5 scale.
2. Rating attention is concentrated, while written reviews form a much
   smaller participation layer in the RYM snapshot.
3. Genre profiles differ in score, attention, and review density across the
   two selected archives.
4. Structural-break and trust results remain method checks or scenarios until
   repeated platform observations and behavioral calibration are available.

It does not currently establish that ChatGPT caused a change in RYM or AOTY,
that AI-review prevalence reached any specified percentage, or that platform
trust will collapse at a particular date or penetration level.

See [Research Report](docs/Research_Report.md), [Research Notes](docs/Research_Notes.md),
[data provenance](data/README.md), and [figure inventory](figures/README.md).

## Author

RunJie Sun<br>
School of Information Management, Nanjing University<br>
[Email](mailto:251820093@smail.nju.edu.cn) · [GitHub](https://github.com/SunRunJie)

Research interests: artificial intelligence, information systems, digital
platforms, and computational social science.

## Citation and Archival Status

Version 1.0.0 is permanently archived by Zenodo as [DOI: 10.5281/zenodo.21955380](https://doi.org/10.5281/zenodo.21955380). Citation metadata are provided in `CITATION.cff`; release-deposit metadata are retained in `.zenodo.json`. Cite the archived version using the DOI and the recommended format on the website.
