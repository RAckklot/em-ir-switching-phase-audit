#!/usr/bin/env python3
import json,csv
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from emir_audit.exact import droop,extrema
from emir_audit.model import backward_euler_peak,triangle
from scripts.verify_extended import peak
R=Path(__file__).resolve().parents[1];j=json.loads((R/'results/extended.json').read_text())
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
colors=['#326ca5','#d97923','#853f90'];names=['simultaneous','staggered','optimal'];labels=['Aligned','Offset 0.100 ns','Optimal offset 0.505 ns'];t=np.linspace(.85,2.0,5001)
fig,ax=plt.subplots(2,1,figsize=(7.4,5.1),sharex=True,gridspec_kw={'height_ratios':[1,2]},layout='constrained')
for name,label,col in zip(names,labels,colors):
 cs=j['cases'][name]['centers_ns'];total=np.array([sum(triangle(x,c) for c in cs) for x in t]);v=droop(t,cs)[:,1]*1000
 ax[0].plot(t,total,color=col,label=label,linewidth=1.5);ax[1].plot(t,v,color=col,linewidth=1.8)
 tt=j['cases'][name]['closed_form']['time_ns'];vv=j['cases'][name]['closed_form']['peak_v']*1000
 ax[1].plot(tt,vv,'o',color=col,markersize=4);ax[1].annotate(f'{vv:.3f} mV',(tt,vv),xytext=(5,8),textcoords='offset points',fontsize=9,color=col)
ax[0].set_ylabel('Total load current (A)');ax[0].legend(loc='upper right',fontsize=8)
ax[1].axhline(49.5,color='#646d76',ls='--',lw=.8);ax[1].text(1.98,49,'Illustrative 49.5 mV limit',ha='right',va='top',fontsize=8,color='#646d76')
ax[1].set_ylabel('Droop at node n2 (mV)');ax[1].set_xlabel('Time (ns)');ax[1].set_ylim(0,65)
for a in ax:a.grid(alpha=.15)
fig.savefig(R/'figures/validated_waveforms.png',dpi=200);plt.close(fig)
ds=np.unique(np.r_[np.linspace(0,1,101),extrema()['optimal_delay_ns']]);vs=np.array([peak((1.,1.+d))['peak_v']*1000 for d in ds]);fig,ax=plt.subplots(figsize=(7.4,3.3),layout='constrained');ax.plot(ds,vs,color=colors[2],lw=2);ax.axhline(vs[0],color=colors[0],ls='--',label='Aligned baseline');ax.axhline(extrema()['free_phase_global_peak_v']*1000,color='#777',ls=':',label='Attainable response-sum bound');ax.set(xlabel='Offset of second event (ns)',ylabel='Maximum droop, either node (mV)');ax.legend(fontsize=8);ax.grid(alpha=.15);fig.savefig(R/'figures/phase_sweep.png',dpi=200);plt.close(fig)
with (R/'results/phase_sweep.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['offset_ns','peak_mV']);w.writerows(zip(ds,vs))
conv=[]
for dt in [.01,.005,.002,.001,.0005,.0002,.0001]:
 c=j['cases']['optimal']['centers_ns'];v=backward_euler_peak(tuple(c),dt_ns=dt)['peak_v'];ts=np.arange(1,int(3/dt)+1)*dt;charges=[sum(triangle(t,x) for t in ts)*dt*1e3 for x in c]
 conv.append({'dt_ns':dt,'peak_v':v,'error_uV':(extrema()['free_phase_global_peak_v']-v)*1e6,'sampled_charge_pC':charges})
(R/'results/convergence.json').write_text(json.dumps(conv,indent=2)+'\n')
print(json.dumps(conv,indent=2))
