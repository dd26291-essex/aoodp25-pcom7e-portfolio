"""Demo: the Visitor pattern generating an explainability report per strategy.

Each RiskStrategy is scored, then the same ExplainabilityReportVisitor visits
each one and produces a plain-language description through double dispatch,
without any reporting logic living inside the strategies. Run:

    python demo_visitor.py
"""

from domain import LoanApplication
from strategy import RuleBasedRisk, MLModelRisk, ChallengerRisk
from visitor import ExplainabilityReportVisitor


def main():
    app = LoanApplication("A1", amount=20000.0, annual_income=60000.0, existing_debt=12000.0)
    visitor = ExplainabilityReportVisitor()

    strategies = [
        RuleBasedRisk(),
        MLModelRisk(),
        ChallengerRisk(champion=RuleBasedRisk(), challenger=MLModelRisk()),
    ]

    print("creditguard - Explainability reports (Visitor pattern)")
    print("=" * 58)
    print(f"Application {app.application_id}: amount {app.amount}, "
          f"income {app.annual_income}, debt {app.existing_debt}\n")

    for strategy in strategies:
        score = strategy.score(app)
        report = strategy.accept(visitor)
        print(f"{type(strategy).__name__}")
        print(f"  score       : {score.value:.2f}")
        print(f"  explanation : {score.explanation}")
        print(f"  report      : {report}\n")


if __name__ == "__main__":
    main()
