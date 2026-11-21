"""Closed-form triangular-pulse responses for the report's normalized RC model.
Time unit ns; C=1 nF, pad/coupling resistors=1 ohm, current peak=1 A.
This is a reference calculation, not a new general verification algorithm.
"""
import numpy as np
from scipy.optimize import brentq
D=.1
H=D/2

def mode(t,lam,d=D,peak=1.):
    """Response to a triangle centered at zero; y' + lam*y = triangle."""
    x=np.asarray(t,dtype=float)+d/2
    h=d/2
    def ramp(z):
        q=np.maximum(z,0)
        return (lam*q+np.expm1(-lam*q))/lam**2
    v=peak/h*(ramp(x)-2*ramp(x-h)+ramp(x-d))
    # Tail formula avoids cancellation of ramp terms and is strictly nonnegative.
    tail=peak/h*np.exp(-lam*np.maximum(x-d,0))*np.expm1(-lam*h)**2/lam**2
    return np.where(x>=d,tail,v)

def response(t,kind='self',d=D,peak=1.):
    a,b=mode(t,1,d,peak),mode(t,3,d,peak)
    return (a+b)/2 if kind=='self' else (a-b)/2

def extrema():
    def derivative(t):
        i=max(0.,1.-2*abs(t)/D)
        return i-(mode(t,1)+3*mode(t,3))/2
    a=float(brentq(derivative,0,H,xtol=1e-15))
    aa=np.expm1(-H)**2/H
    bb=np.expm1(-3*H)**2/(9*H)
    b=float(H+np.log(3*bb/aa)/2)
    # For d=.1 the off-diagonal impulse response increases throughout [0,d].
    # The cross response rises during the pulse and has one stationary tail peak.
    assert D<np.log(3)/2
    self_peak=float(response(a,'self'));cross_peak=float(response(b,'cross'))
    return dict(self_peak_lag_ns=a,cross_peak_lag_ns=b,
                optimal_delay_ns=b-a,self_peak_v=self_peak,cross_peak_v=cross_peak,
                free_phase_global_peak_v=self_peak+cross_peak)

def droop(t,centers):
    t=np.asarray(t)
    c1,c2=centers
    return np.stack((response(t-c1)+response(t-c2,'cross'),
                     response(t-c1,'cross')+response(t-c2)),axis=-1)

if __name__=='__main__':
    import json
    print(json.dumps(extrema(),indent=2))
