# AOODP25_PCOM7E — End of Module Assignment Portfolio

Advanced Object-Oriented Design and Programming, University of Essex Online.
Coding artefacts referenced from the e-Portfolio: a thread-safe banking system (Unit 6) and an
AI-assisted credit-decisioning capstone (`creditguard/`) demonstrating Strategy, Decorator, Visitor,
Abstract Factory, a Model Registry, and a Feature Store.

> This repository is anonymised for marking purposes. No author name appears in code, commits, or
> repository metadata.

## Contents

```
banking/            Unit 6 thread-safe banking system (modular package)
banking_system.py   The single-file combined build, as submitted for Unit 6
tests/               unittest suite for the banking system (15 tests)
creditguard/         Capstone: AI-assisted credit/fraud decisioning service (in progress)
diagrams/            UML class + sequence diagrams, scalability chart
```

## Unit 6 — Thread-safe banking system

`BankAccount` (abstract) with `SavingsAccount` and `CurrentAccount` subclasses. Each account guards its
balance with a `threading.RLock`. `Bank.transfer()` prevents deadlock via canonical lock ordering
(accounts locked in a consistent order regardless of transfer direction). `TransactionSimulator` spawns
concurrent user threads and asserts that total money is conserved throughout.

**Run the tests:**

```
python -m unittest discover -s tests -v
```

**Expected output:** 15 tests, all passing, in under 0.1 seconds:

```
Ran 15 tests in 0.062s

OK
```

**Run the console demo:**

```
python banking_system.py
```

## creditguard — AI-assisted credit decisioning capstone

Extends the banking system into a credit/fraud decisioning service, built to demonstrate design patterns
required for the module's End of Module Assignment:

| Pattern | File | Purpose |
|---|---|---|
| Strategy | `creditguard/strategy.py` | Interchangeable risk-scoring algorithms (rule-based vs AI-model-backed), swappable at runtime |
| Abstract Factory | `creditguard/providers.py` | Swaps a whole family of AI-provider objects (client, embedder, tokeniser) coherently |
| Decorator | `creditguard/decorators.py` | Logging, audit, and rate-limiting layered onto any risk scorer without subclassing |
| Visitor | `creditguard/visitor.py` | Separates portfolio analytics/reporting from account structure |
| Model Registry | `creditguard/registry.py` | Model lifecycle and versioning; invariant — exactly one model in production |
| Feature Store | `creditguard/features.py` | One feature definition shared by training and serving |

**Run the tests** (once implemented):

```
python -m unittest discover -s tests -v
```

`tests/test_ai_mocking.py` exercises the AI-backed strategy with `unittest.mock` — no live API calls,
no network access, no API key required.

## Requirements

Python 3.13, standard library only (`threading`, `unittest`, `unittest.mock`, `abc`, `dataclasses`). No
third-party dependencies.
