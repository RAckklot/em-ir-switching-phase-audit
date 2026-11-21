# v1.0.0 — Validated technical reproduction (21 November 2026)

Initial archival release of the **EM-IR switching-phase reproducibility audit (R1)**.

## Results

- Simultaneous events: **47.628046 mV** (closed form), **47.583 mV** (native Rust).
- Events separated by 0.1 ns: **50.991913 mV** (closed form), **50.858 mV** (native Rust).
- Unrestricted-phase optimum at approximately **0.504591191 ns**: **55.157458 mV** (closed form), **54.465 mV** (native Rust).
- The continuous-time optimum exceeds the simultaneous result by **15.8088%** in the specified *synthetic* RC model.
- Validated archive records 17 passing Python checks, 45 passing pinned upstream tests, 1 passing proposed Rust regression and independent ngspice 44.2 runs.

## Scope

This is a reproducible, **source-specific modeling-assumption audit** and proposed documentation correction, not a new EDA sign-off algorithm, a real-chip defect, a peer-reviewed paper or a commercial product.

Full evidence and limitations: `EM_IR_Validated_Report.pdf` and `docs/TECHNICAL_REPORT.md`.
AI assistance and reproducibility provenance are disclosed in those documents.
