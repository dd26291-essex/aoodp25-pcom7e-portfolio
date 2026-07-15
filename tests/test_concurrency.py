"""Concurrency and integration tests — prove thread safety under stress.

These tests are the make-or-break evidence: final balances must be correct
under heavy concurrency, and bidirectional transfers must never deadlock. Run:
    python -m unittest discover -s tests

Reference: Python threading docs — https://docs.python.org/3/library/threading.html
Test structure assisted by Claude (Anthropic) and reviewed/understood by the author.
"""

import unittest
import threading

from banking.account import SavingsAccount, CurrentAccount
from banking.bank import Bank
from banking.simulator import TransactionSimulator
from banking.exceptions import InsufficientFundsError, AccountNotFoundError


class TestThreadSafety(unittest.TestCase):

    def test_concurrent_deposits_correct(self):
        """Scenario 9a — 100 threads each deposit 10 times: final balance must be exact."""
        account = SavingsAccount("S1", 0)

        def task():
            for _ in range(10):
                account.deposit(10)

        threads = [threading.Thread(target=task) for _ in range(100)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # 100 threads × 10 ops × £10 = £10,000 exactly — any deviation is a race.
        self.assertEqual(account.get_balance(), 10_000)

    def test_concurrent_deposits_withdrawals_conserved(self):
        """Scenario 9b — equal paired deposits and withdrawals: balance unchanged."""
        account = SavingsAccount("S2", 1000)

        def task():
            for _ in range(50):
                account.deposit(10)
                try:
                    account.withdraw(10)
                except InsufficientFundsError:
                    pass

        threads = [threading.Thread(target=task) for _ in range(50)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(account.get_balance(), 1000)

    def test_concurrent_interest_compounds_correctly(self):
        """Scenario 11 — 50 threads each call add_interest() once: the
        result must match compounding applied strictly one at a time.
        Proves the lock added to add_interest() prevents the same
        read-modify-write race that Scenario 9a guards against in deposit()."""
        account = SavingsAccount("S3", 10000.0, interest_rate=0.01)

        def task():
            account.add_interest()

        threads = [threading.Thread(target=task) for _ in range(50)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        expected = 10000.0 * (1.01 ** 50)
        self.assertAlmostEqual(account.get_balance(), expected, places=6)


class TestTransfer(unittest.TestCase):

    def setUp(self):
        self.bank = Bank()
        self.a1 = SavingsAccount("A1", 1000)
        self.a2 = SavingsAccount("A2", 1000)
        self.bank.open_account(self.a1)
        self.bank.open_account(self.a2)

    def test_bidirectional_transfer_no_deadlock(self):
        """Scenario 10 — 200 threads transfer both directions: total conserved, no deadlock."""
        def a_to_b():
            try:
                self.bank.transfer("A1", "A2", 10)
            except InsufficientFundsError:
                pass

        def b_to_a():
            try:
                self.bank.transfer("A2", "A1", 10)
            except InsufficientFundsError:
                pass

        threads = (
            [threading.Thread(target=a_to_b) for _ in range(100)] +
            [threading.Thread(target=b_to_a) for _ in range(100)]
        )
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        total = self.a1.get_balance() + self.a2.get_balance()
        self.assertEqual(total, 2000)

    def test_transfer_raises_on_unknown_account(self):
        """Scenario 3c — transfer from an unknown account raises AccountNotFoundError."""
        self.assertRaises(
            AccountNotFoundError,
            self.bank.transfer, "UNKNOWN", "A1", 10
        )


class TestSimulator(unittest.TestCase):

    def test_simulator_conserves_money(self):
        """Scenario 9c — TransactionSimulator: total money unchanged after full run."""
        bank = Bank()
        a1 = SavingsAccount("A1", 500)
        a2 = SavingsAccount("A2", 500)
        bank.open_account(a1)
        bank.open_account(a2)

        sim = TransactionSimulator(bank, [a1, a2], n_users=30, ops_per_user=50, max_amount=20)
        result = sim.run()

        self.assertEqual(result["start_total"], 1000)
        self.assertTrue(result["conserved"])


if __name__ == "__main__":
    unittest.main()
