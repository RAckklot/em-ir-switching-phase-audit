#!/usr/bin/env python3
"""Generate portfolio figure from reproducible RC equations."""
import argparse
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from emir_audit.model import CASES, DEFAULT, backward_euler_trajectory, convolution_peak


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path, default=Path("figures/droop_waveforms.png"))
    args = p.parse_args()
    fig, ax = plt.subplots(figsize=(8.8, 4.6))
    for label, centers in CASES.items():
        t, u = backward_euler_trajectory(centers, dt_ns=0.001)
        worst_per_t = u.max(axis=1) * 1000
        line, = ax.plot(t, worst_per_t, label=label.capitalize(), linewidth=2)
        hi = convolution_peak(centers)
        ax.scatter(hi["time_ns"], 1000 * hi["peak_v"],
                   s=48, zorder=4, color=line.get_color())
        ax.annotate(f"{hi['peak_v'] * 1000:.3f} mV",
                    (hi["time_ns"], 1000 * hi["peak_v"]),
                    xytext=(8, -18 if label == "simultaneous" else 10),
                    textcoords="offset points", fontsize=8)
    threshold_mv = DEFAULT.vdd_v * 0.0275 * 1000
    ax.axhline(threshold_mv, linestyle="--", linewidth=1.2, label="Illustrative 2.75% limit")
    ax.set_xlim(0.85, 1.5)
    ax.set_ylim(0, 60)
    ax.set_xlabel("Time (ns)")
    ax.set_ylabel("Worst-node voltage droop (mV)")
    ax.set_title("Staggered switching can exceed simultaneous-switching droop")
    ax.legend(loc="upper right", fontsize=9)
    ax.grid(alpha=0.2)
    fig.tight_layout()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=180, bbox_inches="tight")
    print(f"Saved: {args.output}")


if __name__ == "__main__":
    main()
