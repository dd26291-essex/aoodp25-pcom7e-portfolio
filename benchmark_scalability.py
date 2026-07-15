"""Benchmark: throughput vs thread count under lock contention on a single
shared BankAccount. All threads deposit into the SAME account, so every
operation competes for one RLock - this measures contention, not raw
concurrency, and is the scalability evidence the tutor asked for after
Unit 6 feedback (see FEEDBACK.md: "effect of contention on performance
under very high thread counts").

Run: python benchmark_scalability.py
"""

import time
import threading

from banking.account import SavingsAccount

OPS_PER_THREAD = 5000
THREAD_COUNTS = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512]


def benchmark(n_threads):
    account = SavingsAccount("BENCH", 0.0)

    def task():
        for _ in range(OPS_PER_THREAD):
            account.deposit(1)

    threads = [threading.Thread(target=task) for _ in range(n_threads)]
    start = time.perf_counter()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    elapsed = time.perf_counter() - start

    total_ops = n_threads * OPS_PER_THREAD
    assert account.get_balance() == total_ops, "lost updates under contention"
    return total_ops / elapsed, elapsed


def main():
    print(f"{'threads':>8} {'throughput (ops/s)':>20} {'elapsed (s)':>12}")
    results = []
    for n in THREAD_COUNTS:
        throughput, elapsed = benchmark(n)
        results.append((n, throughput, elapsed))
        print(f"{n:>8} {throughput:>20.1f} {elapsed:>12.4f}")
    return results


if __name__ == "__main__":
    main()
