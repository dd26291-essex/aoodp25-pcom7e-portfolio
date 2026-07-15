"""Thread-Safe Banking System - AOODP25_PCOM7E Individual Coding Exercise.

Implements BankAccount (ABC), SavingsAccount, CurrentAccount, Bank and
TransactionSimulator with per-account RLock threading and deadlock-safe
transfer via consistent lock ordering.

Run: python banking_system.py
"""

import threading
import random
from abc import ABC, abstractmethod


# ── Exceptions ───────────────────────────────────────────────────────────────

class BankingError(Exception):
    """Base class for every error raised by this banking system."""
    pass


class InvalidAmountError(BankingError):
    """Raised when a deposit or withdrawal amount is not a positive number."""
    pass


class InsufficientFundsError(BankingError):
    """Raised when a withdrawal would exceed the permitted balance floor."""
    def __init__(self, balance, amount):
        self.balance = balance
        self.required = amount
        shortfall = amount - balance
        message = (
            f"Cannot withdraw {amount:.2f} from balance {balance:.2f} "
            f"(short by {shortfall:.2f})"
        )
        super().__init__(message)


class AccountNotFoundError(BankingError):
    """Raised when a lookup or transfer references an unknown account number."""
    pass


# ── Account classes ───────────────────────────────────────────────────────────

class BankAccount(ABC):
    """Abstract base for every account type.

    Subclasses must implement account_type(), and may override _min_balance()
    to change how far the balance is allowed to fall (e.g. to permit overdraft).
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
        holds self._lock - used by Bank.transfer(), which must hold both
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
        # type(self).__name__ prints the actual subclass name — polymorphism in action.
        return f"{type(self).__name__}({self.account_number}, balance={self._balance:.2f})"


class SavingsAccount(BankAccount):
    """An account that earns interest and cannot be overdrawn."""

    def __init__(self, account_number, initial_balance=0.0, interest_rate=0.0):
        super().__init__(account_number, initial_balance)
        self.interest_rate = interest_rate

    def account_type(self):
        return "Savings"

    def add_interest(self):
        """Add one period's interest (balance * rate) to the balance."""
        # Same lock as deposit/withdraw: read-modify-write must be atomic,
        # or a concurrent deposit/withdraw could interleave with this and
        # lose an update (the same race condition demonstrated earlier).
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


# ── Bank ──────────────────────────────────────────────────────────────────────

class Bank:
    """Central registry: opens accounts, looks them up, and transfers money."""

    def __init__(self):
        self._accounts = {}            # account_number -> BankAccount
        self._lock = threading.Lock()  # guards the registry dict itself

    def open_account(self, account):
        """Register a new account. Raises ValueError if number already exists."""
        # Lock the registry so two simultaneous open_account calls can't corrupt the dict.
        with self._lock:
            if account.account_number in self._accounts:
                raise ValueError(f"Account {account.account_number} already exists.")
            self._accounts[account.account_number] = account

    def get_account(self, account_number):
        """Return the account for the given number, or raise AccountNotFoundError."""
        account = self._accounts.get(account_number)
        if account is None:
            raise AccountNotFoundError(f"Account {account_number} not found.")
        return account

    def transfer(self, src_number, dst_number, amount):
        """Move amount from src to dst atomically and without deadlock.

        Acquires both account locks in a consistent order (ascending account_number)
        so two simultaneous reverse transfers cannot deadlock.
        """
        src = self.get_account(src_number)
        dst = self.get_account(dst_number)

        # Canonical lock ordering to break circular wait (Coffman et al., 1971):
        # always acquire the lower account_number first, regardless of transfer
        # direction, so two simultaneous reverse transfers cannot deadlock.
        first, second = sorted([src, dst], key=lambda a: a.account_number)

        with first._lock:
            with second._lock:
                # Both locks held — the debit/credit methods do the
                # affordability check and the arithmetic; Bank never touches
                # _balance directly, preserving BankAccount's encapsulation
                # even though the atomicity requires locking from outside it.
                src._apply_debit(amount)
                dst._apply_credit(amount)


# ── TransactionSimulator ──────────────────────────────────────────────────────

class TransactionSimulator:
    """Simulates N concurrent users making random transfers on a set of accounts."""

    def __init__(self, bank, accounts, n_users=10, ops_per_user=20, max_amount=100):
        self._bank = bank
        self._accounts = accounts
        self._n_users = n_users
        self._ops_per_user = ops_per_user
        self._max_amount = max_amount

    def _user_task(self):
        """One user's session — random transfers between accounts."""
        for _ in range(self._ops_per_user):
            src, dst = random.sample(self._accounts, 2)
            amount = random.randint(1, self._max_amount)
            try:
                self._bank.transfer(src.account_number, dst.account_number, amount)
            except InsufficientFundsError:
                pass   # src couldn't cover it — skip, all balances unchanged

    def run(self):
        """Spawn all user threads, wait for completion, return a result summary."""
        start_total = sum(a.get_balance() for a in self._accounts)
        threads = [threading.Thread(target=self._user_task) for _ in range(self._n_users)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        end_total = sum(a.get_balance() for a in self._accounts)
        return {
            "start_total": start_total,
            "end_total":   end_total,
            "conserved":   end_total == start_total,
        }


# ── Demo ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 55)
    print("  Thread-Safe Banking System — Demo")
    print("=" * 55)

    bank = Bank()

    savings = SavingsAccount("S001", initial_balance=1000.0, interest_rate=0.05)
    current = CurrentAccount("C001", initial_balance=500.0,  overdraft_limit=200.0)
    bank.open_account(savings)
    bank.open_account(current)

    print(f"\nOpened: {savings}")
    print(f"Opened: {current}")

    # Deposit
    savings.deposit(200)
    print(f"\nAfter deposit £200 -> {savings}")

    # Withdraw
    savings.withdraw(100)
    print(f"After withdraw £100 -> {savings}")

    # Interest
    savings.add_interest()
    print(f"After 5% interest  -> {savings}")

    # Overdraft
    current.withdraw(650)
    print(f"\nOverdraft withdraw £650 -> {current}")

    # Overdraft breach
    print("\nAttempting to breach overdraft limit...")
    try:
        current.withdraw(200)
    except InsufficientFundsError as e:
        print(f"  Caught: {e}")

    # Transfer
    bank.transfer("S001", "C001", 300)
    print(f"\nAfter transfer £300 S001->C001:")
    print(f"  {savings}")
    print(f"  {current}")

    # Concurrency stress test
    print("\nRunning concurrency stress test (10 users, 50 ops each)...")
    a1 = SavingsAccount("T001", 500)
    a2 = SavingsAccount("T002", 500)
    stress_bank = Bank()
    stress_bank.open_account(a1)
    stress_bank.open_account(a2)

    sim = TransactionSimulator(stress_bank, [a1, a2], n_users=10, ops_per_user=50)
    result = sim.run()
    print(f"  Start total: £{result['start_total']:.2f}")
    print(f"  End total:   £{result['end_total']:.2f}")
    print(f"  Conserved:   {result['conserved']}")

    print("\nDemo complete.")


if __name__ == "__main__":
    main()
