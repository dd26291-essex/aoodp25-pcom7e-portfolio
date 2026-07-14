"""Race-condition demonstration — the 'before and after' for thread safety.

Shows the same stress test run twice: once without locks (balance drifts)
and once with an RLock (balance stays correct). The two console outputs are
the Phase 3 centrepiece screenshots for the report.

`time.sleep(0)` between the read and the write yields the thread to the
scheduler, making the interleaving visible without needing millions of threads.
"""

import threading
import time
from .account import SavingsAccount


def run_unlocked_demo():
    """Stress test without a lock — threads interleave on the balance, causing drift."""
    start_balance = 10_000
    account = SavingsAccount("S1", start_balance)

    def task():
        for _ in range(1000):
            # Read-yield-write: sleep(0) hands control to the scheduler between
            # reading and writing, exposing the window another thread can slip into.
            b = account._balance; time.sleep(0); account._balance = b + 1
            b = account._balance; time.sleep(0); account._balance = b - 1

    threads = [threading.Thread(target=task) for _ in range(100)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    final = account.get_balance()
    print(f"Start balance : {start_balance}")
    print(f"Final balance : {final}")
    print(f"Drift         : {final - start_balance}  *** RACE CONDITION ***" if final != start_balance
          else "No drift detected (try again — race is non-deterministic)")


def run_locked_demo():
    """Same stress test with an RLock — balance stays correct every time."""
    start_balance = 10_000
    account = SavingsAccount("S2", start_balance)
    lock = threading.RLock()

    def task():
        for _ in range(1000):
            # The lock makes read-yield-write atomic: no other thread can enter
            # this block until the current one releases the lock.
            with lock:
                b = account._balance; time.sleep(0); account._balance = b + 1
            with lock:
                b = account._balance; time.sleep(0); account._balance = b - 1

    threads = [threading.Thread(target=task) for _ in range(100)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    final = account.get_balance()
    print(f"Start balance : {start_balance}")
    print(f"Final balance : {final}")
    print("No drift — RLock prevented the race." if final == start_balance
          else f"Unexpected drift: {final - start_balance}")


def main():
    print("=== WITHOUT LOCK ===")
    run_unlocked_demo()
    print()
    print("=== WITH LOCK (RLock) ===")
    run_locked_demo()


if __name__ == "__main__":
    main()
