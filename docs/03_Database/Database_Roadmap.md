# Living OS v1.7 Database Foundation Roadmap

## Purpose

본 문서는 Database Foundation의 구현 준비 순서와 완료 Gate를 정의한다. 기능 목록이 아니라 의존성, 위험과 검증 순서에 따른 Roadmap이다.

## Scope

v1.7에서 완료할 범위:

- Database Subsystem Architecture와 기본 구조
- Database Management Subsystem Architecture와 기본 구조
- 공통 Interface, Metadata와 Schema 정책
- Execution Database 연결 계약
- Migration, Backup, Restore와 Recovery 기준
- Health·Performance·Capacity 관찰 기반
- Validation과 필수 Test Matrix
- 기존 구현의 v1.7 구조 매핑과 호환성 계획

후속 Version 범위:

- 고급 Query Optimization
- 자동 Capacity Planning
- 고급 Operational Analytics와 Pattern Detection
- 정책 기반 Maintenance Automation
- 다중 Storage Provider와 분산 Database
- 자동 Scaling과 고급 Recovery Orchestration

## Phase 1: Shared Standard Alignment

### Work

- OS Ecosystem Shared Database Standard Version 확인
- Official Hierarchy, Naming, Interface, Metadata Rule 매핑
- 기존 문서·구현 중복과 충돌 식별
- Living OS 고유 책임과 공유 책임 분리

### Gate

- Shared Standard Reference가 명확함
- 로컬 재정의 또는 승인되지 않은 예외가 없음
- Design Review 입력이 준비됨

## Phase 2: MASTER DESIGN

### Work

- Parent Module과 Component ID 확정
- Subsystem·Engine Group·Engine 책임 확정
- Data Owner와 Schema Catalog 확정
- 공개 Interface와 Dependency 확정
- Execution·Information Management 연결 확정
- Security, Permission, Failure와 Recovery 설계

### Gate

- Architecture와 책임 충돌 없음
- MASTER DESIGN이 해당 Version SSOT로 승인됨
- User Approval 완료

## Phase 3: Structure and Compatibility

### Work

- 표준 Folder·Package 구조 생성
- 현재 `HubStore`, `SchemaRegistry`, Migration, Backup 구현 매핑
- `core` compatibility alias 유지·폐기 계획
- 기존 Module별 SQLite 저장소의 소유권과 Migration 범위 확인

### Gate

- 기존 공개 동작과 데이터 경로가 식별됨
- Breaking Change, Deprecated 기간, Rollback 계획이 문서화됨
- Regression 범위가 확정됨

## Phase 4: Database Subsystem Foundation

### Work

- Storage, Repository, Transaction, Schema, Integrity Interface 정렬
- Record와 Schema Version 분리
- Module Data Owner와 Permission 적용
- 공통 Error와 Execution Metadata 연결
- Migration·Backup·Restore Adapter 연결

### Gate

- CRUD, Integrity, Transaction, Concurrency Test 통과
- 내부 Storage 직접 접근이 차단됨
- 주요 Write가 Execution ID로 추적됨

## Phase 5: Database Management Foundation

### Work

- Health Model과 Read-only Monitor
- Performance·Capacity 측정 계약
- Maintenance Recommendation과 승인 경계
- Recovery Control과 Report 연결
- Configuration 기반 threshold Version 관리

### Gate

- Control plane이 업무 Data Owner를 침범하지 않음
- Health·Performance·Capacity 결과를 추적할 수 있음
- 위험 Maintenance에 Backup·Approval·Rollback이 적용됨

## Phase 6: Migration and Recovery Verification

### Work

- Migration dry-run, checksum, quarantine, idempotency 검증
- Backup Manifest, checksum, retention 검증
- Restore staging, safety backup, Integrity, rollback 검증
- Failure와 partial failure 시나리오 실행

### Gate

- Migration·Backup·Restore·Rollback Test 통과
- 검증된 Recovery Point와 Restore Test Evidence 존재
- 실패 시 Silent Data Loss가 없음

## Phase 7: Integration and Quality Review

### Work

- Information Management와 Execution Database 연동 Test
- Module Regression 및 Streamlit 연결 Test
- Security·Permission·Performance·Capacity Test
- Architecture, Code, Documentation 일치 Review
- Known Issue와 Release Risk 정리

### Gate

- 필수 Test Matrix 통과
- Critical·High 미해결 결함 없음
- Codex Review 완료
- User Approval 완료

## Phase 8: Release Preparation

### Work

- Migration, Backup, Rollback 준비 확인
- Release Note와 Changelog 작성
- GitHub Commit·Push·Release 승인 요청
- Streamlit Deploy와 Stable Verification
- Test, Decision, Migration, Release Evidence Archive

### Gate

- Release Governance 조건 충족
- 배포 환경과 Repository Version 일치
- Database 연결, Version, Migration, Error Log와 Rollback 확인
- Stable Verification 완료

## v1.7 Definition of Done

- Architecture와 MASTER DESIGN 승인
- 11개 Database Foundation 문서 최신화
- 공통 Structure와 Interface 구현
- 기존 데이터와 Module 호환성 검증
- Execution Database·Information Management 연결 검증
- Migration, Backup, Restore, Failure Recovery Test 통과
- Database Management 기본 Monitor와 Recovery 경계 구현
- Codex Review와 User Approval 완료
- Release, Deploy, Stable Verification, Archive 완료

## Next Step

Phase 1–7의 Architecture, 구현, 격리 Validation, 전체 Regression, Streamlit Smoke Test와 Documentation 동기화는 v1.7 Stable에서 완료되었다.

다음 단계는 Phase 8의 User Approval이다. 승인 전에는 Git Commit, Push, GitHub Release, Production Deploy, Stable Verification 또는 Archive를 수행하지 않는다. v1.8 개발도 시작하지 않는다.
