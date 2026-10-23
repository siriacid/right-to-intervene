"""Synthetic right-to-intervene factory benchmark. Discrete time, not a real factory."""
import argparse, csv, math, random, statistics
from collections import deque
from dataclasses import dataclass
from pathlib import Path

STRATEGIES = ('unconstrained','reactive','fixed','adaptive')
SCENARIOS = ('normal','inspection_slowdown','conflicting_priorities','combined')

@dataclass
class Job:
    jid: int
    kind: str
    born: int
    inspected: bool = False

class Factory:
    def __init__(self, strategy, scenario, seed, horizon=240):
        self.strategy,self.scenario,self.horizon=strategy,scenario,horizon
        self.seed=seed
        rng=random.Random(seed)
        self.arrivals=[];self.quality=[]
        for t in range(horizon):
            conflict=scenario in ('conflicting_priorities','combined') and 65<=t<195
            self.arrivals.append(('premium' if rng.random() < (.81 if conflict else .39) else 'standard') if rng.random()<.89 else None)
            self.quality.append(rng.random())
        self.raw=deque();self.buffer=deque();self.inspection=deque();self.ready=deque()
        self.next_id=0;self.delivered=0;self.premium=0;self.standard=0
        self.unsafe_deliveries=0;self.overflow_events=0;self.prevented=0
        self.review_requests=0;self.audit_blocks=0;self.total_delay=0
        self.inspection_completed=0;self.proposals=0
        self.reactive_lock=0;self.throttled=0;self.max_queue=0
        self.completed_inspected=0;self.log=[]
        self.buffer_capacity=7;self.inspection_capacity=3

    def shock(self,t):
        return self.scenario in ('inspection_slowdown','combined') and 70<=t<165

    def new_job(self,kind,t):
        j=Job(self.next_id,kind,t);self.next_id+=1;return j

    def ship(self,j,t,inspected=True):
        self.delivered+=1;self.premium+=(j.kind=='premium');self.standard+=(j.kind=='standard')
        self.total_delay+=t-j.born
        if not inspected:self.unsafe_deliveries+=1
        else:self.completed_inspected+=1

    def run(self):
        for t in range(self.horizon):
            arrival=self.arrivals[t]
            if arrival:self.raw.append(self.new_job(arrival,t))
            slow=self.shock(t)
            can_inspect=(t%4==0 if slow else t%2==0)
            if can_inspect and self.inspection:
                j=self.inspection.popleft();j.inspected=True;self.ready.append(j);self.inspection_completed+=1
            want_produce=bool(self.raw)
            want_bypass=bool(self.buffer) and len(self.buffer)>=5
            want_ship=bool(self.ready)
            self.proposals+=int(want_produce)+int(want_bypass)
            can_bypass=want_bypass;can_produce=want_produce
            if self.strategy=='fixed':
                if want_bypass:self.prevented+=1
                can_bypass=False
                if len(self.buffer)>=self.buffer_capacity:
                    can_produce=False;self.prevented+=int(want_produce)
            elif self.strategy=='adaptive':
                # WARNING: oracle future arrivals and disturbance schedule. Research scaffold only.
                expected_departures=sum(int(((t+k)%4==0 if self.shock(min(self.horizon-1,t+k)) else (t+k)%2==0)) for k in range(1,9))
                projected=len(self.buffer)+len(self.inspection)+sum(x is not None for x in self.arrivals[t+1:min(self.horizon,t+9)])-expected_departures
                if want_bypass:self.prevented+=1
                can_bypass=False
                if projected>self.buffer_capacity+self.inspection_capacity-1 or len(self.buffer)>=self.buffer_capacity-1:
                    can_produce=False;self.throttled+=int(want_produce);self.prevented+=int(want_produce)
                    if want_produce and t%8==0:self.review_requests+=1
            elif self.strategy=='reactive':
                if self.reactive_lock>0:
                    if want_bypass:self.prevented+=1
                    can_bypass=False
                    if len(self.buffer)>=self.buffer_capacity:can_produce=False
                    self.reactive_lock-=1;self.audit_blocks+=1
            if want_ship:
                j=self.ready.popleft();self.ship(j,t);transport_used=True
            else:transport_used=False
            if not transport_used and self.buffer and len(self.inspection)<self.inspection_capacity:
                self.inspection.append(self.buffer.popleft());transport_used=True
            if not transport_used and can_bypass and self.buffer:
                j=self.buffer.popleft();self.ship(j,t,False);transport_used=True
                if self.strategy=='reactive':self.review_requests+=1;self.reactive_lock=6
            if can_produce and self.raw:
                j=self.raw.popleft()
                if len(self.buffer)>=self.buffer_capacity:
                    self.overflow_events+=1
                    if self.strategy=='reactive':self.review_requests+=1;self.reactive_lock=6
                else:self.buffer.append(j)
            self.max_queue=max(self.max_queue,len(self.raw)+len(self.buffer)+len(self.inspection)+len(self.ready))
            if (t+1)%20==0:self.log.append({'tick':t+1,'delivered':self.delivered,'unsafe':self.unsafe_deliveries,'overflow':self.overflow_events,'backlog':len(self.raw)+len(self.buffer)+len(self.inspection)+len(self.ready)})
        return {'scenario':self.scenario,'strategy':self.strategy,'seed':self.seed,
            'delivered':self.delivered,'safe_delivered':self.completed_inspected,'premium_delivered':self.premium,
            'standard_delivered':self.standard,'violations':self.unsafe_deliveries+self.overflow_events,
            'uninspected_shipped':self.unsafe_deliveries,'overflow_events':self.overflow_events,
            'review_requests':self.review_requests,'blocked_actions':self.prevented,
            'mean_lead_time':round(self.total_delay/self.delivered,3) if self.delivered else 0,
            'backlog':len(self.raw)+len(self.buffer)+len(self.inspection)+len(self.ready),
            'max_queue':self.max_queue,'throttled':self.throttled}

