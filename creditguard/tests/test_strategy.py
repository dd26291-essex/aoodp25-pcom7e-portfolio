"""Unit tests for the Strategy pattern: RuleBasedRisk, MLModelRisk,
ChallengerRisk - all interchangeable behind the RiskStrategy interface.
"""

import unittest

from domain import LoanApplication
from strategy import RiskStrategy, RuleBasedRisk, MLModelRisk, ChallengerRisk


class TestRuleBasedRisk(unittest.TestCase):

    def test_low_risk_application_scores_zero(self):
        app = LoanApplication("A1", 20000.0, 60000.0, 12000.0)
        result = RuleBasedRisk().score(app)
        self.assertEqual(result.value, 0.0)

    def test_high_risk_application_triggers_both_rules(self):
        app = LoanApplication("A2", 250000.0, 60000.0, 40000.0)
        result = RuleBasedRisk().score(app)
        self.assertEqual(result.value, 0.8)
        self.assertIn("exceeds 3x annual income", result.explanation)
        self.assertIn("existing debt is", result.explanation)


class TestMLModelRisk(unittest.TestCase):

    def test_default_factory_produces_deterministic_score(self):
        app = LoanApplication("A1", 20000.0, 60000.0, 12000.0)
        strategy = MLModelRisk()
        self.assertEqual(strategy.score(app).value, strategy.score(app).value)


class TestChallengerRisk(unittest.TestCase):

    def test_returns_only_the_champion_score(self):
        app = LoanApplication("A1", 20000.0, 60000.0, 12000.0)
        challenger = ChallengerRisk(champion=RuleBasedRisk(), challenger=MLModelRisk())
        result = challenger.score(app)
        self.assertEqual(result.value, RuleBasedRisk().score(app).value)

    def test_records_both_scores_for_comparison(self):
        app = LoanApplication("A1", 20000.0, 60000.0, 12000.0)
        challenger = ChallengerRisk(champion=RuleBasedRisk(), challenger=MLModelRisk())
        challenger.score(app)
        self.assertIn("champion", challenger.last_comparison)
        self.assertIn("challenger", challenger.last_comparison)


class TestPolymorphism(unittest.TestCase):

    def test_all_strategies_satisfy_the_same_interface(self):
        """Every concrete strategy can be treated identically by calling
        code - the caller never needs to know which one it holds."""
        app = LoanApplication("A1", 20000.0, 60000.0, 12000.0)
        strategies: list[RiskStrategy] = [
            RuleBasedRisk(),
            MLModelRisk(),
            ChallengerRisk(champion=RuleBasedRisk(), challenger=MLModelRisk()),
        ]
        for strategy in strategies:
            result = strategy.score(app)
            self.assertIsInstance(result.value, float)
            self.assertIsInstance(result.explanation, str)


if __name__ == "__main__":
    unittest.main()
