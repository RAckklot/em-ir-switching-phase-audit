#!/usr/bin/env python3
"""Write portable machine-readable results; no external tool called."""
import argparse
import json
from pathlib import Path
from emir_audit.model import compare


def main():
    p = argparse.ArgumentParser(description="Independent EM-IR staggered-switching audit")
    p.add_argument("--output", default="results/verification.json", type=Path)
    args = p.parse_args()
    r = compare()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(r, indent=2) + "\n", encoding="utf-8")
    print("Two-node RC verification; VDD=1.8 V; illustrative 2.75% IR limit")
    for name in ("simultaneous", "staggered"):
        m = r["cases"][name]["methods"]["greens_function_quadrature"]
        print(f"{name:14s}: {m['peak_v'] * 1000:9.6f} mV  "
              f"({m['drop_percent']:.6f}%)  "
              f"{'PASS' if m['within_illustrative_ir_limit'] else 'FAIL'}")
    print("Relative increase: "
          f"{r['comparison']['greens_function_quadrature']['increase_percent']:.4f}%")
    print(f"Saved: {args.output}")
    print("Status: independent numerical model; native Vyges binary NOT executed by this script.")


if __name__ == "__main__":
    main()
