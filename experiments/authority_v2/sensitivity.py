"""Prespecified sensitivity check: 3 review delays by 4 budgets, combined disruption."""
import argparse,csv,statistics
from pathlib import Path
from simulator import run_trial

def main(n=80,out='results'):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    rows=[]
    for delay in (1,3,7):
        for budget in (0,3,10,25):
            data=[run_trial('risk_calibrated','combined',seed,review_budget=budget,review_delay=delay)[0]
                  for seed in range(n)]
            rows.append({'review_delay':delay,'review_budget_per_shift':budget,'n':n,
                         **{field+'_mean':round(statistics.mean(r[field] for r in data),4)
                            for field in ('delivered','unsafe_attempts','reviews','utility','urgent_on_time')}})
    with (out/'review_sensitivity.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        fig,axs=plt.subplots(1,3,figsize=(13,4),layout='constrained')
        for delay in (1,3,7):
            z=[r for r in rows if r['review_delay']==delay]
            for ax,field,name in zip(axs,('unsafe_attempts_mean','delivered_mean','utility_mean'),
                                    ('Risky activations','Verified shipments','Synthetic utility')):
                ax.plot([r['review_budget_per_shift'] for r in z],[r[field] for r in z],'-o',label=f'{delay}-tick review')
                ax.set(xlabel='Review capacity / 120 ticks',ylabel=name)
                ax.grid(alpha=.25)
        axs[0].legend();fig.suptitle('Human review cost & delay sensitivity, combined scenario')
        fig.savefig(out/'review_sensitivity.png',dpi=180);plt.close(fig)
    except ImportError:pass
    for r in rows:print(r)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--trials',type=int,default=80);parser.add_argument('--out',default='results')
    args=parser.parse_args();main(args.trials,args.out)
