"""Strategy pattern: interchangeable risk-scoring algorithms.

Reference: Gamma et al. (1994) Design Patterns — the Strategy pattern.
"""

from abc import ABC, abstractmethod

from domain import LoanApplication, RiskScore


class RiskStrategy(ABC):
    """Common interface every risk-scoring algorithm must implement.

    Whatever calls `score()` should never need to know or care which concrete
    strategy it is holding — that is the whole point of the pattern. Compare
    this shape to BankAccount(ABC) from Unit 6: one abstract method, several
    concrete subclasses, polymorphic dispatch at the call site.

    TODO: declare the one abstract method every strategy must provide.
    Signature suggestion: def score(self, application: LoanApplication) -> RiskScore
    """

    # TODO: @abstractmethod def score(self, application: LoanApplication) -> RiskScore: ...


class RuleBasedRisk(RiskStrategy):
    """Deterministic, explainable scoring using simple hand-written rules.

    TODO: implement score(). Ideas for rules (keep it simple — 3-5 checks):
    - amount relative to some income/limit field on the application
    - a hard reject above some threshold
    - each rule you apply should feed into RiskScore.explanation so the
      decision is auditable (this is your evidence for the "black-box
      coupling" discussion in Task 3).
    """


class MLModelRisk(RiskStrategy):
    """Scoring delegated to an AI model client obtained via an AIProviderFactory.

    TODO (do this AFTER Phase 1c, once providers.py exists): accept a client
    object (or an AIProviderFactory) in __init__, and in score() call the
    client with the application's data, parse whatever it returns into a
    RiskScore. This is the strategy that test_ai_mocking.py (Phase 1h) will
    exercise with a mocked client — no live API calls in the test suite.

    For now, leave a minimal stub so strategy.py imports cleanly; wire the
    real client call once providers.py exists.
    """


# TODO (optional, cut first if time is short — see BUILD_PLAN.md scope-cut order):
# class ChallengerRisk(RiskStrategy):
#     """Runs alongside the champion strategy to compare scores without affecting
#     the live decision — the "runtime behavioural flexibility" argument made concrete."""
