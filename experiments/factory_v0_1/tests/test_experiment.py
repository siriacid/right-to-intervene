import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from experiment import simulate, STRATEGIES, SCENARIOS

class FactoryTests(unittest.TestCase):
    def test_reproducibility(self):
        for st in STRATEGIES:
            a,_=simulate(st,'combined',12,120)
            b,_=simulate(st,'combined',12,120)
            self.assertEqual(a,b)
    def test_safe_gates(self):
        for sc in SCENARIOS:
            for st in ('fixed','adaptive'):
                r,_=simulate(st,sc,22,240)
                self.assertEqual(r['violations'],0)
    def test_outputs_consistent(self):
        for st in STRATEGIES:
            r,_=simulate(st,'combined',5,240)
            self.assertEqual(r['safe_delivered']+r['uninspected_shipped'],r['delivered'])
            self.assertEqual(r['violations'],r['uninspected_shipped']+r['overflow_events'])
    def test_unsafe_baseline_exposed(self):
        r,_=simulate('unconstrained','combined',12,240)
        self.assertGreater(r['violations'],0)

if __name__=='__main__':unittest.main()
