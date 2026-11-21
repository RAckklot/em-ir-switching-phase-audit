# Reproduce the validated R1 results

Run from the package root. Python 3.12.14, Rust 1.100.0, and ngspice 44.2 were used. `requirements-tested.txt` records exact Python versions; `requirements.txt` retains broader compatible ranges. Install ngspice using your operating system package manager, and pass the executable path below. The archived Debian package hash is in `results/environment.json`.

```bash
python -m pip install -r requirements-tested.txt
PYTHONPATH=. python -m pytest -q
git clone https://github.com/vyges-tools/em-ir.git ../emir-upstream
git -C ../emir-upstream checkout 9ad03f02054ab3c3ec87bc69a684dff2aaf7a8a9
(cd ../emir-upstream && cargo build --release --locked)
(cd ../emir-upstream && cargo test --locked)
PYTHONPATH=. python scripts/verify_extended.py \
  --ngspice /absolute/path/to/ngspice \
  --native ../emir-upstream/target/release/vyges-em-ir \
  --upstream ../emir-upstream
PYTHONPATH=. python scripts/make_extended_figures.py
```

The runner regenerates the native fixtures and SPICE decks, exports high-precision SPICE waveforms and asserts agreement with the analytic reference. Source builds need network access to Git dependencies. Native output is rounded to six decimal volts; compare it with backward Euler, not directly with an arbitrarily tight continuous-time tolerance. A native exit code of zero is not an IR-budget PASS; inspect `ir_met`.

## Proposed upstream regression

The included patch was checked against the pinned commit; the integration regression passed. To repeat on a disposable checkout, first set `PATCH` to the absolute path of `docs/upstream-documentation-and-regression.patch`, then:

```bash
git -C ../emir-upstream apply --check "$PATCH"
git -C ../emir-upstream apply "$PATCH"
(cd ../emir-upstream && cargo test --locked --test switching_phase_regression)
git -C ../emir-upstream apply --reverse "$PATCH"
```

This is a local test, not authorization or instructions to submit upstream. The authoritative native result was produced before adding this regression, with no tracked upstream modifications.

## Independent rechecking

`results/extended.json` contains per-method peaks and source/binary hashes. The original tests cover decoupling, common shifts, linear scaling, convergence and positive causal kernels. The added checks compare the closed form with quadrature, verify the attained response-sum bound, and exercise scaled currents. The phase sweep is an illustration, not the proof of global optimality.

For PDF regeneration, `scripts/build_report.py` uses reportlab 4.4.9 and DejaVu Sans fonts from the standard Linux font directory. It reads the included figures; edit the source script to change report prose. It also regenerates `docs/TECHNICAL_REPORT.md`.
