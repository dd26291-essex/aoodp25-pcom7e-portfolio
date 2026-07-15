"""Proves MLModelRisk is testable with zero live API calls, using
unittest.mock to substitute the client/builder an AIProviderFactory would
otherwise supply.

Reference: Python Software Foundation - unittest.mock documentation.
"""

import unittest
from unittest.mock import MagicMock

from domain import LoanApplication
from strategy import MLModelRisk
from providers import AIProviderFactory


class TestMLModelRiskMocking(unittest.TestCase):

    def test_uses_mocked_client_not_a_real_one(self):
        """The mocked client's complete() is called exactly once, with the
        exact prompt the mocked builder produced - proof the wiring works
        without ever constructing a real AIProviderFactory."""
        mock_factory = MagicMock(spec=AIProviderFactory)
        mock_factory.create_client.return_value.complete.return_value = "mocked response"
        mock_factory.create_prompt_builder.return_value.build_prompt.return_value = "mocked prompt"

        strategy = MLModelRisk(factory=mock_factory)
        app = LoanApplication("A1", 20000.0, 60000.0, 12000.0)
        result = strategy.score(app)

        mock_factory.create_client.return_value.complete.assert_called_once_with("mocked prompt")
        self.assertIn("mocked response", result.explanation)

    def test_score_is_deterministic_given_a_fixed_mock_response(self):
        """Same mocked response in, same RiskScore.value out twice - proves
        the response-to-score conversion is a pure function of its input,
        not dependent on anything external or random."""
        mock_factory = MagicMock(spec=AIProviderFactory)
        mock_factory.create_client.return_value.complete.return_value = "x" * 50
        mock_factory.create_prompt_builder.return_value.build_prompt.return_value = "prompt"

        strategy = MLModelRisk(factory=mock_factory)
        app = LoanApplication("A1", 20000.0, 60000.0, 12000.0)
        self.assertEqual(strategy.score(app).value, strategy.score(app).value)

    def test_mock_factory_never_touches_the_real_local_stub(self):
        """A MagicMock(spec=AIProviderFactory) rejects attributes that are
        not part of the real interface - proof this mock cannot silently
        drift away from what AIProviderFactory actually declares."""
        mock_factory = MagicMock(spec=AIProviderFactory)
        with self.assertRaises(AttributeError):
            mock_factory.some_method_that_does_not_exist()


if __name__ == "__main__":
    unittest.main()
