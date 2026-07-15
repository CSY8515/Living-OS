from __future__ import annotations

from typing import Any

import streamlit as st

from subsystems.compatibility.engines.formatting import format_won
from subsystems.compatibility.engines.storage import FILES, read_json, write_json


def safe_amount(value: Any) -> int:
    try:
        return max(0, int(value or 0))
    except (TypeError, ValueError):
        return 0


def clean_items(items: Any) -> list[dict[str, Any]]:
    if hasattr(items, "to_dict"):
        try:
            items = items.to_dict("records")
        except (TypeError, ValueError):
            items = []
    elif isinstance(items, tuple):
        items = list(items)

    if not isinstance(items, list):
        return []

    cleaned: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name", "") or "").strip()
        amount = safe_amount(item.get("amount", 0))
        if name or amount:
            cleaned.append({"name": name or "이름 없음", "amount": amount})
    return cleaned


def calculate_finance(
    monthly_income: Any,
    fixed_expenses: Any,
    savings_goals: Any,
) -> dict[str, Any]:
    income = safe_amount(monthly_income)
    expenses = clean_items(fixed_expenses)
    goals = clean_items(savings_goals)
    total_fixed = sum(item["amount"] for item in expenses)
    total_savings = sum(item["amount"] for item in goals)
    remaining = income - total_fixed - total_savings

    if income > 0:
        ratio = round(total_fixed / income * 100, 1)
    elif total_fixed > 0:
        ratio = 100.0
    else:
        ratio = 0.0

    if ratio <= 50:
        risk = "NORMAL"
    elif ratio <= 60:
        risk = "WARNING"
    elif ratio <= 70:
        risk = "DANGER"
    else:
        risk = "CRITICAL"

    return {
        "monthly_income": income,
        "fixed_expenses": expenses,
        "savings_goals": goals,
        "summary": {
            "total_fixed_expenses": total_fixed,
            "total_savings_goals": total_savings,
            "remaining_amount": remaining,
            "fixed_expense_ratio": ratio,
            "risk_level": risk,
        },
    }


def load_finance_budget() -> dict[str, Any]:
    raw = read_json(*FILES["finance_budget"])
    if not isinstance(raw, dict):
        raw = {}
    return calculate_finance(
        raw.get("monthly_income", 0),
        raw.get("fixed_expenses", []),
        raw.get("savings_goals", []),
    )


def save_finance_budget(
    monthly_income: Any,
    fixed_expenses: Any,
    savings_goals: Any,
) -> dict[str, Any]:
    budget = calculate_finance(monthly_income, fixed_expenses, savings_goals)
    write_json(FILES["finance_budget"][0], budget)
    return budget


def render_risk(risk: str) -> None:
    if risk == "CRITICAL":
        st.error("위험도: CRITICAL")
    elif risk == "DANGER":
        st.error("위험도: DANGER")
    elif risk == "WARNING":
        st.warning("위험도: WARNING")
    else:
        st.success("위험도: NORMAL")


def render_finance() -> None:
    st.title("Finance")
    st.caption("월 수입, 고정 지출, 저축 목표를 입력하고 예산 상태를 계산합니다.")

    budget = load_finance_budget()

    with st.form("finance_budget_form"):
        monthly_income = st.number_input(
            "월 수입",
            min_value=0,
            value=budget["monthly_income"],
            step=100_000,
            format="%d",
        )

        st.subheader("고정 지출")
        fixed_expenses = st.data_editor(
            budget["fixed_expenses"],
            num_rows="dynamic",
            width="stretch",
            column_config={
                "name": st.column_config.TextColumn("고정 지출 이름"),
                "amount": st.column_config.NumberColumn(
                    "고정 지출 금액",
                    min_value=0,
                    step=10_000,
                    format="%d",
                ),
            },
            key="fixed_expenses_editor",
        )

        st.subheader("저축 목표")
        savings_goals = st.data_editor(
            budget["savings_goals"],
            num_rows="dynamic",
            width="stretch",
            column_config={
                "name": st.column_config.TextColumn("저축 목표 이름"),
                "amount": st.column_config.NumberColumn(
                    "저축 목표 금액",
                    min_value=0,
                    step=10_000,
                    format="%d",
                ),
            },
            key="savings_goals_editor",
        )

        submitted = st.form_submit_button("예산 저장", type="primary")

    if submitted:
        budget = save_finance_budget(
            monthly_income,
            fixed_expenses,
            savings_goals,
        )
        st.success("예산을 저장했습니다.")

    summary = budget["summary"]
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("총 고정 지출", format_won(summary["total_fixed_expenses"]))
    col2.metric("총 저축 목표", format_won(summary["total_savings_goals"]))
    col3.metric("남은 금액", format_won(summary["remaining_amount"]))
    col4.metric("고정지출 비율", f"{summary['fixed_expense_ratio']:.1f}%")
    render_risk(summary["risk_level"])
