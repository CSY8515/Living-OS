# Living OS v1.7 Database Subsystem

## Purpose

Database Subsystem은 Living OS의 Module 데이터와 공통 운영 데이터를 안전하게 저장하고 조회하는 공통 Subsystem이다. 데이터 무결성과 Transaction 경계를 소유하며, 저장된 데이터의 업무적 해석이나 운영 상태 관리는 소유하지 않는다.

## Responsibility

Database Subsystem은 다음 책임을 가진다.

- Schema와 Table 또는 Collection 관리
- Storage Adapter 관리
- Create, Read, Update, Delete
- Query와 Transaction
- Index와 Constraint
- Integrity Validation
- Schema Version과 Migration 실행
- Backup Snapshot과 Restore 적용
- Database Version 식별

## Non-responsibility

다음 책임은 Database Subsystem에 포함하지 않는다.

- 데이터 분류·연결·Knowledge Asset 변환
- Health·Performance·Capacity 정책 판단
- 업무 데이터의 의미 변경
- Analytics 결과를 이용한 Decision 또는 Rule 생성
- 사용자 승인 없는 영구 삭제
- Module별 Execution Database 복제

## Ownership Model

각 데이터 Entity는 하나의 Module Data Owner를 가진다. 공통 Database를 사용하더라도 소유권은 Module 경계로 구분한다.

- Owner Module만 공식 Write Interface를 제공한다.
- 다른 Module은 Owner의 Interface 또는 Event를 사용한다.
- Cross Module Query는 승인된 Read Model 또는 Search Interface를 사용한다.
- 물리 Table 공유가 논리적 소유권 공유를 의미하지 않는다.

## Internal Components

| Component | Responsibility |
| --- | --- |
| Schema Registry | Module, Entity, Schema Version 등록과 Validation |
| Storage Adapter | SQLite 등 물리 저장소 차이 격리 |
| Transaction Manager | Atomicity, commit, rollback 경계 관리 |
| Repository | Entity 단위 Query와 Persistence 계약 구현 |
| Integrity Validator | Constraint와 일관성 검사 |
| Migration Runner | 승인된 Version 전환 실행 |
| Backup Adapter | 일관된 Snapshot 생성 |
| Restore Adapter | 검증된 Snapshot 적용과 실패 Rollback |

Engine Group과 Engine 배치는 MASTER DESIGN에서 확정하며, 각 Engine은 하나의 실행 책임만 가진다.

## Data Flow

`Module Service → Database Interface → Validation → Transaction → Storage Adapter → Database`

Read 결과는 호출 Module로 반환되며, 정보 분류와 Knowledge Asset 변환은 Information Management Interface로 전달한다.

## Execution Integration

다음 주요 작업은 공통 Execution Interface로 기록한다.

- Schema initialization
- Data mutation
- Migration dry-run 및 apply
- Backup create 및 verify
- Restore 및 rollback
- Integrity check
- Maintenance action

기록에는 Execution ID, Trace ID, Module, Subsystem, Engine, Function, input/output reference, status, version, duration과 error reference를 포함한다. Secret과 민감한 원문은 저장하지 않는다.

## Safety Rules

- Write 전에 Input과 Permission을 검증한다.
- 다중 변경은 명시적 Transaction으로 묶는다.
- 경쟁 갱신은 Version 또는 동등한 concurrency control로 감지한다.
- Schema 변경은 Migration 없이 적용하지 않는다.
- 영구 삭제보다 Soft Delete를 우선한다.
- Restore 전에 현재 상태의 안전 백업을 생성한다.
- 실패 시 부분 적용을 남기지 않는다.

## Actual Implementation

공식 facade는 `subsystems/database/subsystem.py`의 `DatabaseSubsystem`이다.

Engine 경로:

- `engines/connection.py`: SQLite connection과 transaction
- `engines/migrations.py`: Schema v2 Migration Registry와 history
- `engines/component.py`: v1.7.1 공통 Database Integration Contract와 compatibility Adapter
- `engines/repository.py`: CRUD, Search, Archive, Version check
- `engines/execution.py`: Execution Database record
- `engines/integrity.py`: Integrity, Foreign Key, Table, Index, Version check
- `engines/contracts.py`: Control Interface와 결과 계약

기존 `HubStore`, `SchemaRegistry`, `V1MigrationService`, `BackupService`를 재사용하며 `core` 경로의 compatibility alias를 유지한다.

## Acceptance Criteria

- 공개 Interface 외 내부 저장 구현에 직접 접근하지 않음
- Module별 Data Owner와 Entity Schema가 식별됨
- Transaction, Integrity, Migration, Backup, Restore가 테스트됨
- Database Management와 Information Management 책임이 분리됨
- 모든 주요 실행을 Trace할 수 있음
- 실패 후 원래 상태로 복구할 수 있음

## Related Documents

- [Database Management Subsystem](Database_Management_Subsystem.md)
- [Database Schema](Database_Schema.md)
- [Database Interface](Database_Interface.md)
- [Database Workflow](Database_Workflow.md)
- [Database Testing](Database_Testing.md)
