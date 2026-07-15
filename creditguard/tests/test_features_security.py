"""Unit tests for FeatureStore and the secure-coding utilities in security.py."""

import os
import unittest

from domain import LoanApplication
from features import FeatureStore
from security import get_api_key, redact, MissingAPIKeyError


class TestFeatureStore(unittest.TestCase):

    def test_computes_the_same_features_for_the_same_application(self):
        """Determinism here is what prevents train/serve skew."""
        app = LoanApplication("A1", 20000.0, 60000.0, 12000.0)
        store = FeatureStore()
        self.assertEqual(store.compute_features(app), store.compute_features(app))

    def test_ratios_are_computed_correctly(self):
        app = LoanApplication("A1", 30000.0, 60000.0, 12000.0)
        features = FeatureStore().compute_features(app)
        self.assertAlmostEqual(features["amount_to_income_ratio"], 0.5)
        self.assertAlmostEqual(features["debt_to_income_ratio"], 0.2)


class TestSecurity(unittest.TestCase):

    def test_missing_api_key_raises(self):
        os.environ.pop("TEST_EMA_API_KEY", None)
        with self.assertRaises(MissingAPIKeyError):
            get_api_key("TEST_EMA_API_KEY")

    def test_present_api_key_is_returned(self):
        os.environ["TEST_EMA_API_KEY"] = "sk-verysecret12345"
        self.assertEqual(get_api_key("TEST_EMA_API_KEY"), "sk-verysecret12345")

    def test_redact_hides_all_but_the_last_characters(self):
        self.assertEqual(redact("sk-verysecret12345"), "**************2345")


if __name__ == "__main__":
    unittest.main()
