# Living OS v1.7 Database Foundation

## Purpose

이 디렉터리는 Living OS v1.7 Database Foundation의 공식 설계와 구현 기준이다. Database Subsystem과 Database Management Subsystem의 책임을 분리하고, 모든 Module이 공유할 저장·운영 계약과 검증 결과를 정의한다.

공통 Architecture와 Governance는 이 디렉터리에서 재정의하지 않는다. 다음 문서를 상위 기준으로 사용한다.

- [Architecture Principles](../01_Architecture/Architecture_Principles.md)
- [Architecture Governance](../01_Architecture/Governance.md)
- [Shared Architecture Adoption](../01_Architecture/Shared_Architecture.md)
- [Architecture Standards](../01_Architecture/Architecture_Standards.md)
- [Design Review Standard](../01_Architecture/Design_Review_Standard.md)

## Architecture Position

공식 계층은 다음과 같다.

`User → Ultra Brain → Meta OS Ecosystem → OS Ecosystem → OS System → Capability → Module → Subsystem → Engine Group → Engine → Function`

Database Subsystem과 Database Management Subsystem은 Settings/Admin Module이 조정하는 동급의 독립 Subsystem이다. 어느 Subsystem도 다른 하나를 소유하지 않으며, Database Management는 공식 Control Interface만 사용한다.

## Responsibility Boundary

| Area | Owns | Must not own |
| --- | --- | --- |
| Database Subsystem | Schema, Storage, CRUD, Query, Transaction, Index, Constraint, Integrity, Migration, Backup, Restore, Version | 운영 정책 판단, 정보 분류, 업무 의미 변경 |
| Database Management Subsystem | Health, Performance, Capacity, Optimization, Cleanup, Maintenance, Recovery Control, Operational Statistics | 업무 데이터 직접 수정, Schema의 임의 변경 |
| Information Management | Classification, Metadata enrichment, Linking, Search, Knowledge Asset lifecycle | 물리 저장소와 Transaction 구현 |
| Execution Database | 주요 실행의 Metadata, 상태, 결과 참조와 Trace | 업무 데이터 원본의 중복 저장 |

## Document Map

| Document | Single responsibility |
| --- | --- |
| [Database Subsystem](Database_Subsystem.md) | 저장 및 무결성 책임 |
| [Database Management Subsystem](Database_Management_Subsystem.md) | Database 운영 책임 |
| [Database Schema](Database_Schema.md) | Schema 설계·등록·변경 기준 |
| [Migration](Migration.md) | Version 간 안전한 데이터 전환 |
| [Backup and Restore](Backup_Restore.md) | 백업·검증·복원·복구 기준 |
| [Database Interface](Database_Interface.md) | 외부에 공개하는 Database 계약 |
| [Database Metadata](Database_Metadata.md) | Database 공통 Metadata 기준 |
| [Database Workflow](Database_Workflow.md) | 요청·실행·운영 흐름 |
| [Database Testing](Database_Testing.md) | 검증과 필수 테스트 기준 |
| [Database Roadmap](Database_Roadmap.md) | v1.7 구현 준비와 후속 확장 순서 |

## Implemented Structure

현재 v1.7.1 Stable에는 다음 구조가 구현되어 있다.

- `subsystems/database/`: Data Plane facade와 Connection, Migration, Repository, Execution, Integrity engines
- `subsystems/database_management/`: Control Plane facade와 Health, Report engines
- additive Schema v2/v3 Migration과 Migration history
- Finance, Health, Vehicle, Housing, Food 공통 Component Adapter 및 RecordRepository 계약 등록
- 등록 구성요소 통합 Schema/Migration/Health/Integrity/Backup/Restore/Execution 관리
- 신규 및 상위 Architecture 계층용 Database Integration Contract와 Bootstrap Template
- CRUD, Search, Soft Archive, Transaction, optimistic concurrency
- Execution, Backup, Restore history와 required indexes
- checksum·Manifest 검증 Backup과 staging·safety backup·Integrity Restore
- Health, Schema Registry, Migration, Backup, Restore, Performance, Capacity 상태와 운영 보고
- Settings의 명시적 Migration·Health·Backup·Restore·Report controls

기존 Hub와 Module별 Database 경로는 유지된다. 실제 사용자 Hub Database에는 v1.7 Migration을 자동 적용하지 않으며, Settings의 명시적 승인 후에만 적용한다.

## v1.7 Completion Gate

- 책임·Interface·Data Owner가 MASTER DESIGN에 확정됨
- Schema와 Migration Version이 추적 가능함
- Backup 생성뿐 아니라 Restore가 검증됨
- 모든 주요 Database 작업이 Execution Interface와 연결됨
- CRUD, Integrity, Transaction, Migration, Backup, Restore, Rollback, Performance, Capacity, Failure Recovery 테스트가 통과함
- Documentation, Source, Test, Release Version이 일치함
- Codex Review와 User Approval이 완료됨

## Status

- Version: `1.7.0-rc`
- Status: `REVIEW`
- Scope: Implementation, Validation, Testing, Release Preparation
- Production target: v1.7.1 Stable
- Release workflow: approved; Commit, Push, Release, Deploy, Stable Verification, Archive 진행
