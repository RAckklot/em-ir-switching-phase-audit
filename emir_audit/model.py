"""Two-node RC voltage-droop reproducibility model.

This module implements an independent model of the publicly documented
Vyges em-ir switching-pulse semantics; it is NOT the Vyges Rust solver.

Electrical model (droop below the ideal pad voltage):
    C du/dt + G u = i(t)
where G has 1-ohm pad paths and a 1-ohm inter-node coupling resistor.

Three independent numerical approaches are provided:
  * scipy solve_ivp on the piecewise-smooth ODE;
  * Green-function convolution with scipy quadrature;
  * backward Euler discretization as a source-equivalent control.

All times exposed by this module are nanoseconds.
"""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np
from scipy.integrate import quad, solve_ivp
from scipy.optimize import minimize_scalar


@dataclass(frozen=True)
class Circuit:
    vdd_v: float = 1.8
    r_pad_ohm: float = 1.0
    r_coupling_ohm: float = 1.0
    cap_pf: float = 1000.0
    pulse_duration_ns: float = 0.1
    pulse_energy_pj: float = 90.0

    @property
    def peak_a(self) -> float:
        # The triangular pulse's charge is energy / VDD.
        # Duration: ns to s; energy: pJ to J.
        charge_coulomb = self.pulse_energy_pj * 1e-12 / self.vdd_v
        return 2.0 * charge_coulomb / (self.pulse_duration_ns * 1e-9)

    @property
    def g(self) -> np.ndarray:
        gp, gc = 1 / self.r_pad_ohm, 1 / self.r_coupling_ohm
        return np.array([[gp + gc, -gc], [-gc, gp + gc]])

    @property
    def ns_rate(self) -> float:
        # 1 ns / (1 pF) = 1000 (V/A) in the equation for du/dt_ns.
        return 1000.0 / self.cap_pf


DEFAULT = Circuit()
CASES = {
    "simultaneous": (1.0, 1.0),
    "staggered": (1.0, 1.1),
}


def triangle(t_ns: float, center_ns: float, circuit: Circuit = DEFAULT) -> float:
    h = circuit.pulse_duration_ns / 2.0
    d = abs(t_ns - center_ns)
    return 0.0 if d >= h else circuit.peak_a * (1.0 - d / h)


def stimulus(t_ns: float, centers: tuple[float, float], circuit: Circuit = DEFAULT) -> np.ndarray:
    return np.array([triangle(t_ns, x, circuit) for x in centers])


def rhs(t_ns: float, droop: np.ndarray, centers: tuple[float, float], circuit: Circuit = DEFAULT) -> np.ndarray:
    return circuit.ns_rate * (stimulus(t_ns, centers, circuit) - circuit.g @ droop)


def _breakpoints(centers: tuple[float, float], circuit: Circuit, end_ns: float) -> list[float]:
    h = circuit.pulse_duration_ns / 2.0
    return sorted({0.0, end_ns, *(float(c + offset) for c in centers for offset in (-h, 0.0, h))})


def ode_trajectory(
    centers: tuple[float, float],
    circuit: Circuit = DEFAULT,
    *,
    end_ns: float = 2.0,
    max_step_ns: float = 0.0002,
) -> tuple[np.ndarray, np.ndarray]:
    """Integrate each pulse region independently so corners are never skipped."""
    breaks = _breakpoints(centers, circuit, end_ns)
    x = np.zeros(2)
    times = [0.0]
    values = [x.copy()]
    for a, b in zip(breaks[:-1], breaks[1:]):
        if b <= a:
            continue
        sol = solve_ivp(
            lambda t, u: rhs(t, u, centers, circuit),
            (a, b), x,
            max_step=max_step_ns,
            atol=1e-13,
            rtol=1e-11,
        )
        if not sol.success:
            raise RuntimeError(sol.message)
        x = sol.y[:, -1]
        times.extend(sol.t[1:].tolist())
        values.extend(sol.y[:, 1:].T)
    return np.asarray(times), np.asarray(values)


def peak_from_trajectory(times: np.ndarray, droop: np.ndarray) -> dict:
    index = np.unravel_index(int(np.argmax(droop)), droop.shape)
    return {
        "peak_v": float(droop[index]),
        "time_ns": float(times[index[0]]),
        "node": int(index[1] + 1),
    }


def ode_peak(centers: tuple[float, float], circuit: Circuit = DEFAULT) -> dict:
    return peak_from_trajectory(*ode_trajectory(centers, circuit))


def green_kernel(t_ns: float, circuit: Circuit = DEFAULT) -> np.ndarray:
    """Exact two-node matrix exponential for symmetric pad/coupling topology."""
    if t_ns < 0:
        return np.zeros((2, 2))
    gp, gc = 1.0 / circuit.r_pad_ohm, 1.0 / circuit.r_coupling_ohm
    common = np.exp(-circuit.ns_rate * gp * t_ns)
    difference = np.exp(-circuit.ns_rate * (gp + 2 * gc) * t_ns)
    return 0.5 * circuit.ns_rate * np.array([
        [common + difference, common - difference],
        [common - difference, common + difference],
    ])


