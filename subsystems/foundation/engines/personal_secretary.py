from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol, Sequence
from uuid import uuid4

from subsystems.foundation.engines.time import utc_now_iso


PRIORITY_RANK = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}


@dataclass(frozen=True)
class OperationalReportEnvelope:
    """Read-only handoff contract from an operational producer."""

    report_id: str
    source: str
    generated_at: str
    priority: str
    summary: Mapping[str, Any]
    findings: tuple[Mapping[str, Any], ...] = field(default_factory=tuple)
    recommendations: tuple[str, ...] = field(default_factory=tuple)
    rule_candidates: tuple[Mapping[str, Any], ...] = field(default_factory=tuple)
    standard_candidates: tuple[Mapping[str, Any], ...] = field(default_factory=tuple)

    def validate(self) -> None:
        if not self.report_id.strip() or not self.source.strip():
            raise ValueError("Operational report identity is required.")
        if not self.generated_at.strip():
            raise ValueError("Operational report generated_at is required.")
        if self.priority not in PRIORITY_RANK:
            raise ValueError("Unknown operational report priority.")
        if not isinstance(self.summary, Mapping):
            raise ValueError("Operational report summary must be an object.")

    def to_payload(self) -> dict[str, Any]:
        self.validate()
        return {
            "report_id": self.report_id,
            "source": self.source,
            "generated_at": self.generated_at,
            "priority": self.priority,
            "summary": dict(self.summary),
            "findings": [dict(item) for item in self.findings],
            "recommendations": list(self.recommendations),
            "rule_candidates": [dict(item) for item in self.rule_candidates],
            "standard_candidates": [dict(item) for item in self.standard_candidates],
            "contract_version": 1,
        }


@dataclass(frozen=True)
class PersonalSecretaryBrief:
    briefing_id: str
    generated_at: str
    priority: str
    source_reports: tuple[str, ...]
    summary: Mapping[str, Any]
    recommendations: tuple[str, ...]
    user_report: str

    def to_payload(self) -> dict[str, Any]:
        return {
            "briefing_id": self.briefing_id,
            "generated_at": self.generated_at,
            "priority": self.priority,
            "source_reports": list(self.source_reports),
            "summary": dict(self.summary),
            "recommendations": list(self.recommendations),
            "user_report": self.user_report,
            "contract_version": 1,
        }


class PersonalSecretaryContract(Protocol):
    """Capability boundary used by Living OS operational producers."""

    def aggregate_operational_reports(
        self, reports: Sequence[OperationalReportEnvelope]
    ) -> PersonalSecretaryBrief: ...


class PersonalSecretaryAggregator:
    """Deterministic contract implementation: aggregate, prioritize, recommend."""

    capability_id = "CAP-PERSONAL-SECRETARY"

    def aggregate_operational_reports(
        self, reports: Sequence[OperationalReportEnvelope]
    ) -> PersonalSecretaryBrief:
        selected = tuple(reports)
        if not selected:
            raise ValueError("At least one operational report is required.")
        for report in selected:
            report.validate()
        priority = max(selected, key=lambda item: PRIORITY_RANK[item.priority]).priority
        recommendations = tuple(
            dict.fromkeys(
                recommendation
                for report in selected
                for recommendation in report.recommendations
                if recommendation.strip()
            )
        )
        total_records = sum(
            int(report.summary.get("records_total", 0)) for report in selected
        )
        unresolved_issues = sum(
            int(report.summary.get("unresolved_issues", 0)) for report in selected
        )
        rule_candidates = sum(len(report.rule_candidates) for report in selected)
        standard_candidates = sum(len(report.standard_candidates) for report in selected)
        summary = {
            "report_count": len(selected),
            "records_total": total_records,
            "unresolved_issues": unresolved_issues,
            "rule_candidates": rule_candidates,
            "standard_candidates": standard_candidates,
        }
        user_report = (
            f"운영 우선순위 {priority}. "
            f"운영 보고 {len(selected)}건, 미해결 이슈 {unresolved_issues}건을 확인했습니다. "
            f"권장 조치 {len(recommendations)}건을 검토해 주세요."
        )
        return PersonalSecretaryBrief(
            briefing_id=f"PSB-{uuid4()}",
            generated_at=utc_now_iso(),
            priority=priority,
            source_reports=tuple(report.report_id for report in selected),
            summary=summary,
            recommendations=recommendations,
            user_report=user_report,
        )
