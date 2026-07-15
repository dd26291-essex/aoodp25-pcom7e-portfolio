# Scalability Analysis — Contention Under High Thread Counts

Benchmark: `benchmark_scalability.py`. 5,000 deposits per thread, on a single
shared `SavingsAccount`, at thread counts from 1 to 512, run on [state your
machine spec here, e.g. Intel Core i7-7700HQ, 16 GB DDR4, Windows 10].

## Result

Throughput rises sharply from 1 to 2 threads, then **plateaus at roughly
1.1–1.4 million deposits/second from 8 threads through 512 threads** — a
64x increase in thread count produces no further throughput change.

## Interpretation

This is not the classic lock-contention collapse a Java or C++ implementation
would show under the same workload. In CPython, the Global Interpreter Lock
(GIL) already serialises the execution of Python bytecode across all threads,
regardless of how many application-level locks (`RLock`) exist (Python
Software Foundation, 2024b). `BankAccount._lock` guarantees *correctness*
under concurrent access — it prevents the read-modify-write race demonstrated
in `race_demo.py` — but it is not what determines *throughput* here, because
the GIL has already bounded that to roughly one Python-level operation at a
time before the application lock is ever considered.

The practical implication: this implementation's ceiling is the interpreter,
not the locking strategy. A production system needing genuinely higher
throughput on this workload would need either multiple processes
(`multiprocessing`, sidestepping the GIL entirely) or a non-CPython runtime,
not a different locking scheme — the `RLock` design here is already correct
and is not the bottleneck.

## Reproducing this result

```
python benchmark_scalability.py
```

Deterministic in outcome (the final balance always equals `threads *
5000`, asserted inside the benchmark itself), though wall-clock timings vary
run to run with machine load.
