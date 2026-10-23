"""Run paired seeded experiments, percentile-bootstrap confidence intervals and figures."""
import argparse, csv, json, statistics
import numpy as np
from collections import defaultdict
from pathlib import Path
from simulator import POLICIES,SCENARIOS,run_trial

METRICS = ('delivered','urgent_on_time','standard_on_time','unsafe_attempts',
           'reviews','average_backlog','prediction_brier','utility')

def write_csv(path,rows):
    if not rows:return
    with open(path,'w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0])); writer.writeheader();writer.writerows(rows)

def boot_ci(values, iterations=1000, seed=42):
    """Paired difference CI: resample seed-indexed paired treatment differences."""
    n=len(values)
    if n<2: return (statistics.mean(values),statistics.mean(values))
    arr=np.asarray(values,dtype=float)
    rng=np.random.default_rng(seed)
    draws=np.mean(arr[rng.integers(0,n,size=(iterations,n))],axis=1)
    return tuple(np.quantile(draws,[.025,.975]).tolist())

def execute(out='results',n=160,horizon=360,review_budget=10,review_delay=3):
    if n < 2:raise ValueError('Use at least 2 paired seeds')
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    trials=[]; timelines=[]
    for scenario in SCENARIOS:
        for seed in range(n):
            for policy in POLICIES:
                row,history=run_trial(policy,scenario,seed,horizon,review_budget,review_delay)
                trials.append(row)
                if seed==0 and policy in ('sensor_rule','risk_calibrated'):
                    timelines.extend([dict(scenario=scenario,policy=policy,**v) for v in history])
    write_csv(out/'trials.csv',trials)
    write_csv(out/'traces_seed0.csv',timelines)
    by_key={(r['scenario'],r['policy'],r['seed']):r for r in trials}
    summary=[]; differences=[]
    for scenario in SCENARIOS:
        for policy in POLICIES:
            batch=[by_key[scenario,policy,seed] for seed in range(n)]
            d={'scenario':scenario,'policy':policy,'n':n}
            for metric in METRICS:
                xs=[r[metric] for r in batch if r[metric] is not None]
                d[metric+'_mean']=round(statistics.mean(xs),4) if xs else None
                d[metric+'_sd']=round(statistics.stdev(xs),4) if len(xs)>1 else None
            summary.append(d)
            if policy=='risk_calibrated':continue
            for metric in METRICS:
                values=[by_key[scenario,'risk_calibrated',seed][metric]-by_key[scenario,policy,seed][metric]
                        for seed in range(n) if by_key[scenario,'risk_calibrated',seed][metric] is not None and by_key[scenario,policy,seed][metric] is not None]
                if not values:continue
                lo,hi=boot_ci(values,seed=seed_index(scenario,policy,metric))
                differences.append({'scenario':scenario,'versus':policy,'metric':metric,'mean_paired_difference':round(statistics.mean(values),4),
                                    'bootstrap_ci_low':round(lo,4),'bootstrap_ci_high':round(hi,4),'n_pairs':len(values)})
    write_csv(out/'summary.csv',summary)
    write_csv(out/'paired_effects.csv',differences)
    manifest={'title':'RTI 2.0 causal authority experiment', 'synthetic':True,'trials':len(trials),'seeds_per_scenario':n,
        'horizon':horizon,'review_budget_per_120_ticks':review_budget,'review_delay_ticks':review_delay,
        'scenario_names':SCENARIOS,'policies':POLICIES,'bootstrap_resamples':1000,
        'caveats':['Oracle can see latent state and is excluded from deployable model comparisons.',
                   'Adaptive risk estimator assumes nominal 12% sensor error even in noisy scenario.',
                   'Human review uses a perfect but delayed historical machine-state report.',
                   'Utility weights are research choices, not validated societal harm valuations.',
                   'Hard interlock blocks shipping unverified items for all controllers.']}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2))
    plot(summary,differences,out)
    return summary,differences

def seed_index(*parts):
    v=917
    for p in parts:
        for c in p:v=(v*33+ord(c))%2**32
    return v

def plot(summary,diffs,out):
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except ImportError:
        print('matplotlib not installed: CSV and JSON outputs still available');return
    lookup={(x['scenario'],x['policy']):x for x in summary}
    fig,axs=plt.subplots(2,2,figsize=(12,8),layout='constrained')
    for ax,metric,title in zip(axs.flat,('delivered','unsafe_attempts','reviews','utility'),
                               ('Inspected deliveries','Unsafe rapid-lane activations','Human reviews','Scenario utility score')):
        for policy in ('conservative','sensor_rule','reactive','risk_calibrated','risk_no_reviews','oracle'):
            ax.plot(range(len(SCENARIOS)),[lookup[sc,policy][metric+'_mean'] for sc in SCENARIOS],marker='o',label=policy)
        ax.set_xticks(range(len(SCENARIOS)),[s.replace('_','\n') for s in SCENARIOS]);ax.set_ylabel(title);ax.grid(alpha=.25)
    axs[0,0].legend(fontsize=8,ncol=2,loc='best')
    fig.suptitle('RTI 2.0 — paired synthetic factory scenarios (descriptive means)')
    fig.savefig(out/'scenario_comparison.png',dpi=190);plt.close(fig)
    fig,ax=plt.subplots(figsize=(9,6),layout='constrained')
    for p in POLICIES:
        r=lookup['combined',p]
        ax.scatter(r['unsafe_attempts_mean'],r['delivered_mean'],s=90)
        ax.annotate(p,(r['unsafe_attempts_mean'],r['delivered_mean']),xytext=(5,5),textcoords='offset points')
    ax.set(xlabel='Unsafe rapid-lane activations / trial (lower is better)',ylabel='Inspected deliveries / trial (higher is better)',
           title='Combined scenario: efficiency vs equipment-risk tradeoff')
    ax.grid(alpha=.25);fig.savefig(out/'risk_throughput.png',dpi=190);plt.close(fig)
    # Show paired effects and uncertainties, rather than independent error bars.
    fig,axs=plt.subplots(1,2,figsize=(12,5),layout='constrained')
    for ax,metric,title in zip(axs,('delivered','unsafe_attempts'),('Difference in deliveries','Difference in risky activations')):
        filtered=[x for x in diffs if x['scenario']=='combined' and x['metric']==metric and x['versus']!='oracle']
        pos=range(len(filtered))
        ax.errorbar([x['mean_paired_difference'] for x in filtered],list(pos),
                    xerr=[[x['mean_paired_difference']-x['bootstrap_ci_low'] for x in filtered],
                          [x['bootstrap_ci_high']-x['mean_paired_difference'] for x in filtered]],fmt='o',capsize=4)
        ax.axvline(0,color='gray',linestyle='--');ax.set_yticks(list(pos),[x['versus'] for x in filtered]);ax.set_xlabel(title)
        ax.set_title('Adaptive minus baseline, paired 95% bootstrap CI')
    fig.savefig(out/'paired_effects.png',dpi=190);plt.close(fig)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',default='results');p.add_argument('--trials',type=int,default=160)
    p.add_argument('--horizon',type=int,default=360);p.add_argument('--review-budget',type=int,default=10)
    p.add_argument('--review-delay',type=int,default=3);a=p.parse_args()
    summary,_=execute(a.out,a.trials,a.horizon,a.review_budget,a.review_delay)
    for row in summary:
        if row['scenario']=='combined':
            print(f"{row['policy']:<19} shipped={row['delivered_mean']:7.2f} unsafe={row['unsafe_attempts_mean']:6.2f} "
                  f"reviews={row['reviews_mean']:6.2f} utility={row['utility_mean']:8.2f}")
