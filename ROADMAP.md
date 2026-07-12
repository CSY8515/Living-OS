# Living OS Roadmap

## v0.8 Core Reliability and Consistency

Status: Implemented; awaiting approval

Goals:

- Correct dashboard and version-label inconsistencies.
- Consolidate read-only date handling for Analytics and Review.
- Improve safe report discovery and preserve malformed-data fallbacks.
- Add isolated regression tests without changing JSON/JSONL schemas.

Approved scope: `docs/ROADMAP_v0.8.md`

## v0.7 Review Workspace

상태: 구현 완료

목표:

- 기존 Living OS 기록을 통합해서 검토하는 읽기 전용 Review Workspace 추가
- `draft`, `active`, `review` 상태의 Decision 검토 큐 제공
- 기간 및 상태 필터 제공
- 기존 JSON/JSONL 스키마와 v0.6 기능의 완전한 호환성 유지

상세 승인 범위: `docs/ROADMAP_v0.7.md`

## v0.6 Analytics

상태: 완료

목표:

- 기존 기록을 기반으로 하는 읽기 전용 Analytics 추가
- Daily Log, Decision, Archive, Report 요약 제공

---

## v0.1 MVP

상태: 완료

목표:

- Streamlit 기반 MVP 생성
- Dashboard, Finance, Housing, Decision Log 구현
- Dummy Data Generator 구현
- Report System 구현
- JSON / JSONL 저장 구조 검증

## v0.2 Core

상태: 구현 중

목표:

- 실제 매일 사용할 수 있는 Core OS 완성
- Daily Log 중심 운영 구조 도입
- Decision Log 단순화
- Report System을 일일/주간/월간 보고서로 정리
- Archive 검색/조회 구조 추가
- Module Manager 구조 추가
- Settings, Backup, Restore 추가
- Dummy/Test 기능 제거

핵심 기능:

- Dashboard
- Daily Log
- Decision Log
- Reports
- Archive
- Module Manager
- Settings

## v0.3 Module Foundation

상태: 예정

목표:

- Module Manager를 기반으로 실제 모듈 추가 준비
- 각 모듈의 데이터 경계 정의
- Core와 Module 간 연결 규칙 정의

후보 모듈:

- Vehicle OS
- Food OS
- Finance OS
- Health OS
- Housing OS
- Learning OS

## v0.4 Finance / Housing Migration

상태: 예정

목표:

- v0.1에서 구현된 Finance / Housing 기능을 v0.2 Core 구조에 맞게 정식 모듈로 승격
- Core와 확장 모듈의 역할 분리

## v0.5 Data Reliability

상태: 예정

목표:

- 백업/복원 개선
- 데이터 검증
- JSON 스키마 정리
- 향후 SQLite 전환 가능성 검토

## 이후 버전 후보

이번 버전에서는 제외하지만 이후 검토할 기능:

- AI Recommendation
- AI Decision Engine
- Automation
- Habit
- Routine
- Notification
- Expansion Pack
- Streamlit Cloud 배포
- GitHub Release 자동화
