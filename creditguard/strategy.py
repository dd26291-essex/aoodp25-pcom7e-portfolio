"""Strategy pattern: interchangeable risk-scoring algorithms.

Reference: Gamma et al. (1994) Design Patterns — the Strategy pattern.
"""

from abc import ABC, abstractmethod

from domain import LoanApplication, RiskScore


class RiskStrategy(ABC):
    """Common interface every risk-scoring algorithm must implement."""
    @abstractmethod
    def score(self, application: LoanApplication) -> RiskScore:
        ...


class RuleBasedRisk(RiskStrategy):
    """Deterministic, explainable scoring using two hand-written rules.

    Each rule that fires appends its reasoning to RiskScore.explanation, so
    the result is auditable rather than an opaque number.
    """
    def score(self, application: LoanApplication) -> RiskScore:
        reasons = []
        risk = 0.0

        # rule 1: loan amount relative to income
        if application.amount > application.annual_income * 3:
            risk += 0.5
            reasons.append(f"amount {application.amount} exceeds 3x annual income")

        # rule 2: existing debt burden
        debt_ratio = application.existing_debt / application.annual_income
        if debt_ratio > 0.4:
            risk += 0.3
            reasons.append(f"existing debt is {debt_ratio:.0%} of income")

        return RiskScore(
            value=min(risk, 1.0),
            explanation="; ".join(reasons) or "no risk factors triggered",
        )


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
