"""Abstract Factory: matched families of AI-provider objects.

Reference: Gamma et al. (1994) Design Patterns - Abstract Factory.
"""

from abc import ABC, abstractmethod

from domain import LoanApplication
from security import get_api_key


class AIClient(ABC):
    """One product of the family: does the actual scoring call."""

    @abstractmethod
    def complete(self, prompt: str) -> str:
        ...


class PromptBuilder(ABC):
    """The other product of the family: formats an application into a prompt
    string shaped the way this provider's client expects."""

    @abstractmethod
    def build_prompt(self, application: LoanApplication) -> str:
        ...


class AIProviderFactory(ABC):
    """Produces one matched AIClient + PromptBuilder pair."""
    @abstractmethod
    def create_client(self) -> AIClient:
        ...
    @abstractmethod
    def create_prompt_builder(self) -> PromptBuilder:
        ...


class LocalStubClient(AIClient):
    """A deterministic, offline stand-in for a real AI client. No network,
    no randomness - given the same prompt, always returns the same result."""
    def complete(self, prompt: str) -> str:
        return f"stub-response: prompt length {len(prompt)}"


class SimplePromptBuilder(PromptBuilder):
    """Formats a LoanApplication's fields into a plain-text prompt string."""
    def build_prompt(self, application: LoanApplication) -> str:
        return (
            f"Loan Application {application.application_id}: "
            f"requesting {application.amount}, "
            f"annual income {application.annual_income}, "
            f"existing debt {application.existing_debt}."
        )


class LocalStubFactory(AIProviderFactory):
    """The default, always-available factory - no external dependency."""
    def create_client(self) -> AIClient:
        return LocalStubClient()

    def create_prompt_builder(self) -> PromptBuilder:
        return SimplePromptBuilder()


class AnthropicClient(AIClient):
    """Simulates what a real Anthropic-backed client would look like: reads
    its API key from the environment (never a literal, per OWASP guidance),
    so the key can never leak into version control. The response itself is
    still simulated deterministically - swapping in a real SDK call here
    would require no change anywhere else in the codebase."""

    def __init__(self):
        self._api_key = get_api_key("ANTHROPIC_API_KEY")

    def complete(self, prompt: str) -> str:
        return f"anthropic-simulated-response: prompt length {len(prompt)}"


class AnthropicFactory(AIProviderFactory):
    """Simulates what a real Anthropic-backed factory would look like."""
    def create_client(self) -> AIClient:
        return AnthropicClient()

    def create_prompt_builder(self) -> PromptBuilder:
        return SimplePromptBuilder()
