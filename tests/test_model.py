"""Minimal correctness controls. No upstream Rust binary is executed here."""
import numpy as np
import pytest
from emir_audit.model import (
    CASES,
    Circuit,
    DEFAULT,
    backward_euler_peak,
    compare,
    convolution_peak,
    green_kernel,
    ode_peak,
)


def test_physical_pulse_energy_and_peak_current():
    assert DEFAULT.peak_a == pytest.approx(1.0)
    # Area of a triangular 1 A, 0.1 ns pulse = 50 pC = 90 pJ / 1.8 V.
    assert 0.5 * DEFAULT.pulse_duration_ns * 1e-9 * DEFAULT.peak_a == pytest.approx(50e-12)


@pytest.mark.parametrize("name", ["simultaneous", "staggered"])
def test_independent_methods_agree(name):
    centers = CASES[name]
    rk = ode_peak(centers)
    green = convolution_peak(centers)
    assert abs(rk["peak_v"] - green["peak_v"]) < 2e-6
    be = backward_euler_peak(centers, dt_ns=0.01)
    assert abs(be["peak_v"] - green["peak_v"]) < 0.0002


def test_staggered_strictly_worse():
    r = compare()
    for name in ("piecewise_ode", "greens_function_quadrature", "backward_euler_0p01_ns"):
        assert r["comparison"][name]["increase_percent"] > 6.5


def test_illustrative_false_safe_decision():
    r = compare()
    for method in ("piecewise_ode", "greens_function_quadrature", "backward_euler_0p01_ns"):
        assert r["cases"]["simultaneous"]["methods"][method]["within_illustrative_ir_limit"]
        assert not r["cases"]["staggered"]["methods"][method]["within_illustrative_ir_limit"]


def test_decoupled_nodes_remove_phase_advantage():
    # Nearly no inter-node conductance: the two loads cannot reinforce each other.
    c = Circuit(r_coupling_ohm=1e12)
    peak1 = ode_peak(CASES["simultaneous"], c)["peak_v"]
    peak2 = ode_peak(CASES["staggered"], c)["peak_v"]
    assert abs(peak2 - peak1) < 1e-6


def test_shift_both_event_times_does_not_change_peak():
    initial = ode_peak((1.0, 1.1))["peak_v"]
    shifted = ode_peak((1.3, 1.4))["peak_v"]
    assert abs(initial - shifted) < 2e-6


def test_backward_euler_converges_toward_independent_solution():
    centers = CASES["staggered"]
    ref = convolution_peak(centers)["peak_v"]
    e1 = abs(backward_euler_peak(centers, dt_ns=0.01)["peak_v"] - ref)
    e2 = abs(backward_euler_peak(centers, dt_ns=0.001)["peak_v"] - ref)
    assert e2 < e1


def test_linear_energy_scaling():
    c2 = Circuit(pulse_energy_pj=180.0)
    base = ode_peak(CASES["staggered"])["peak_v"]
    doubled = ode_peak(CASES["staggered"], c2)["peak_v"]
    assert doubled / base == pytest.approx(2.0, rel=1e-6)


def test_green_function_causality_and_positivity():
    assert np.all(green_kernel(-0.1) == 0)
    for t in [0.0, 0.1, 0.5, 1.0]:
        assert np.all(green_kernel(t) >= -1e-14)
