"""Unit tests for the Visitor pattern: double dispatch produces a
different report per concrete RiskStrategy type."""

import unittest

from domain import LoanApplication
from strategy import RuleBasedRisk, MLModelRisk, ChallengerRisk
from visitor import ExplainabilityReportVisitor


class TestExplainabilityReportVisitor(unittest.TestCase):

    def setUp(self):
        self.visitor = ExplainabilityReportVisitor()
        self.app = LoanApplication("A1", 20000.0, 60000.0, 12000.0)

    def test_dispatches_to_the_correct_method_per_type(self):
        rule_based_report = RuleBasedRisk().accept(self.visitor)
        ml_model_report = MLModelRisk().accept(self.visitor)
        self.assertIn("rule-based", rule_based_report.lower())
        self.assertIn("ai-model-backed", ml_model_report.lower())

    def test_challenger_report_reflects_last_comparison(self):
        challenger = ChallengerRisk(champion=RuleBasedRisk(), challenger=MLModelRisk())
        challenger.score(self.app)
        report = challenger.accept(self.visitor)
        self.assertIn("champion/challenger", report.lower())


if __name__ == "__main__":
    unittest.main()
