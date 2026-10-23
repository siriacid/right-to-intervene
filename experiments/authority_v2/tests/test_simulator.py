import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from simulator import make_trace, run_trial, POLICIES,SCENARIOS, bayes_update

class TestRTI(unittest.TestCase):
    def test_paired_exogenous_randomness(self):
        self.assertEqual(make_trace('combined',23),make_trace('combined',23))
        self.assertNotEqual(make_trace('combined',23),make_trace('combined',24))
    def test_repeatability(self):
        for p in POLICIES:
            self.assertEqual(run_trial(p,'combined',12)[0],run_trial(p,'combined',12)[0])
    def test_hard_interlock(self):
        for p in POLICIES:
            for sc in SCENARIOS:
                result,_=run_trial(p,sc,13)
                self.assertEqual(result['hard_interlock_violations'],0)
                self.assertLessEqual(result['fast_success'],result['fast_attempted'])
                self.assertEqual(result['fast_success']+result['fast_failed'],result['fast_attempted'])
    def test_reviews_capped(self):
        for sc in SCENARIOS:
            r,_=run_trial('risk_calibrated',sc,4,review_budget=3)
            self.assertLessEqual(r['reviews'],r['review_capacity'])
        r,_=run_trial('risk_calibrated','normal',2,review_budget=0)
        self.assertEqual(r['reviews'],0)
    def test_no_oracle_confusion(self):
        # The oracle is the only policy explicitly using trace.hidden_healthy
        r,_=run_trial('oracle','combined',21)
        self.assertEqual(r['unsafe_attempts'],0)
    def test_sensor_updates(self):
        self.assertGreater(bayes_update(.5,True),.5)
        self.assertLess(bayes_update(.5,False),.5)
    def test_different_horizon(self):
        r,_=run_trial('risk_calibrated','normal',21,horizon=120)
        self.assertLessEqual(r['reviews'],10)

if __name__=='__main__': unittest.main()
