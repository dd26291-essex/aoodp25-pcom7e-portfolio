"""Secure-coding utilities shared across creditguard. Boundary validation
of application data already lives in domain.py (LoanApplication.__post_init__);
this module covers secrets handling and log redaction (OWASP, 2021).
"""

import os


class MissingAPIKeyError(RuntimeError):
    """Raised when a required API key is not present in the environment."""


def get_api_key(env_var: str) -> str:
    """Reads an API key from an environment variable - never from a literal
    in source code, which would leak the secret into version control."""
    key = os.environ.get(env_var)
    if not key:
        raise MissingAPIKeyError(f"environment variable {env_var} is not set")
    return key


def redact(text: str, visible: int = 4) -> str:
    """Masks all but the last `visible` characters, for logging identifiers
    without exposing them in full in log output."""
    if len(text) <= visible:
        return "*" * len(text)
    return "*" * (len(text) - visible) + text[-visible:]
