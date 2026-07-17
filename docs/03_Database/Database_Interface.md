# Living OS v1.7 Database Interface Standard

## Purpose

본 문서는 Module과 Shared Foundation이 Database 내부 구현에 직접 의존하지 않도록 공개 Interface 계약을 정의한다. 구체적인 언어 API와 Request·Response Schema는 MASTER DESIGN에서 확정한다.

## Interface Principles

- Interface에 의존하고 SQLite 등 구현체에 의존하지 않는다.
- 호출자는 Data Owner와 Permission 범위를 명시한다.
- 모든 Input과 Output은 Version이 있는 Schema를 사용한다.
- Write는 Validation, Transaction, Error와 Execution ID를 제공한다.
- Retry는 idempotency가 보장된 작업에서만 허용한다.
- Timeout, Cancellation, Deprecation 정책을 명시한다.
- 민감한 값은 Log와 Error Message에 노출하지 않는다.

## Common Contract

각 Interface는 다음 Metadata를 가진다.

- Interface ID
- Purpose
- Caller
- Receiver
- Input Schema
- Output Schema
- Permission
- Validation
- Error
- Timeout
- Retry
- Version
- Deprecation Policy

공통 Output은 `Result`, `Status`, `Message`, `Data`, `Error`, `Execution ID`, `Timestamp`, `Version`을 포함한다.

## Database API

### Create

- 새로운 Entity를 등록한다.
- Owner, Entity Type, Record ID, Schema Version과 Payload가 필요하다.
- 동일 ID 정책과 초기 Version을 검증한다.
- 성공 시 생성된 Reference와 Record Version을 반환한다.

### Read

- Entity Reference를 이용해 승인된 View를 반환한다.
- 존재 여부와 Read Permission을 구분해 처리한다.
- 내부 Storage 경로나 Secret을 반환하지 않는다.

### Update

- 예상 Record Version을 받아 경쟁 갱신을 감지한다.
- 변경 전후 전체 민감 Payload 대신 안전한 Reference를 기록한다.
- 성공 시 새 Record Version을 반환한다.

### Delete

- 기본적으로 Soft Delete를 수행한다.
- 영구 삭제는 별도 Permission, Approval, Retention 확인과 Audit을 요구한다.
- 관계와 Archive 영향을 검증한다.

## Query API

Query는 Owner, Entity Type, Filter, Sort, Pagination, Projection, Permission을 명시한다.

- 임의 SQL이나 Storage-specific Query를 외부에 노출하지 않는다.
- Size Limit과 Timeout을 적용한다.
- Cross Module 조회는 승인된 Read Model 또는 Search Interface로 제한한다.
- Query 결과의 Schema Version을 반환한다.

## Schema API

- Register Schema
- Get Schema
- Validate Payload
- List Supported Versions
- Deprecate Schema

Schema 등록과 폐기는 Owner와 Governance 승인을 확인한다.

## Migration API

- Plan
- Dry Run
- Apply
- Get Status
- Cancel when safe
- Rollback 또는 Recovery Request

Apply는 승인, 검증된 Backup과 Dry-run 결과 없이는 실행하지 않는다.

## Backup API

- Create
- Verify
- List Recovery Points
- Get Manifest
- Apply Retention

## Restore API

- Validate Archive
- Preview
- Restore
- Verify Result
- Rollback

Restore는 Database Management 또는 승인된 관리 Workflow에서만 호출한다.

## Health, Performance and Analytics API

- Health: connection, integrity, migration state와 Health status 조회
- Performance: latency, lock, throughput 등 운영 측정값 조회
- Capacity: size, growth, free-space 상태 조회
- Analytics: 집계된 운영 통계 조회

이 API는 업무 데이터 원문을 반환하지 않으며 Database Management 책임에 속한다.

## Error Contract

최소 Error 정보:

- Error Code와 Type
- 안전한 Message
- Source
- Severity
- Recoverable
- Retryable
- Execution ID와 Trace ID
- Created At

Expected Version 불일치, Permission 거부, Validation 실패, Integrity 실패, Timeout과 Storage 장애를 구분한다.

## Acceptance Criteria

- Module이 Database 파일이나 Table에 직접 접근하지 않음
- CRUD와 관리 API의 책임이 분리됨
- Version, Permission, Validation, Timeout, Error가 계약에 존재함
- Write·Migration·Restore 결과를 Execution ID로 추적 가능함
- 구현체 교체가 호출 Module의 업무 로직 변경을 요구하지 않음

## Actual Python Interfaces

- Data Plane: `subsystems.database.DatabaseSubsystem`
- Control Plane: `subsystems.database_management.DatabaseManagementSubsystem`
- Control contract: `subsystems.database.engines.contracts.DatabaseControlInterface`

Data Plane은 `initialize`, `transaction`, `create`, `read`, `update`, `archive`, `list`, `search`, `apply_migrations`, `integrity_check`, `create_backup`, `validate_restore`, `restore`, `schema_registry`, `execution_records`를 제공한다.

Control Plane은 `health_check`, `schema_registry`, `migration_status`, `request_migration`, `backup_status`, `request_backup`, `restore_candidates`, `preflight_restore`, `request_restore`, `operational_report`를 제공한다.

## Related Documents

- [Database Subsystem](Database_Subsystem.md)
- [Database Metadata](Database_Metadata.md)
- [Database Workflow](Database_Workflow.md)
- [Architecture Standards](../01_Architecture/Architecture_Standards.md)
