"""Unit tests for ModelRegistry: the invariant that at most one version of
a given model is ever in production at once."""

import unittest

from registry import ModelRegistry


class TestModelRegistry(unittest.TestCase):

    def setUp(self):
        self.registry = ModelRegistry()
        self.registry.register("credit-scorer", "v1")
        self.registry.register("credit-scorer", "v2")

    def test_promoting_a_version_makes_it_production(self):
        self.registry.promote("credit-scorer", "v1", "production")
        self.assertEqual(self.registry.get_production("credit-scorer").version, "v1")

    def test_promoting_a_second_version_retires_the_first(self):
        """The invariant: exactly one production version, ever."""
        self.registry.promote("credit-scorer", "v1", "production")
        self.registry.promote("credit-scorer", "v2", "production")
        production_versions = [v for v in self.registry._versions if v.stage == "production"]
        self.assertEqual(len(production_versions), 1)
        self.assertEqual(production_versions[0].version, "v2")

    def test_promoting_an_unregistered_version_raises(self):
        with self.assertRaises(ValueError):
            self.registry.promote("credit-scorer", "v99", "production")


if __name__ == "__main__":
    unittest.main()
