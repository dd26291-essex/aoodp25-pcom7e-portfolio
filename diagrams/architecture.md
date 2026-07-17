# Architecture Diagrams

## 1. Unit 6: Banking system class diagram

```mermaid
classDiagram
    class BankAccount {
        <<abstract>>
        +account_number
        -_balance
        -_lock
        +deposit(amount)
        +withdraw(amount)
        +get_balance() float
        #_apply_debit(amount)
        #_apply_credit(amount)
        #_min_balance() float
        +account_type()* str
    }
    class SavingsAccount {
        +interest_rate
        +account_type() str
        +add_interest()
    }
    class CurrentAccount {
        -_overdraft_limit
        +account_type() str
        #_min_balance() float
    }
    class Bank {
        -_accounts dict
        -_lock
        +open_account(account)
        +get_account(number) BankAccount
        +transfer(src, dst, amount)
    }
    class TransactionSimulator {
        -_bank
        -_accounts
        +run() dict
    }

    BankAccount <|-- SavingsAccount
    BankAccount <|-- CurrentAccount
    Bank "1" o-- "*" BankAccount : registry
    TransactionSimulator ..> Bank : drives
```

## 2. Unit 6: `Bank.transfer()` lock-acquisition sequence

Shows the deadlock-prevention mechanism: both locks are always acquired in
the same order (lower `account_number` first), regardless of transfer
direction, which is what makes two simultaneous reverse transfers safe.

```mermaid
sequenceDiagram
    participant T as Thread
    participant B as Bank
    participant First as first account<br/>(lower account_number)
    participant Second as second account<br/>(higher account_number)

    T->>B: transfer(src, dst, amount)
    B->>B: sort src, dst by account_number
    B->>First: acquire lock
    activate First
    B->>Second: acquire lock
    activate Second
    B->>First: _apply_debit(amount)
    B->>Second: _apply_credit(amount)
    B->>Second: release lock
    deactivate Second
    B->>First: release lock
    deactivate First
    B-->>T: transfer complete
```

## 3. creditguard: Pattern relationships

```mermaid
classDiagram
    class RiskStrategy {
        <<abstract>>
        +score(application)* RiskScore
        +accept(visitor)* 
    }
    class RuleBasedRisk
    class MLModelRisk {
        -_factory
    }
    class ChallengerRisk {
        -_champion
        -_challenger
    }
    class RiskStrategyDecorator {
        <<abstract>>
        -_wrapped
    }
    class LoggingDecorator
    class AuditDecorator
    class RateLimitDecorator
    class AIProviderFactory {
        <<abstract>>
        +create_client()* AIClient
        +create_prompt_builder()* PromptBuilder
    }
    class LocalStubFactory
    class AnthropicFactory
    class StrategyVisitor {
        <<abstract>>
        +visit_rule_based(s)*
        +visit_ml_model(s)*
        +visit_challenger(s)*
    }
    class ExplainabilityReportVisitor

    RiskStrategy <|-- RuleBasedRisk
    RiskStrategy <|-- MLModelRisk
    RiskStrategy <|-- ChallengerRisk
    RiskStrategy <|-- RiskStrategyDecorator
    RiskStrategyDecorator <|-- LoggingDecorator
    RiskStrategyDecorator <|-- AuditDecorator
    RiskStrategyDecorator <|-- RateLimitDecorator
    RiskStrategyDecorator o-- RiskStrategy : wraps
    ChallengerRisk o-- RiskStrategy : champion/challenger
    MLModelRisk o-- AIProviderFactory : uses
    AIProviderFactory <|-- LocalStubFactory
    AIProviderFactory <|-- AnthropicFactory
    StrategyVisitor <|-- ExplainabilityReportVisitor
    RiskStrategy ..> StrategyVisitor : accept(visitor)
```