def simulate(strategy,scenario,seed,horizon):
    f=Factory(strategy,scenario,seed,horizon);return f.run(),f.log

def confidence(values):
    return statistics.mean(values),(1.96*statistics.stdev(values)/math.sqrt(len(values)) if len(values)>1 else 0.)

def save_rows(path,rows):
    if not rows:return
    with open(path,'w',newline='') as fp:
        w=csv.DictWriter(fp,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def execute(out,n=100,horizon=240):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    rows=[];traces=[]
    for sc in SCENARIOS:
        for seed in range(n):
            for st in STRATEGIES:
                r,log=simulate(st,sc,seed,horizon);rows.append(r)
                if seed==0:traces.extend([dict(scenario=sc,strategy=st,**p) for p in log])
    save_rows(out/'trials.csv',rows);save_rows(out/'traces.csv',traces)
    metrics=('delivered','safe_delivered','violations','review_requests','backlog','mean_lead_time','standard_delivered')
    summary=[]
    for sc in SCENARIOS:
        for st in STRATEGIES:
            selected=[r for r in rows if r['scenario']==sc and r['strategy']==st]
            d={'scenario':sc,'strategy':st}
            for metric in metrics:
                m,ci=confidence([r[metric] for r in selected]);d[metric+'_mean']=round(m,3);d[metric+'_ci95']=round(ci,3)
            summary.append(d)
    save_rows(out/'summary.csv',summary)
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        labels=list(SCENARIOS);fig,axs=plt.subplots(1,2,figsize=(14,5),layout='constrained')
        for st in STRATEGIES:
            s=[next(x for x in summary if x['scenario']==sc and x['strategy']==st) for sc in labels]
            axs[0].errorbar(range(len(labels)),[x['safe_delivered_mean'] for x in s],yerr=[x['safe_delivered_ci95'] for x in s],marker='o',capsize=3,label=st)
            axs[1].errorbar(range(len(labels)),[x['violations_mean'] for x in s],yerr=[x['violations_ci95'] for x in s],marker='o',capsize=3,label=st)
        for ax,title,ylabel in [(axs[0],'Verified production','Inspected deliveries / trial'),(axs[1],'Safety outcomes','Violations / trial')]:
            ax.set_xticks(range(len(labels)),[x.replace('_','\n') for x in labels]);ax.set_title(title);ax.set_ylabel(ylabel);ax.grid(alpha=.2)
        axs[0].legend();fig.suptitle(f'Right to Intervene — simulated results (n={n} paired seeds/scenario)')
        fig.savefig(out/'results.png',dpi=180);plt.close(fig)
        fig,ax=plt.subplots(figsize=(8,5),layout='constrained')
        for st in STRATEGIES:
            s=[x for x in summary if x['scenario']=='combined' and x['strategy']==st][0]
            ax.errorbar(s['violations_mean'],s['safe_delivered_mean'],xerr=s['violations_ci95'],yerr=s['safe_delivered_ci95'],fmt='o',capsize=4,label=st)
        ax.set(xlabel='Safety violations per trial (lower is better)',ylabel='Inspected deliveries per trial (higher is better)',title='Combined disturbances: safety–throughput frontier')
        ax.legend();ax.grid(alpha=.2);fig.savefig(out/'tradeoff.png',dpi=180);plt.close(fig)
    except ImportError:print('matplotlib missing; CSV outputs written; pip install matplotlib for charts')
    return summary

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',default='results');p.add_argument('--trials',type=int,default=100);p.add_argument('--horizon',type=int,default=240)
    a=p.parse_args();s=execute(a.out,a.trials,a.horizon)
    for x in s:
        print(f"{x['scenario']:25} {x['strategy']:14} inspected={x['safe_delivered_mean']:6.1f}±{x['safe_delivered_ci95']:4.1f} violations={x['violations_mean']:6.1f}±{x['violations_ci95']:4.1f} reviews={x['review_requests_mean']:5.1f}")
