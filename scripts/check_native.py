#!/usr/bin/env python3
"""Optional end-to-end check with a locally installed Vyges executable.

This is intentionally separate from the mathematical reproducer. If run and
successful, its stdout may be retained as native experimental evidence.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def run(binary: str, name: str):
    job = ROOT / "examples" / f"{name}.emir"
    proc = subprocess.run([binary, "run", str(job), "--json"],
                          capture_output=True, text=True, check=True)
    try:
        res = json.loads(proc.stdout)
    except json.JSONDecodeError as error:
        raise RuntimeError(f"Expected JSON from native tool, received: {proc.stdout[:1500]}") from error
    if res.get("dynamic") is None:
        raise AssertionError(f"Native tool did not report dynamic IR in {name}")
    return res


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--binary", default="vyges-em-ir", help="Path to the compiled upstream executable")
    p.add_argument("--output-dir", type=Path, default=ROOT / "native-outputs")
    args = p.parse_args()
    outputs = {name: run(args.binary, name) for name in ("simultaneous", "staggered")}
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name, output in outputs.items():
        (args.output_dir / f"{name}.json").write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
        d = output["dynamic"]
        print(f"{name}: {d['drop'] * 1000:.5f} mV, {d['drop_pct']:.5f}%")
    a, b = [outputs[n]["dynamic"]["drop"] for n in ("simultaneous", "staggered")]
    assert b > a, "Expected staggered drop to be greater"
    assert a < 0.0495 < b, "Expected illustrative IR threshold to distinguish cases"
    assert outputs["simultaneous"].get("ir_met") is True
    assert outputs["staggered"].get("ir_met") is False
    # The values should be near the upstream solver's source-equivalent backward-Euler results.
    assert abs(a - 0.047583) < 0.0005, "Unexpected native simultaneous value"
    assert abs(b - 0.050858) < 0.0005, "Unexpected native staggered value"
    print("Native upstream verification PASSED. Retain exact binary version/commit in your report.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (subprocess.CalledProcessError, FileNotFoundError, AssertionError, RuntimeError) as exc:
        print(f"Native verification NOT passed: {exc}", file=sys.stderr)
        sys.exit(1)
