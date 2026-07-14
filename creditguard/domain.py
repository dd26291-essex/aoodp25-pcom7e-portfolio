"""Value objects shared across the creditguard capstone."""

from dataclasses import dataclass


@dataclass(frozen=True)
class LoanApplication:
    """An immutable snapshot of one loan application.

    TODO: pick the fields a risk decision actually needs. At minimum you will
    want an identifier, the requested amount, and something the strategies can
    use to differentiate low-risk from high-risk applicants (e.g. an income
    figure, an existing-debt figure, a credit history length). Keep it small —
    this is a demonstration, not a real underwriting model.
    """
    # TODO: applicant_id: str
    # TODO: amount: float
    # TODO: ... your fields here


@dataclass(frozen=True)
class RiskScore:
    """The output of any RiskStrategy: a score plus the reasoning behind it.

    TODO: decide the shape. A numeric score (e.g. 0.0-1.0, probability of
    default) is standard, but you also need *why* — an explanation string or a
    list of factors — because Task 2 asks you to show auditability/explain-
    ability, and an opaque float alone cannot support that argument.
    """
    # TODO: value: float
    # TODO: explanation: str


@dataclass(frozen=True)
class Decision:
    """The final approve/decline outcome, derived from a RiskScore.

    TODO: what does a loan officer (or an audit log) need to see? Consider:
    approved: bool, score: RiskScore, threshold used, and a timestamp so the
    AuditVisitor (Phase 1e) has something to report on.
    """
    # TODO: your fields here
