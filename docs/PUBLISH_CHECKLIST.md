# Publication checklist

## Completed in preparation

- [x] Recover the **R1 validated** archive (not the earlier R0 archive).
- [x] Re-run all 17 independent Python tests in the preparation environment.
- [x] Preserve pinned upstream provenance, native logs and ngspice outputs.
- [x] Scan text/logs for obvious private paths, tokens and email addresses.
- [x] Include Zenodo metadata, citation metadata, release notes and GitHub publishing scripts.
- [x] Keep limitations and AI-assistance disclosure visible.

## Account owner steps — not performed in ChatGPT

- [ ] Review the PDF, scientific claims, publication credit (`RAckklot`), and license.
- [ ] Create a **public** repository with `bash scripts/publish_github.sh` (requires `gh auth login` once).
- [ ] Open a narrowly scoped [issue in vyges-tools/em-ir](https://github.com/vyges-tools/em-ir/issues/new) using `docs/UPSTREAM_ISSUE_DRAFT.md`; a connected-app attempt was refused with a GitHub 403 permission error.
- [ ] Link GitHub to [Zenodo](https://zenodo.org/), sync repositories and enable **this** repository **before** creating a GitHub release.
- [ ] Run `bash scripts/create_release.sh --zenodo-enabled` to make `v1.0.0` after verifying the integration toggle.
- [ ] Check the DOI assigned by Zenodo; insert the DOI badge in README *only after it exists*.
- [ ] Share `docs/LINKEDIN_POST.md` with the real repository and DOI links.

## Publication integrity

Do not claim peer review, upstream acceptance, a silicon defect, an original general verification algorithm, or an actual industrial sign-off failure. The 49.5 mV budget is a **synthetic illustrative threshold**.
