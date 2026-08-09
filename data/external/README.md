# External Observed Archives

These files are third-party snapshots of public AOTY and RYM pages. They are
real observations collected by the named dataset authors. They are not
official platform exports and do not provide repeated observations of the same
platform metrics over time.

| Local directory | Source | Snapshot or coverage | Rows used | License | Use in this project |
|:--|:--|:--|--:|:--|:--|
| `aoty_metacritic_30000/` | [Contemporary album ratings and reviews](https://www.kaggle.com/datasets/kauvinlucas/30000-albums-aggregated-review-ratings) by Kauvin Lucas | Releases from 1940 to October 2020; dataset updated 2021-04-13 | 32,358 albums; 116,384 training review excerpts | GPL-2.0 | AOTY critic-user comparison, cross-platform exact matching, real human review sample |
| `aoty_top5000/` | [AOTY 5000 Highest User Rated Music Albums](https://www.kaggle.com/datasets/tabibyte/aoty-5000-highest-user-rated-albums) by tabibyte | Dataset updated 2024-10-20 | 5,000 albums | CC BY 3.0 | AOTY score, rating-volume, and genre snapshot |
| `rym_top5000/` | [Rate Your Music: The Top 5,000 Most Popular Albums](https://www.kaggle.com/datasets/tobennao/rym-top-5000) by Bryan O. | Collected 2022-03-11 | 5,000 albums | Not specified by publisher | RYM score, rating-volume, review-volume, and genre snapshot; redistribution requires separate review |

## Reproduction

```powershell
py src\data_collection\download_archived_datasets.py
py src\analysis\observed_archive_analysis.py
```

The downloader verifies the SHA-256 hashes recorded in
`source_manifest.csv`. It stops on network or checksum failure and never
creates substitute rows.

## Scope

- The AOTY historical archive ends before the release of ChatGPT.
- The RYM archive is a popularity-selected snapshot, while the AOTY 2024 file
  is a high-rating-selected snapshot. Raw totals cannot be compared as market
  shares or platform size.
- Release year describes the album, not the date on which a rating was made.
- Exact matches use normalized artist, title, and release year. They avoid
  fuzzy matching and discard duplicate keys.
- The source archives contain aggregate album records and published critic
  excerpts. No user identifiers are used in the analysis.