def convolution_droop(t_ns: float, centers: tuple[float, float], circuit: Circuit = DEFAULT) -> np.ndarray:
    """Independent causal convolution; split quadrature at pulse apices."""
    h = circuit.pulse_duration_ns / 2.0
    result = np.zeros(2)
    for j, center in enumerate(centers):
        left, right = max(0.0, center - h), min(t_ns, center + h)
        if right <= left:
            continue
        cuts = [left] + ([center] if left < center < right else []) + [right]
        for a, b in zip(cuts[:-1], cuts[1:]):
            for k in range(2):
                result[k] += quad(
                    lambda s: green_kernel(t_ns - s, circuit)[k, j] * triangle(s, center, circuit),
                    a, b, epsabs=1e-13, epsrel=1e-11,
                )[0]
    return result


def convolution_peak(centers: tuple[float, float], circuit: Circuit = DEFAULT) -> dict:
    """Find peak from a bounded dense scan followed by local optimization."""
    time_grid = np.linspace(0.0, 2.0, 201)
    values = np.array([np.max(convolution_droop(t, centers, circuit)) for t in time_grid])
    maxima = []
    for idx in range(1, len(time_grid) - 1):
        if values[idx] >= values[idx - 1] and values[idx] >= values[idx + 1]:
            result = minimize_scalar(
                lambda t: -float(np.max(convolution_droop(t, centers, circuit))),
                bounds=(float(time_grid[idx - 1]), float(time_grid[idx + 1])),
                method="bounded", options={"xatol": 1e-12},
            )
            maxima.append((-float(result.fun), float(result.x)))
    if not maxima:
        raise AssertionError("No interior maxima found; investigate observation horizon")
    peak, when = max(maxima)
    return {
        "peak_v": peak,
        "time_ns": when,
        "node": int(np.argmax(convolution_droop(when, centers, circuit)) + 1),
    }


def backward_euler_trajectory(
    centers: tuple[float, float],
    circuit: Circuit = DEFAULT,
    *,
    dt_ns: float = 0.01,
    end_ns: float = 2.0,
) -> tuple[np.ndarray, np.ndarray]:
    """Fixed-step backward Euler reference, not an em-ir executable invocation."""
    if dt_ns <= 0:
        raise ValueError("dt_ns must be positive")
    m = np.eye(2) + dt_ns * circuit.ns_rate * circuit.g
    inverse_m = np.linalg.inv(m)
    x = np.zeros(2)
    ts = [0.0]
    xs = [x.copy()]
    for step in range(1, int(np.ceil(end_ns / dt_ns)) + 1):
        t_ns = step * dt_ns
        x = inverse_m @ (x + dt_ns * circuit.ns_rate * stimulus(t_ns, centers, circuit))
        ts.append(t_ns)
        xs.append(x.copy())
    return np.asarray(ts), np.asarray(xs)


def backward_euler_peak(centers: tuple[float, float], circuit: Circuit = DEFAULT, dt_ns: float = 0.01) -> dict:
    return peak_from_trajectory(*backward_euler_trajectory(centers, circuit, dt_ns=dt_ns))


def compare(circuit: Circuit = DEFAULT, threshold_percent: float = 2.75) -> dict:
    result = {
        "case_description": "Two-node coupled RC network, triangular 90 pJ events",
        "units": "seconds represented as nanoseconds; peak droop reported in volts",
        "parameters": {
            "vdd_v": circuit.vdd_v,
            "r_pad_ohm": circuit.r_pad_ohm,
            "r_coupling_ohm": circuit.r_coupling_ohm,
            "cap_pf_per_node": circuit.cap_pf,
            "pulse_energy_pj": circuit.pulse_energy_pj,
            "pulse_duration_ns": circuit.pulse_duration_ns,
            "peak_current_a": circuit.peak_a,
            "illustrative_ir_limit_percent": threshold_percent,
        },
        "cases": {},
        "comparison": {},
        "validation_status": {
            "native_upstream_binary_executed": False,
            "independent_scipy_methods_executed": True,
            "real_silicon_measurement": False,
        },
    }
    for name, centers in CASES.items():
        methods = {
            "piecewise_ode": ode_peak(centers, circuit),
            "greens_function_quadrature": convolution_peak(centers, circuit),
            "backward_euler_0p01_ns": backward_euler_peak(centers, circuit),
        }
        for value in methods.values():
            value["drop_percent"] = 100 * value["peak_v"] / circuit.vdd_v
            value["within_illustrative_ir_limit"] = value["drop_percent"] <= threshold_percent
        result["cases"][name] = {"center_times_ns": centers, "methods": methods}
    for method in ("piecewise_ode", "greens_function_quadrature", "backward_euler_0p01_ns"):
        a = result["cases"]["simultaneous"]["methods"][method]["peak_v"]
        b = result["cases"]["staggered"]["methods"][method]["peak_v"]
        result["comparison"][method] = {
            "extra_droop_v": float(b - a),
            "increase_percent": float(100 * (b / a - 1)),
            "ranking": "staggered_deeper" if b > a else "not_staggered_deeper",
        }
    return result
