"""Unit tests for BankAccount, SavingsAccount, and CurrentAccount.

Each test follows the Arrange-Act-Assert pattern: set up an account (setUp),
call one method (act), check one outcome (assert). Run with:
    python -m unittest discover -s tests

Reference: Python unittest docs — https://docs.python.org/3/library/unittest.html
"""

import unittest

from banking.account import SavingsAccount, CurrentAccount
from banking.exceptions import InvalidAmountError, InsufficientFundsError


class TestDeposit(unittest.TestCase):

    def setUp(self):
        """Create a fresh account before each test so tests don't interfere."""
        self.account = SavingsAccount("S1", 100)

    def test_deposit_increases_balance(self):
        """Scenario 1 — deposit adds the correct amount."""
        self.account.deposit(50)
        self.assertEqual(self.account.get_balance(), 150)

    def test_deposit_zero_raises(self):
        """Scenario 5a — zero deposit is rejected."""
        self.assertRaises(InvalidAmountError, self.account.deposit, 0)

    def test_deposit_negative_raises(self):
        """Scenario 4 — negative deposit is rejected."""
        self.assertRaises(InvalidAmountError, self.account.deposit, -10)


class TestWithdraw(unittest.TestCase):

    def setUp(self):
        self.account = SavingsAccount("S2", 100)

    def test_withdraw_deducts_balance(self):
        """Scenario 2 — withdraw deducts the correct amount."""
        self.account.withdraw(40)
        self.assertEqual(self.account.get_balance(), 60)

    def test_withdraw_beyond_balance_raises(self):
        """Scenario 3 — withdraw beyond balance raises InsufficientFundsError."""
        self.assertRaises(InsufficientFundsError, self.account.withdraw, 200)

    def test_withdraw_zero_raises(self):
        """Scenario 5b — zero withdrawal is rejected."""
        self.assertRaises(InvalidAmountError, self.account.withdraw, 0)

    def test_withdraw_leaves_balance_unchanged_on_rejection(self):
        """Scenario 3b — balance must not change when a withdrawal is rejected."""
        try:
            self.account.withdraw(200)
        except InsufficientFundsError:
            pass
        # Balance must still be 100 — the failed withdraw must not mutate it.
        self.assertEqual(self.account.get_balance(), 100)


class TestOverdraft(unittest.TestCase):

    def setUp(self):
        self.account = CurrentAccount("C1", 100, overdraft_limit=50)

    def test_overdraft_within_limit_allowed(self):
        """Scenario 6 — withdraw that takes balance negative within limit succeeds."""
        self.account.withdraw(130)
        self.assertEqual(self.account.get_balance(), -30)

    def test_overdraft_beyond_limit_raises(self):
        """Scenario 7 — withdraw beyond overdraft limit is rejected."""
        self.assertRaises(InsufficientFundsError, self.account.withdraw, 160)


class TestInterest(unittest.TestCase):

    def test_interest_added_correctly(self):
        """Scenario 8 — add_interest applies the rate to the current balance."""
        account = SavingsAccount("S3", 1000, interest_rate=0.05)
        account.add_interest()
        self.assertEqual(account.get_balance(), 1050)


if __name__ == "__main__":
    unittest.main()
