# docs: simultaneous-switching stimulus is not a universal transient IR-drop upper bound

The pinned README at commit `9ad03f02054ab3c3ec87bc69a684dff2aaf7a8a9` describes the default globally aligned switching as a "strict upper bound". This is not generally valid for **transient peak voltage droop in coupled RC networks**. This is a documentation/modeling-scope observation, **not** a claim that the numerical solver calculates supplied events incorrectly.

The automatically extracted events all use `job.switch_t_ns` ([source](https://github.com/vyges-tools/em-ir/blob/9ad03f02054ab3c3ec87bc69a684dff2aaf7a8a9/src/extract.rs#L487-L495)). By contrast, the existing manually specified `.pdn` format already accepts separate event times.

## Minimal reproduction

```text
vdd 1.8
pad p
res p n1 1.0 met1
res p n2 1.0 met1
res n1 n2 1.0 met1
cap n1 1000
cap n2 1000
switch n1 90.0 1.0 0.1
switch n2 90.0 1.0 0.1
```

Save this as `case.pdn`, with a corresponding `case.emir`:

```text
design: phase_counterexample
pdn: case.pdn
ir_limit_pct: 2.75
```

Change only the final pulse's center from `1.0` to `1.1` ns, or `1.5045911912944` ns for the unrestricted-phase optimum.

| Separation | Native `--json` worst droop | Independent continuous-time reference (ngspice 44.2) |
|---|---:|---:|
| 0 ns | 47.583 mV | 47.628042 mV |
| 0.1 ns | 50.858 mV | 50.991811 mV |
| ~0.504591 ns | 54.465 mV | 55.157437 mV |

All native measurements used the unmodified pinned executable built with `cargo build --release --locked`. The native method agrees with an independently implemented backward-Euler solver at the implicit 0.01 ns timestep. The finer ngspice integration resolves the continuous-time peak; the numerical difference is not an allegation of a solver defect.

At the deliberately illustrative 2.75% IR limit (`49.5 mV` at VDD=1.8 V), aligned switching has JSON `ir_met=true` and the staggered examples have `ir_met=false`. This is **not** a foundry sign-off limit or evidence of a failing chip.

## Suggested clarification

Please describe global timestamp alignment as a *simultaneous-switching stress scenario*, **not as a universal upper bound over admissible timing phases**. It need not be changed in the solver: manual events already support per-event timestamps. The associated local patch `docs/upstream-documentation-and-regression.patch` updates the README and adds a short passing Rust integration regression.

This is a synthetic, model-level counterexample. It does not demonstrate a routed-design failure, feasible device activity trace, silicon defect, or new general verification algorithm. Thanks for considering the documentation correction.

**Additional evidence:** [insert the public portfolio repository URL after publishing it]
