"""Feature Store: one feature definition shared by training and serving,
eliminating train/serve skew (Sculley et al., 2015).

Conceptual AI-oriented pattern (not GoF): a single point of truth for how
raw application data becomes model input, so the features a model was
trained on are guaranteed to match the features it sees in production.
"""

from domain import LoanApplication


class FeatureStore:
    """Computes the same feature vector for an application whether it is
    being used to train a model offline or to score a live request."""

    def compute_features(self, application: LoanApplication) -> dict:
        return {
            "amount_to_income_ratio": application.amount / application.annual_income,
            "debt_to_income_ratio": application.existing_debt / application.annual_income,
        }
