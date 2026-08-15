# Versioning and archival release

The website, report, code, provenance records, and generated figures are treated as one versioned research object. Version `1.0.0` is dated 16 August 2026.

## Before creating a release

1. Run the empirical pipeline with the locked Python 3.12 environment.
2. Confirm that `docs/analysis_results.md` and the twelve analysis figures match the public claims.
3. Confirm that `VERSION`, `CITATION.cff`, `.zenodo.json`, the PDF filename, and the website citation page use the same version and date.
4. Commit the verified files and create an annotated Git tag named `v1.0.0`.

## GitHub release

Create a GitHub release from tag `v1.0.0`. Use the title `Music Information Ecosystems v1.0.0` and attach `website/assets/research-brief-v1.0.0.pdf`. Copy the evidence-status paragraph from `CHANGELOG.md` into the release notes.

## Zenodo

1. Sign in to Zenodo using the GitHub account that owns the repository.
2. Enable the repository in Zenodo's GitHub integration before publishing the GitHub release.
3. Publish the `v1.0.0` GitHub release. Zenodo will create a version DOI and a concept DOI.
4. Verify the deposit metadata against `.zenodo.json` before publishing the Zenodo record.
5. Add the assigned DOI to `CITATION.cff`, `.zenodo.json`, `website/cite.html`, the README, and the recommended citation.

Never display a DOI until the corresponding deposit resolves publicly.

## OSF alternative

If OSF is preferred, create a public project, upload the release archive and PDF, register a frozen project version, and add the resulting persistent URL to the same citation surfaces. Do not label a mutable project URL as a DOI.
