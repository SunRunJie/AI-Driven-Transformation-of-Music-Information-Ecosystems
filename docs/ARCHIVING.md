# Versioning and Archival Releases

The latest archived release is Version 1.0.0, published on 16 August 2026 and preserved by Zenodo at [10.5281/zenodo.21955380](https://doi.org/10.5281/zenodo.21955380). The DOI identifies that frozen release, including its report title, research brief, code, provenance records, and publication figures.

The default branch may contain revisions made after Version 1.0.0. Until a new release is created, those revisions should be cited by commit rather than described as part of the archived DOI record. `VERSION`, `CITATION.cff`, `.zenodo.json`, and the versioned website materials continue to describe the latest archived release.

## Preparing the Next Release

1. Choose the next version number and record the unreleased changes in `CHANGELOG.md`.
2. Run the empirical pipeline in the locked Python 3.12.10 environment.
3. Confirm that `docs/analysis_results.md`, the analysis figures, and the public claims agree.
4. Check that every observed, controlled, synthetic, and scenario output carries the correct evidence label.
5. Update `VERSION`, `CITATION.cff`, `.zenodo.json`, the README, the website citation page, and the versioned research brief to the same version, date, and title.
6. Run `py scripts/check_publication.py` and resolve every reported error.
7. Commit the verified release state and create an annotated Git tag named `vX.Y.Z`.

## GitHub and Zenodo

Create the GitHub release from the verified tag and attach the matching versioned research brief. If the repository remains connected to Zenodo, the GitHub release can create a new archived version under the existing record. Verify the deposited files and metadata before treating the new DOI version as public.

The DOI minted by Zenodo should be recorded in `CITATION.cff`, the README, and the website after the deposit resolves publicly. It should not be inserted into `.zenodo.json` as a pre-existing related identifier for the same deposit.

Never describe an unreleased branch or mutable project page as the frozen object identified by a DOI.
