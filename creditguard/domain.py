"""Value objects shared across the creditguard capstone."""

from dataclasses import dataclass


@dataclass(frozen=True)
class LoanApplication:
    """An immutable snapshot of one loan application."""
    application_id: str
    amount: float
    annual_income: float
    existing_debt: float

    def __post_init__(self):
        # existing_debt may legitimately be zero; amount and income cannot.
        if self.annual_income <= 0:
            raise ValueError(f"annual_income must be positive, got {self.annual_income}")
        if self.amount <= 0:
            raise ValueError(f"amount must be positive, got {self.amount}")
        if self.existing_debt < 0:
            raise ValueError(f"existing_debt cannot be negative, got {self.existing_debt}")


@dataclass(frozen=True)
class RiskScore:
    """The output of any RiskStrategy: a numeric score plus a human-readable reason."""
    value: float
    explanation: str


@dataclass(frozen=True)
class Decision:
    """The final approve/decline outcome, derived from a RiskScore."""
    application_id: str
    approved: bool
    score: RiskScore
    timestamp: str
