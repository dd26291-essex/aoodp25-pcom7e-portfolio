"""Unit tests for the Decorator pattern: each decorator adds behaviour
without changing the wrapped strategy's actual scoring result.
"""

import unittest

from domain import LoanApplication
from strategy import RuleBasedRisk
from decorators import LoggingDecorator, AuditDecorator, RateLimitDecorator


class TestDecoratorsPreserveTheResult(unittest.TestCase):

    def test_logging_decorator_does_not_change_the_score(self):
        app = LoanApplication("A1", 20000.0, 60000.0, 12000.0)
        plain = RuleBasedRisk().score(app)
        decorated = LoggingDecorator(RuleBasedRisk()).score(app)
        self.assertEqual(plain.value, decorated.value)

    def test_stacked_decorators_all_run(self):
        """Logging wraps auditing wraps the real strategy - both layers
        must record something, proving neither was skipped."""
        app = LoanApplication("A1", 20000.0, 60000.0, 12000.0)
        audited = AuditDecorator(RuleBasedRisk())
        stacked = LoggingDecorator(audited)
        stacked.score(app)
        self.assertGreater(len(stacked.log), 0)
        self.assertGreater(len(audited.audit_trail), 0)


class TestRateLimitDecorator(unittest.TestCase):

    def test_allows_calls_up_to_the_limit(self):
        app = LoanApplication("A1", 20000.0, 60000.0, 12000.0)
        limited = RateLimitDecorator(RuleBasedRisk(), limit=2)
        limited.score(app)
        limited.score(app)  # should not raise

    def test_rejects_calls_beyond_the_limit(self):
        app = LoanApplication("A1", 20000.0, 60000.0, 12000.0)
        limited = RateLimitDecorator(RuleBasedRisk(), limit=1)
        limited.score(app)
        with self.assertRaises(RuntimeError):
            limited.score(app)


if __name__ == "__main__":
    unittest.main()
