"""Unit tests for the Abstract Factory: LocalStubFactory produces a
matched, working client/prompt-builder pair with no external dependency.
"""

import unittest

from domain import LoanApplication
from providers import AIProviderFactory, LocalStubFactory


class TestLocalStubFactory(unittest.TestCase):

    def test_produces_a_working_client_and_builder(self):
        factory = LocalStubFactory()
        client = factory.create_client()
        builder = factory.create_prompt_builder()

        app = LoanApplication("A1", 20000.0, 60000.0, 12000.0)
        prompt = builder.build_prompt(app)
        response = client.complete(prompt)

        self.assertIsInstance(prompt, str)
        self.assertIsInstance(response, str)

    def test_client_is_deterministic(self):
        client = LocalStubFactory().create_client()
        self.assertEqual(client.complete("same prompt"), client.complete("same prompt"))


class TestAbstractness(unittest.TestCase):

    def test_factory_interface_cannot_be_instantiated_directly(self):
        with self.assertRaises(TypeError):
            AIProviderFactory()


if __name__ == "__main__":
    unittest.main()
