"""Account classes for the banking system.

`BankAccount` is an abstract base holding an encapsulated balance that can only
change through the validated `deposit`, `withdraw` and `get_balance` methods.
`SavingsAccount` and `CurrentAccount` extend it. (The brief names the required
class `BankAccount`.)
"""
import threading

from abc import ABC, abstractmethod

from .exceptions import InvalidAmountError, InsufficientFundsError


class BankAccount(ABC):
    """Abstract base for every account type.

    Subclasses must implement `account_type()`, and may override `_min_balance()`
    to change how far the balance is allowed to fall (e.g. to permit an overdraft).
    """

    def __init__(self, account_number, initial_balance=0.0):
        # Reject a negative opening balance — a normal account can't open in debt.
        if initial_balance < 0:
            raise InvalidAmountError("amount must be positive.")
        self.account_number = account_number   # public: an identifier, not a secret
        self._balance = initial_balance         # non-public: only changed via methods
        # RLock (not Lock): Bank.transfer() acquires this from outside before
        # calling _apply_debit/_apply_credit, so re-entrancy matters here
        # (Python Software Foundation, 2024, threading docs).
        self._lock = threading.RLock()

    @abstractmethod
    def account_type(self):
        """Return a short label for this account kind (e.g. 'Savings').

        Declared abstract, so each subclass MUST provide it — that is what makes
        BankAccount impossible to instantiate on its own.
        """

    def _min_balance(self):
        """Lowest value the balance may legally fall to. Default 0 (no overdraft)."""
        return 0.0

    def deposit(self, amount):
        """Add a positive amount to the balance."""
        # Guard clause: validate before mutating, so a negative "deposit" can't
        # sneak money out through the wrong door.
        if amount <= 0:
            raise InvalidAmountError("Deposit Amount must be positive.")
        with self._lock:
            self._balance += amount

    def withdraw(self, amount):
        """Deduct amount, provided the balance stays at or above its minimum."""
        # Door 1 — is the amount itself valid?
        if amount <= 0:
            raise InvalidAmountError("Withdrawal amount must be positive.")
        # Door 2 — the check AND the subtract share one lock so no thread can
        # slip in between reading the balance and writing the new value.
        with self._lock:
            if self._balance - amount < self._min_balance():
                raise InsufficientFundsError(self._balance, amount)
            self._balance -= amount

    def get_balance(self):
        """Return the balance (read accessor for the encapsulated value)."""
        with self._lock:
            return self._balance

    def _apply_debit(self, amount):
        """Subtract amount from the balance. Assumes the caller already
        holds self._lock — used by Bank.transfer(), which must hold both
        accounts' locks simultaneously across the whole operation to stay
        atomic, so it cannot go through withdraw()'s own locking. Keeping
        the affordability check and the arithmetic here (not in Bank) means
        _balance is still only ever touched from inside this class."""
        if self._balance - amount < self._min_balance():
            raise InsufficientFundsError(self._balance, amount)
        self._balance -= amount

    def _apply_credit(self, amount):
        """Add amount to the balance. Assumes the caller already holds
        self._lock (see _apply_debit)."""
        self._balance += amount

    def __repr__(self):
        # type(self).__name__ prints the *actual* subclass name (SavingsAccount,
        # CurrentAccount) — a small polymorphism touch for clean screenshots.
        return f"{type(self).__name__}({self.account_number}, balance={self._balance:.2f})"


class SavingsAccount(BankAccount):
    """An account that earns interest and cannot be overdrawn."""

    def __init__(self, account_number, initial_balance=0.0, interest_rate=0.0):
        super().__init__(account_number,initial_balance)
        self.interest_rate = interest_rate

    def account_type(self):
        return "Savings"

    def add_interest(self):
        """Add one period's interest (balance * rate) to the balance."""
        # Same lock as deposit/withdraw: read-modify-write must be atomic,
        # or a concurrent deposit/withdraw could interleave with this and
        # lose an update (the same race condition Section 4 demonstrates).
        with self._lock:
            interest = self._balance * self.interest_rate
            self._balance += interest
            return f"interest amount added={interest}"


class CurrentAccount(BankAccount):
    """An everyday account that may be overdrawn up to an agreed limit."""

    def __init__(self, account_number, initial_balance=0.0, overdraft_limit=0.0):
        super().__init__(account_number, initial_balance)
        self._overdraft_limit = overdraft_limit

    def account_type(self):
        return "Current"

    def _min_balance(self):
        return -self._overdraft_limit

