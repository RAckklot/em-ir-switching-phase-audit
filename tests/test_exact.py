"""Validation of the new closed form against the older independent quadrature."""
import numpy as np
import pytest
from emir_audit.exact import droop,extrema,response
from emir_audit.model import convolution_droop, Circuit, convolution_peak

@pytest.mark.parametrize('centers',[(1.,1.),(1.,1.1),(1.,1.+extrema()['optimal_delay_ns'])])
def test_closed_form_against_independent_quadrature(centers):
    for t in [.94,.975,1.025,1.08,1.15,1.55,1.8]:
        assert np.allclose(droop(t,centers),convolution_droop(t,centers),atol=2e-12,rtol=1e-10)

def test_free_phase_bound_is_attained():
    ex=extrema();t=1.+ex['cross_peak_lag_ns'];cs=(1.,1.+ex['optimal_delay_ns'])
    assert abs(droop(t,cs)[1]-ex['free_phase_global_peak_v'])<1e-13
    ts=np.linspace(0,3,3001)
    for delay in np.linspace(-.8,.8,81):
        assert np.max(droop(ts,(1.,1.+delay)))<=ex['free_phase_global_peak_v']+1e-13

def test_response_extrema_are_local_maxima():
    ex=extrema()
    for kind,t in [('self',ex['self_peak_lag_ns']),('cross',ex['cross_peak_lag_ns'])]:
        assert response(t,kind)>response(t-1e-4,kind)
        assert response(t,kind)>response(t+1e-4,kind)

def test_analytic_causality_and_passivity():
    ts=np.linspace(-1,8,10001)
    assert np.all(response(ts)>=-1e-13)
    assert np.all(response(ts,'cross')>=-1e-13)
    assert np.all(response(ts[ts<-.05])==0)

def test_one_milliamp_scaling_preserves_relative_violation():
    small=Circuit(pulse_energy_pj=.09)
    a=convolution_peak((1.,1.),small)['peak_v'];b=convolution_peak((1.,1.1),small)['peak_v']
    assert small.peak_a==pytest.approx(.001)
    assert b/a>1.07
