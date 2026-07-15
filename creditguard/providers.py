"""Abstract Factory: matched families of AI-provider objects.

Reference: Gamma et al. (1994) Design Patterns - Abstract Factory.
"""

from abc import ABC, abstractmethod

from domain import LoanApplication


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
    """Produces one matched AIClient + PromptBuilder pair.

    TODO: declare the two abstract methods every concrete factory must
    provide. Signatures:
        def create_client(self) -> AIClient: ...
        def create_prompt_builder(self) -> PromptBuilder: ...
    """
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


class AnthropicFactory(AIProviderFactory):
    """Simulates what a real Anthropic-backed factory would look like.

    TODO (after LocalStubFactory works): mirror its shape, but imagine this
    is where a real integration would read an API key from an environment
    variable (never a literal - this is your secure-coding evidence for
    Task 1) and construct a real client. For this capstone, the client can
    still just simulate a response deterministically like LocalStubClient -
    the point is showing the pattern lets you swap providers, not shipping
    a production AI integration.
    """
