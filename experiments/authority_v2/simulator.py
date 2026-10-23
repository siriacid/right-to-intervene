"""RTI 2.0: causal, paired stochastic factory-control benchmark (synthetic only).

All controllers see the SAME demand, failures, and noisy sensor signals.
No policy gets hidden equipment health or future draws. Observations have 1-tick lag.
"""
from __future__ import annotations
import random
from dataclasses import dataclass
from collections import deque

POLICIES = ('conservative', 'sensor_rule', 'reactive', 'risk_calibrated', 'risk_no_reviews', 'oracle')
SCENARIOS = ('normal', 'wear_shift', 'sensor_noise', 'demand_surge', 'combined')

@dataclass(frozen=True)
class Job:
    jid: int
    arrival: int
    urgent: bool
    deadline: int

@dataclass(frozen=True)
class Trace:
    arrivals: tuple
    hidden_healthy: tuple
    sensor_green: tuple
    standard_online: tuple


def make_trace(scenario: str, seed: int, horizon: int = 360) -> Trace:
    """Generate all exogenous outcomes before choosing any policy.

    Sensor at t reports hidden state at t-1. A random seed defines a paired block.
    """
    if scenario not in SCENARIOS:
        raise ValueError(scenario)
    rng = random.Random(seed + 27_182)
    healthy, arrivals, online, sensor = [], [], [], []
    state = True
    for t in range(horizon):
        active = 100 <= t < 260
        wear = scenario in ('wear_shift', 'combined') and active
        surge = scenario in ('demand_surge', 'combined') and active
        noisy = scenario in ('sensor_noise', 'combined')
        if state:
            state = rng.random() >= (0.055 if wear else 0.014)
        else:
            state = rng.random() < (0.022 if wear else 0.105)
        healthy.append(state)
        # Independent production cells (A: urgent capable, B: standard capable).
        # The shared inspection input buffer absorbs both production streams.
        arrivals_t = []
        rate_a = 0.42 if not surge else 0.73
        rate_b = 0.36 if not surge else 0.53
        if rng.random() < rate_a:
            arrivals_t.append((True, 15 if not surge else 12))
        if rng.random() < rate_b:
            arrivals_t.append((False, 45))
        arrivals.append(tuple(arrivals_t))
        # Normal inspection undergoes externally scheduled outages.
        online.append((not (scenario in ('wear_shift','combined') and active and (t % 7 in (0,1)))))
        previous = healthy[t-1] if t else True
        error = 0.29 if noisy else 0.12
        sensor.append(previous if rng.random() >= error else not previous)
    return Trace(tuple(arrivals), tuple(healthy), tuple(sensor), tuple(online))


def bayes_update(prior: float, positive: bool, false_rate: float = 0.12) -> float:
    likelihood_h = (1.0 - false_rate) if positive else false_rate
    likelihood_b = false_rate if positive else (1.0 - false_rate)
    numerator = prior * likelihood_h
    denominator = numerator + (1.0 - prior) * likelihood_b
    return numerator / denominator if denominator else prior


def propagate(p_healthy: float, steps: int = 1, fault: float = 0.014, recovery: float = 0.105) -> float:
    for _ in range(steps):
        p_healthy = p_healthy * (1 - fault) + (1 - p_healthy) * recovery
    return p_healthy


