# Publication checklist

## Completed in preparation

- [x] Recover the **R1 validated** archive (not the earlier R0 archive).
- [x] Re-run all 17 independent Python tests in the preparation environment.
- [x] Preserve pinned upstream provenance, native logs and ngspice outputs.
- [x] Scan text/logs for obvious private paths, tokens and email addresses.
- [x] Include Zenodo metadata, citation metadata, release notes and GitHub publishing scripts.
- [x] Keep limitations and AI-assistance disclosure visible.

## Publication status (verified 21 November 2026)

- [x] Public repository: https://github.com/RAckklot/em-ir-switching-phase-audit
- [x] GitHub release `v1.0.0`: https://github.com/RAckklot/em-ir-switching-phase-audit/releases/tag/v1.0.0
- [x] README updated to reflect the public release.
- [ ] Account owner: review scientific claims, attribution/AI-assistance disclosure, license and report before promotion.
- [ ] Check the [Zenodo GitHub integration](https://zenodo.org/account/settings/github/): sync and enable this repository if it is not already enabled.
- [ ] Verify whether a Zenodo record and DOI exist for `v1.0.0`; no DOI has been independently verified or linked.
- [ ] If `v1.0.0` was published before Zenodo integration was enabled, create a **new** GitHub release (e.g. `v1.0.1`) after enabling the repository to trigger Zenodo archiving. Do **not** rerun `scripts/create_release.sh`, which attempts to create the already-existing `v1.0.0` tag.
- [ ] Add the exact verified DOI to the README and citation metadata once Zenodo confirms its record.
- [ ] Submit the narrowly scoped [upstream issue](https://github.com/vyges-tools/em-ir/issues/new) using `docs/UPSTREAM_ISSUE_DRAFT.md`; an earlier connected-app attempt returned HTTP 403, so no upstream post is claimed.
- [ ] Share `docs/LINKEDIN_POST.md` using the actual repository and, if minted, DOI links.

## Publication integrity

Do not claim peer review, upstream acceptance, a silicon defect, an original general verification algorithm, or an actual industrial sign-off failure. The 49.5 mV budget is a **synthetic illustrative threshold**.
