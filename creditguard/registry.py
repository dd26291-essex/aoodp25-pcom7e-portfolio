"""Model Registry: lifecycle and versioning for AI-backed risk models.

Conceptual AI-oriented pattern (not GoF): tracks which model version is
live, so a deployment can be rolled back without redeploying code.
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ModelVersion:
    """One registered version of a model, with its current lifecycle stage."""
    name: str
    version: str
    stage: str = "development"
    registered_at: str = field(default_factory=lambda: datetime.now().isoformat())


class ModelRegistry:
    """Tracks every registered model version. Invariant: at most one version
    of a given model name is ever in "production" at once - promoting a new
    version automatically retires the old one, the same conservation-style
    guarantee Unit 6 used for account balances."""

    def __init__(self):
        self._versions: list[ModelVersion] = []

    def register(self, name: str, version: str) -> ModelVersion:
        mv = ModelVersion(name=name, version=version)
        self._versions.append(mv)
        return mv

    def promote(self, name: str, version: str, stage: str) -> None:
        if stage == "production":
            for mv in self._versions:
                if mv.name == name and mv.stage == "production":
                    mv.stage = "retired"
        for mv in self._versions:
            if mv.name == name and mv.version == version:
                mv.stage = stage
                return
        raise ValueError(f"no registered version {name}:{version}")

    def get_production(self, name: str):
        matches = [mv for mv in self._versions if mv.name == name and mv.stage == "production"]
        return matches[0] if matches else None
