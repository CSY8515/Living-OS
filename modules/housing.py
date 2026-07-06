from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

import streamlit as st

from modules.storage import FILES, read_json, write_json


def safe_non_negative_int(value: Any) -> int:
    try:
        return max(0, int(value or 0))
    except (TypeError, ValueError):
        return 0


def monthly_cost_deduction(total_monthly_cost: int) -> int:
    if total_monthly_cost <= 500_000:
        return 0
    if total_monthly_cost <= 700_000:
        return 5
    if total_monthly_cost <= 900_000:
        return 10
    if total_monthly_cost <= 1_100_000:
        return 15
    return min(30, 20 + ((total_monthly_cost - 1_100_000) // 200_000) * 5)


def commute_deduction(commute_minutes: int) -> int:
    if commute_minutes <= 20:
        return 0
    if commute_minutes <= 40:
        return 5
    if commute_minutes <= 60:
        return 10
    return 20


def housing_grade(score: int) -> str:
    if score >= 90:
        return "A"
    if score >= 75:
        return "B"
    if score >= 60:
        return "C"
    return "D"


def calculate_housing_candidate(
    name: Any,
    deposit: Any,
    monthly_rent: Any,
    maintenance_fee: Any,
    maintenance_fee_provided: bool,
    commute_minutes: Any,
    parking_available: bool,
    options_memo: Any,
    special_notes: Any,
) -> dict[str, Any]:
    clean_name = str(name or "").strip() or "이름 없는 매물"
    clean_deposit = safe_non_negative_int(deposit)
    clean_rent = safe_non_negative_int(monthly_rent)
    clean_maintenance = (
        safe_non_negative_int(maintenance_fee) if maintenance_fee_provided else 0
    )
    clean_commute = safe_non_negative_int(commute_minutes)
    total_monthly_cost = clean_rent + clean_maintenance

    deductions = {
        "monthly_cost": monthly_cost_deduction(total_monthly_cost),
        "commute": commute_deduction(clean_commute),
        "parking": 0 if parking_available else 10,
        "missing_maintenance_fee": 0 if maintenance_fee_provided else 5,
    }
    score = max(0, 100 - sum(deductions.values()))

    return {
        "name": clean_name,
        "deposit": clean_deposit,
        "monthly_rent": clean_rent,
        "maintenance_fee": clean_maintenance,
        "maintenance_fee_provided": bool(maintenance_fee_provided),
        "total_monthly_cost": total_monthly_cost,
        "commute_minutes": clean_commute,
        "parking_available": bool(parking_available),
        "options_memo": str(options_memo or "").strip(),
        "special_notes": str(special_notes or "").strip(),
        "score": score,
        "grade": housing_grade(score),
        "deductions": deductions,
    }


def normalize_candidate(raw: Any) -> dict[str, Any] | None:
    if not isinstance(raw, dict):
        return None

    candidate = calculate_housing_candidate(
        raw.get("name", ""),
        raw.get("deposit", 0),
        raw.get("monthly_rent", 0),
        raw.get("maintenance_fee", 0),
        bool(raw.get("maintenance_fee_provided", True)),
        raw.get("commute_minutes", 0),
        bool(raw.get("parking_available", False)),
        raw.get("options_memo", ""),
        raw.get("special_notes", ""),
    )
    candidate["id"] = str(raw.get("id") or uuid4())
    candidate["created_at"] = str(raw.get("created_at") or "")
    return candidate


def load_housing_candidates() -> list[dict[str, Any]]:
    raw = read_json(*FILES["housing_candidates"])
    if not isinstance(raw, dict):
        return []

    candidates = raw.get("candidates", [])
    if not isinstance(candidates, list):
        return []

    normalized = [normalize_candidate(candidate) for candidate in candidates]
    return [candidate for candidate in normalized if candidate is not None]


def save_housing_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    record = {
        "id": str(uuid4()),
        **candidate,
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
    }
    candidates = load_housing_candidates()
    candidates.append(record)
    write_json(FILES["housing_candidates"][0], {"candidates": candidates})
    return record


def get_housing_summary() -> dict[str, Any]:
    candidates = load_housing_candidates()
    if not candidates:
        return {
            "candidate_count": 0,
            "best_candidate": None,
            "average_score": 0.0,
        }

    best = max(candidates, key=lambda candidate: candidate["score"])
    average = round(
        sum(candidate["score"] for candidate in candidates) / len(candidates),
        1,
    )
    return {
        "candidate_count": len(candidates),
        "best_candidate": {
            "name": best["name"],
            "score": best["score"],
            "grade": best["grade"],
        },
        "average_score": average,
    }


def render_housing() -> None:
    st.title("Housing")
    st.caption("원룸 후보를 입력하면 월 부담과 출퇴근 조건을 기준으로 점수를 계산합니다.")

    with st.form("housing_candidate_form", clear_on_submit=True):
        name = st.text_input("매물명")

        cost_col1, cost_col2, cost_col3 = st.columns(3)
        deposit = cost_col1.number_input(
            "보증금", min_value=0, step=1_000_000, format="%d"
        )
        monthly_rent = cost_col2.number_input(
            "월세", min_value=0, step=10_000, format="%d"
        )
        maintenance_fee = cost_col3.number_input(
            "관리비", min_value=0, step=10_000, format="%d"
        )
        maintenance_fee_missing = st.checkbox("관리비 미기재")

        condition_col1, condition_col2 = st.columns(2)
        commute_minutes = condition_col1.number_input(
            "도보 출퇴근 시간(분)",
            min_value=0,
            step=5,
            format="%d",
        )
        parking_label = condition_col2.radio(
            "주차 가능 여부",
            ["예", "아니오"],
            horizontal=True,
        )

        options_memo = st.text_area("옵션 메모")
        special_notes = st.text_area("특이사항 메모")
        submitted = st.form_submit_button("원룸 후보 저장", type="primary")

    if submitted:
        if not name.strip():
            st.error("매물명을 입력해주세요.")
        else:
            candidate = calculate_housing_candidate(
                name,
                deposit,
                monthly_rent,
                maintenance_fee,
                not maintenance_fee_missing,
                commute_minutes,
                parking_label == "예",
                options_memo,
                special_notes,
            )
            saved = save_housing_candidate(candidate)
            st.success(
                f"{saved['name']}을(를) {saved['score']}점, "
                f"{saved['grade']}등급으로 저장했습니다."
            )

    candidates = load_housing_candidates()
    st.subheader(f"등록된 원룸 후보 {len(candidates)}개")
    if not candidates:
        st.info("등록된 원룸 후보가 없습니다.")
        return

    table_rows = [
        {
            "이름": candidate["name"],
            "총 월 부담금": candidate["total_monthly_cost"],
            "출퇴근 시간(분)": candidate["commute_minutes"],
            "주차": "예" if candidate["parking_available"] else "아니오",
            "점수": candidate["score"],
            "등급": candidate["grade"],
        }
        for candidate in candidates
    ]
    st.dataframe(
        table_rows,
        width="stretch",
        hide_index=True,
        column_config={
            "총 월 부담금": st.column_config.NumberColumn(format="%d원"),
        },
    )

    special_candidates = [
        candidate for candidate in candidates if candidate["special_notes"]
    ]
    if special_candidates:
        st.subheader("특이사항")
        for candidate in special_candidates:
            st.warning(f"{candidate['name']}: {candidate['special_notes']}")
