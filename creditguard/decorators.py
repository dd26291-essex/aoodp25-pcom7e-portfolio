"""Decorator pattern: cross-cutting behaviour layered onto any RiskStrategy
without subclassing it.

Reference: Gamma et al. (1994) Design Patterns - Decorator.
"""

from datetime import datetime

from domain import LoanApplication, RiskScore
from strategy import RiskStrategy


class RiskStrategyDecorator(RiskStrategy):
    """Base decorator: wraps a RiskStrategy and delegates to it by default.
    Concrete decorators override score() to add behaviour before/after
    calling super().score(), never touching the wrapped strategy itself."""

    def __init__(self, wrapped: RiskStrategy):
        self._wrapped = wrapped

    def score(self, application: LoanApplication) -> RiskScore:
        return self._wrapped.score(application)

    def accept(self, visitor):
        # a decorator is transparent to the Visitor - it reports on
        # whichever strategy it wraps, not on the decorator itself.
        return self._wrapped.accept(visitor)


class LoggingDecorator(RiskStrategyDecorator):
    """Records a timestamped entry before and after each scoring call."""

    def __init__(self, wrapped: RiskStrategy):
        super().__init__(wrapped)
        self.log: list[str] = []

    def score(self, application: LoanApplication) -> RiskScore:
        self.log.append(f"{datetime.now().isoformat()} scoring {application.application_id}")
        result = super().score(application)
        self.log.append(
            f"{datetime.now().isoformat()} result {result.value} for {application.application_id}"
        )
        return result


class AuditDecorator(RiskStrategyDecorator):
    """Keeps a permanent, append-only record of every decision made - the
    evidence trail an auditor or regulator would need, independent of
    whatever the wrapped strategy actually is."""

    def __init__(self, wrapped: RiskStrategy):
        super().__init__(wrapped)
        self.audit_trail: list[dict] = []

    def score(self, application: LoanApplication) -> RiskScore:
        result = super().score(application)
        self.audit_trail.append({
            "application_id": application.application_id,
            "score": result.value,
            "explanation": result.explanation,
        })
        return result


class RateLimitDecorator(RiskStrategyDecorator):
    """Refuses to process more than `limit` scoring calls - protects the
    wrapped strategy (and any real API behind it) from abuse, an OWASP-style
    boundary control rather than a business rule."""

    def __init__(self, wrapped: RiskStrategy, limit: int = 100):
        super().__init__(wrapped)
        self._limit = limit
        self._count = 0

    def score(self, application: LoanApplication) -> RiskScore:
        if self._count >= self._limit:
            raise RuntimeError(f"rate limit of {self._limit} calls exceeded")
        self._count += 1
        return super().score(application)
