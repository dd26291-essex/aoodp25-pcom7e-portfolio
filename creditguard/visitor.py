"""Visitor pattern: reporting logic separated from the RiskStrategy classes
it reports on. Adding a new report type never touches strategy.py.

Reference: Gamma et al. (1994) Design Patterns - Visitor.
"""

from abc import ABC, abstractmethod


class StrategyVisitor(ABC):
    """One visit method per concrete RiskStrategy type. accept() on each
    strategy calls the matching method here - double dispatch, so no
    isinstance() checks are needed anywhere."""

    @abstractmethod
    def visit_rule_based(self, strategy):
        ...

    @abstractmethod
    def visit_ml_model(self, strategy):
        ...

    @abstractmethod
    def visit_challenger(self, strategy):
        ...


class ExplainabilityReportVisitor(StrategyVisitor):
    """Generates a plain-language description of any RiskStrategy, suited to
    a compliance/audit reader who needs to know how a decision was reached
    without inspecting source code - directly supports the auditability
    and explainability argument in Task 3."""

    def visit_rule_based(self, strategy) -> str:
        return "Deterministic rule-based scorer: fully explainable, no external dependency."

    def visit_ml_model(self, strategy) -> str:
        return (
            f"AI-model-backed scorer using {type(strategy._factory).__name__}: "
            "requires an audit trail, since the scoring logic is external to this codebase."
        )

    def visit_challenger(self, strategy) -> str:
        comparison = strategy.last_comparison
        if comparison is None:
            return "Champion/challenger comparison: no scoring call made yet."
        agree = "agree" if comparison["agreement"] else "disagree"
        return (
            f"Champion/challenger comparison: champion scored "
            f"{comparison['champion'].value}, challenger scored "
            f"{comparison['challenger'].value} ({agree})."
        )
