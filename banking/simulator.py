"""TransactionSimulator — spawns concurrent users to stress-test the bank.

Each simulated user runs in its own thread, performing random deposits and
withdrawals on randomly chosen accounts. After all threads finish, the total
balance across all accounts must equal the starting total — proving the
thread-safe implementation loses no money under concurrency.
"""

import threading
import random

from .exceptions import InsufficientFundsError


class TransactionSimulator:
    """Simulates N concurrent users making random transactions on a set of accounts."""

    def __init__(self, bank, accounts, n_users=10, ops_per_user=20, max_amount=100):
        """
        bank:         Bank instance used to execute transfers.
        accounts:     list of BankAccount subclass instances to transact on.
        n_users:      number of concurrent user threads to spawn.
        ops_per_user: number of transfer operations each user performs.
        max_amount:   upper bound for random transfer amounts.
        """
        self._bank = bank
        self._accounts = accounts
        self._n_users = n_users
        self._ops_per_user = ops_per_user
        self._max_amount = max_amount

    def _user_task(self):
        """One user's session — random transfers between accounts.

        Transfers preserve total money by definition, so any drift in the
        final total is a genuine concurrency bug.
        """
        for _ in range(self._ops_per_user):
            src, dst = random.sample(self._accounts, 2)   # pick two distinct accounts
            amount = random.randint(1, self._max_amount)
            try:
                self._bank.transfer(src.account_number, dst.account_number, amount)
            except InsufficientFundsError:
                pass   # src couldn't cover it — skip, all balances unchanged

    def run(self):
        """Spawn all user threads, wait for them to finish, return a result summary."""
        start_total = sum(a.get_balance() for a in self._accounts)

        threads = [threading.Thread(target=self._user_task) for _ in range(self._n_users)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        end_total = sum(a.get_balance() for a in self._accounts)
        return {
            "start_total": start_total,
            "end_total": end_total,
            "conserved": end_total == start_total
        }
