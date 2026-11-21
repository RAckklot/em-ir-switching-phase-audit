#!/usr/bin/env python3
"""Execute original/optimal fixtures, exact math, SPICE, and optional native CLI.
Run from this directory's parent with PYTHONPATH=.; see README.md.
"""
import argparse,json,re,subprocess,hashlib,platform
from pathlib import Path
import numpy as np
from scipy.optimize import minimize_scalar
from emir_audit.exact import droop,extrema
from emir_audit.model import ode_peak,convolution_peak,backward_euler_peak
ROOT=Path(__file__).resolve().parents[1]

def peak(centers):
    t=np.linspace(0,3,3001);v=droop(t,centers).max(axis=1)
    cand=[(v[0],t[0]),(v[-1],t[-1])]
    for i in range(1,len(t)-1):
        if v[i]>0 and v[i]>=v[i-1] and v[i]>=v[i+1]:
            r=minimize_scalar(lambda x:-float(np.max(droop(x,centers))),bounds=(t[i-1],t[i+1]),method='bounded',options={'xatol':1e-14})
            cand.append((-r.fun,r.x))
    v,t=max(cand)
    return {'peak_v':float(v),'time_ns':float(t)}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--ngspice',required=True);ap.add_argument('--native');ap.add_argument('--upstream');a=ap.parse_args()
    out=ROOT/'results';(out/'spice').mkdir(exist_ok=True);(out/'native').mkdir(exist_ok=True)
    ex=extrema();cs={'simultaneous':(1.,1.),'staggered':(1.,1.1),'optimal':(1.,1.+ex['optimal_delay_ns'])}
    result={'analytic_extrema':ex,'cases':{},'versions':{'python':platform.python_version()},'limitations':['synthetic lumped RC grid','no measured silicon','independent unconstrained event phases','no new algorithm claimed']}
    for name,centers in cs.items():
        row={'centers_ns':centers,'closed_form':peak(centers),'ode':ode_peak(centers),'quadrature':convolution_peak(centers),'backward_euler':backward_euler_peak(centers),'spice':{}}
        base='vdd 1.8\npad p\nres p n1 1.0 met1\nres p n2 1.0 met1\nres n1 n2 1.0 met1\ncap n1 1000\ncap n2 1000\n'
        pdn=base+''.join(f'switch n{j+1} 90.0 {c:.15g} 0.1\n' for j,c in enumerate(centers))
        (ROOT/'examples'/f'{name}.pdn').write_text(pdn)
        (ROOT/'examples'/f'{name}.emir').write_text(f'design: {name}\npdn: {name}.pdn\nir_limit_pct: 2.75\n')
        for label,step in [('1ps',1e-12),('0p2ps',2e-13)]:
            lines=['Two-node RC phase audit','VDD p 0 1.8','R1 p n1 1','R2 p n2 1','R12 n1 n2 1','C1 n1 0 1n','C2 n2 0 1n']
            for j,c in enumerate(centers):
                lines.append(f'I{j+1} n{j+1} 0 PWL(0 0 {(c-.05)*1e-9:.16g} 0 {c*1e-9:.16g} 1 {(c+.05)*1e-9:.16g} 0 3n 0)')
            lines+=['.options reltol=1e-10 abstol=1e-14 vntol=1e-12 method=trap','.option measdgt=12',f'.tran {step:.16g} 3n 0 {step:.16g}','.measure tran vmin1 MIN v(n1)','.measure tran vmin2 MIN v(n2)','.control','set numdgt=15','set measdgt=15','run','quit','.endc','.end']
            net=out/'spice'/f'{name}_{label}.cir'
            lines.insert(lines.index('quit'),'set wr_singlescale')
            lines.insert(lines.index('quit'),f'wrdata {net.with_suffix(".dat")} v(n1) v(n2)')
            net.write_text('\n'.join(lines)+'\n')
            proc=subprocess.run([a.ngspice,'-b',str(net)],capture_output=True,text=True)
            (net.with_suffix('.log')).write_text(proc.stdout+'\nSTDERR\n'+proc.stderr)
            if proc.returncode:raise RuntimeError(proc.stderr)
            wave=np.loadtxt(net.with_suffix('.dat'))
            assert wave.shape[1]==3
            vals=np.min(wave[:,1:],axis=0).tolist()
            row['spice'][label]={'peak_v':1.8-min(vals),'node_min_voltages':vals,'exit_code':proc.returncode}
        if a.native:
            cmd=[a.native,'run',str(ROOT/'examples'/f'{name}.emir'),'--json'];proc=subprocess.run(cmd,capture_output=True,text=True)
            (out/'native'/f'{name}.stdout.json').write_text(proc.stdout);(out/'native'/f'{name}.stderr.log').write_text(proc.stderr)
            data=json.loads(proc.stdout)
            row['native']={'exit_code':proc.returncode,'dynamic':data['dynamic'],'ir_met':data['ir_met'],'command':cmd}
            assert abs(data['dynamic']['drop']-row['backward_euler']['peak_v'])<1e-6
        exact=row['closed_form']['peak_v']
        assert abs(row['quadrature']['peak_v']-exact)<2e-10
        assert abs(row['ode']['peak_v']-exact)<2e-7
        assert abs(row['spice']['0p2ps']['peak_v']-exact)<2e-7
        result['cases'][name]=row
    assert abs(result['cases']['optimal']['closed_form']['peak_v']-ex['free_phase_global_peak_v'])<1e-12
    aligned=result['cases']['simultaneous']['closed_form']['peak_v']
    result['optimal_increase_percent']=100*(ex['free_phase_global_peak_v']/aligned-1)
    result['spice_version']=subprocess.run([a.ngspice,'--version'],capture_output=True,text=True).stdout
    if a.upstream:
        result['upstream_commit']=subprocess.check_output(['git','-C',a.upstream,'rev-parse','HEAD'],text=True).strip()
        result['upstream_tracked_diff']=subprocess.check_output(['git','-C',a.upstream,'diff','--exit-code'],text=True)
        result['cargo_lock_sha256']=hashlib.sha256((Path(a.upstream)/'Cargo.lock').read_bytes()).hexdigest()
    if a.native:result['native_binary_sha256']=hashlib.sha256(Path(a.native).read_bytes()).hexdigest()
    (out/'extended.json').write_text(json.dumps(result,indent=2)+'\n')
    for k,v in result['cases'].items(): print(k, {m:(x.get('peak_v') if isinstance(x,dict) else x) for m,x in v.items() if m not in ['spice','native']},v.get('native'))
    print('optimal increase percent',result['optimal_increase_percent'])
if __name__=='__main__':main()
