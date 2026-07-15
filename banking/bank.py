"""Bank — registry of accounts and customers, plus deadlock-safe money transfer.

Single-responsibility (SOLID): an Account manages its own balance; the Bank
knows the SET of accounts and is the only place that transfers money between
them, because a transfer must coordinate two accounts atomically.
"""

import threading

from .exceptions import AccountNotFoundError


class Bank:
    """Central registry: opens accounts, looks them up, and transfers money."""

    def __init__(self):
        self._accounts = {}          # account_number -> Account
        self._lock = threading.Lock()  # guards the registry dict itself

    def open_account(self, account):
        """Register a new account in the bank.

        account: any BankAccount subclass instance (SavingsAccount, CurrentAccount).
        Raises ValueError if the account number is already registered.
        """
        # Lock the registry so two simultaneous open_account calls can't corrupt the dict.
        with self._lock:
            if account.account_number in self._accounts:
                raise ValueError(f"Account {account.account_number} already exists.")
            self._accounts[account.account_number] = account

    def get_account(self, account_number):
        """Return the account for the given number.
        Raises:
            AccountNotFoundError: if no account with that number exists.
        """
        account = self._accounts.get(account_number)
        if account is None:
            raise AccountNotFoundError(f"Account {account_number} not found.")
        return account

    def transfer(self, src_number, dst_number, amount):
        """Move amount from src to dst atomically and without deadlock.

        Acquires both account locks in a consistent order (ascending account_number
        as a string) so two simultaneous reverse transfers cannot deadlock.

        Raises:
            AccountNotFoundError: if either account number is unknown.
            InsufficientFundsError: if src cannot cover the amount.
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