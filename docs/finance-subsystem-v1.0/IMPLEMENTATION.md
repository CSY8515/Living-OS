# Finance Subsystem v1.0 Implemented Engines and Functions

## Ledger Engine

record_income, record_expense, list_transactions, monthly totals, and expense grouping.

## Budget Engine

create_budget, internal migration upsert, list_budgets, budget_usage, and remaining_budget.

## Cash Flow Engine

monthly_cash_flow with monthly income, expense, and net cash flow.

## Savings Engine

create_installment_savings, create_term_deposit, record_savings_contribution, list_savings, savings_goal_progress, and calculate_maturity. Interest projection uses stored basis points and day-count simple interest.

## Report Engine

summary_report, render_financial_status, and idempotent immutable monthly_close.

## Supporting Engines

Storage provides lazy creation, transactions, integrity health, schema metadata, and export snapshots. Migration provides explicit transactional adoption of the legacy Finance JSON. Validation centralizes boundary rules.

## Living OS integration

Finance is registered as enabled module finance version 1.0.0, compatible with Living OS >=1.2,<2.0. The Experience subsystem imports only FinanceSubsystem and exposes the Finance page in canonical and compatibility modes.