def run_trial(policy: str, scenario: str, seed: int, horizon: int = 360,
              review_budget: int = 10, review_delay: int = 3):
    if policy not in POLICIES or review_budget < 0 or review_delay < 1:
        raise ValueError('Invalid policy or review settings')
    trace = make_trace(scenario, seed, horizon)
    # Every policy starts with equal knowledge; only oracle sees the latent state.
    belief = 0.88
    backlog: list[Job] = []
    delivered = 0; urgent_on_time = 0; standard_on_time = 0
    unsafe_attempts = 0; attempted_fast = 0; reviews = 0
    false_positive_blocks = 0; failed_fast = 0; fast_success = 0
    review_pending: deque = deque(); reviewed_state = None
    reviewed_until = -1; review_open_until = -1
    last_failure_tick = -10000
    sum_queue = 0; brier = 0.0; total_value = 0
    delay_sum = 0; standard_shipped = 0; urgent_shipped = 0
    missed_urgent = 0; missed_standard = 0
    decision_counts = {'allow':0,'restrict':0,'review':0,'revoked':0}
    history = []
    review_by_shift = [0] * ((horizon + 119) // 120)
    jid = 0
    for t in range(horizon):
        # A review completes only after delay; answers are based on health when
        # review was REQUESTED, not hidden current health (stale information).
        while review_pending and review_pending[0][0] <= t:
            _, observed_at, health_then = review_pending.popleft()
            # Propagate the observed historical state forward without knowing
            # intervening hidden transitions. A later sensor may contradict it.
            reviewed_state = propagate(float(health_then), t - observed_at)
            reviewed_until = t + 4
        if t == 0:
            p_now = belief
        else:
            prior_tminus1 = belief
            obs = trace.sensor_green[t]
            posterior_old = bayes_update(prior_tminus1, obs)
            p_now = propagate(posterior_old)
        if reviewed_state is not None and t <= reviewed_until:
            # Treat the delayed verified report as a second, fallible piece of
            # evidence; confidence fades. This is a heuristic fusion method,
            # NOT a claimed Bayes-optimal smoothing algorithm.
            w = 0.55 * (reviewed_until - t + 1) / 5.0
            p_now = (1 - w) * p_now + w * reviewed_state
        belief = p_now
        brier += (p_now - float(trace.hidden_healthy[t])) ** 2
        for urgent, slack in trace.arrivals[t]:
            backlog.append(Job(jid, t, urgent, t + slack)); jid += 1
        # Sort by earliest deadline; ties break by entry timestamp and id.
        backlog.sort(key=lambda j: (j.deadline, j.arrival, j.jid))

        def finish(j: Job):
            nonlocal delivered, urgent_on_time, standard_on_time, total_value
            nonlocal delay_sum, standard_shipped, urgent_shipped
            delivered += 1; delay_sum += t - j.arrival
            on_time = t <= j.deadline
            if j.urgent:
                urgent_shipped += 1; urgent_on_time += int(on_time)
            else:
                standard_shipped += 1; standard_on_time += int(on_time)
            total_value += (7 if j.urgent else 3) if on_time else (1 if j.urgent else 0.5)

        # Conventional inspector processes one unit every two ticks; all shipped
        # items must pass either this verified inspector or the fast verified lane.
        if t % 2 == 0 and trace.standard_online[t] and backlog:
            finish(backlog.pop(0))
        # Rapid lane has capacity 1 every two ticks; same final QA interlock.
        if t % 2 == 1 and backlog:
            candidate = backlog[0]
            green = trace.sensor_green[t]
            remaining = review_budget - review_by_shift[t//120]
            urgency = max(0.0, min(1.0, (22-(candidate.deadline - t))/22))
            if policy == 'conservative':
                decision = 'restrict'
            elif policy == 'sensor_rule':
                decision = 'allow' if green else 'restrict'
            elif policy == 'reactive':
                decision = 'allow' if green and t-last_failure_tick > 12 else 'restrict'
            elif policy == 'oracle':
                # Non-deployable reference only; deliberately given hidden state.
                decision = 'allow' if trace.hidden_healthy[t] else 'restrict'
            else:
                # Conservative when failure is costly; dynamically reduces
                # threshold for urgent requests when backlog pressure rises.
                # No policy uses latent state, future arrivals or future faults.
                threshold = max(0.79, 0.92 - 0.035*urgency - 0.035*min(1,len(backlog)/10))
                if p_now >= threshold:
                    decision = 'allow'
                elif policy == 'risk_calibrated' and 0.39 <= p_now < threshold and remaining > 0 and t >= review_open_until:
                    decision = 'review'
                elif p_now < 0.25:
                    decision = 'revoked'
                else:
                    decision = 'restrict'
            decision_counts[decision] += 1
            if decision == 'allow':
                attempted_fast += 1
                if trace.hidden_healthy[t]:
                    fast_success += 1
                    finish(backlog.pop(0))
                    belief = bayes_update(belief, True, false_rate=0.001)
                else:
                    unsafe_attempts += 1; failed_fast += 1
                    # Hard physical interlock blocks release; job remains queued
                    # for reinspection/rework. Unsafe *activation* counts as risk.
                    last_failure_tick = t
                    belief = bayes_update(belief, False, false_rate=0.001)
            elif decision == 'review':
                reviews += 1; review_by_shift[t//120] += 1
                review_pending.append((t+review_delay, t, trace.hidden_healthy[t]))
                review_open_until = t + review_delay
            elif trace.hidden_healthy[t]:
                false_positive_blocks += 1
        sum_queue += len(backlog)
        history.append({'tick':t, 'belief_healthy':round(p_now,4),
                        'actual_healthy':int(trace.hidden_healthy[t]),
                        'backlog':len(backlog),'delivered':delivered,
                        'unsafe_attempts':unsafe_attempts,'reviews':reviews})
    for j in backlog:
        if j.urgent: missed_urgent += 1
        else: missed_standard += 1
    # Meaningful throughput-risk-review objective; not a universal safety metric.
    utility = total_value - 16 * unsafe_attempts - 1.5 * reviews - 0.5 * (missed_urgent + missed_standard)
    metrics = {'scenario':scenario,'policy':policy,'seed':seed,'delivered':delivered,
        'urgent_on_time':urgent_on_time,'standard_on_time':standard_on_time,
        'unsafe_attempts':unsafe_attempts,'reviews':reviews,
        'fast_success':fast_success,'fast_failed':failed_fast,'fast_attempted':attempted_fast,
        'blocked_healthy_slots':false_positive_blocks,'backlog':len(backlog),
        'average_backlog':round(sum_queue/horizon,3),
        'mean_delay':round(delay_sum/delivered,3) if delivered else 0,
        'standard_shipped':standard_shipped,'urgent_shipped':urgent_shipped,
        'prediction_brier':round(brier/horizon,5) if policy != 'oracle' else None,
        'utility':round(utility,3), 'review_capacity':review_budget*len(review_by_shift),
        'hard_interlock_violations':0}
    metrics.update({'n_'+key:val for key,val in decision_counts.items()})
    return metrics,history
