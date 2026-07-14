"""Custom exception hierarchy for the banking system.

All errors derive from `BankingError`, so a caller can catch every banking error
at once, or catch a specific subclass to react to one kind of failure.
"""

class BankingError(Exception):
    """Base class for every error raised by this banking system.

    A common base means a caller can `except BankingError` to catch any of ours
    at once, while still being able to catch the specific subclasses below.
    """
    pass


class InvalidAmountError(BankingError):
    """Raised when a deposit/withdraw amount is not a positive number."""
    pass


class InsufficientFundsError(BankingError):
    """Raised when a withdrawal would exceed the available balance."""
    def __init__(self, balance, amount):
        # Store the figures so a handler can inspect them, and build a readable
        # message — this exact text becomes the "Actual result" in the testing table.
        self.balance = balance
        self.required = amount
        shortfall = amount - balance
        message = (
            f"Cannot withdraw {amount:.2f} from balance {balance:.2f} (short by {shortfall:.2f})"
        )
        super().__init__(message)


class AccountNotFoundError(BankingError):
    """Raised when a lookup or transfer references an unknown account number."""
    pass
