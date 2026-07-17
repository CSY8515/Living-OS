# Living OS v1.7 Database Migration Standard

## Purpose

본 문서는 Database Schema와 데이터 Version을 안전하고 재현 가능하게 전환하는 Migration 기준을 정의한다.

## Principles

- Versioned: 모든 Migration은 고유 ID와 Source·Target Version을 가진다.
- Dry-run first: 적용 전에 대상과 오류를 검사한다.
- Backup first: 변경 전에 검증 가능한 Backup을 생성한다.
- Transactional: 가능한 변경은 하나의 Transaction으로 수행한다.
- Idempotent: 재시도 시 중복 적용이나 손상이 없어야 한다.
- Auditable: 승인·입력 checksum·결과·오류를 추적한다.
- Recoverable: 실패와 취소 시 원래 상태로 복구할 수 있어야 한다.

## Migration Record

최소 기록 항목:

- Migration ID
- Source Version
- Target Version
- Schema Version
- Data Owner
- Reason과 Decision Reference
- Input Source와 Checksum
- Dry-run Result
- Backup Reference
- Started At과 Completed At
- Status
- Accepted·Rejected·Quarantined Count
- Error Reference
- Rollback Reference
- Execution ID와 Trace ID
- Applied By와 Approval Reference

## Lifecycle

PLANNED

↓

VALIDATING

↓

DRY_RUN_COMPLETED

↓

APPROVED

↓

BACKED_UP

↓

RUNNING

↓

VALIDATING_RESULT

↓

COMPLETED

실패 시 `FAILED → ROLLING_BACK → ROLLED_BACK`으로 전환한다. 자동 복구가 불가능하면 `RECOVERY_REQUIRED`로 전환하고 추가 Write를 중지한다.

## Procedure

1. Source와 Target Version을 확인한다.
2. 입력 데이터와 Schema를 읽기 전용으로 검사한다.
3. checksum과 대상 건수를 기록한다.
4. Dry-run으로 accepted, rejected, quarantined 항목을 보고한다.
5. Migration·Backup·Rollback 계획을 Review한다.
6. 필요한 User Approval을 받는다.
7. Backup을 생성하고 검증한다.
8. Migration을 Transaction 안에서 적용한다.
9. Schema, record count, 관계, checksum과 업무 불변조건을 검증한다.
10. 결과와 Execution Metadata를 기록한다.
11. 실패하면 Rollback 또는 검증된 Backup Restore를 수행한다.

## Compatibility Rules

- 기존 공개 Interface의 하위 호환성을 최대한 유지한다.
- Legacy Reader나 alias는 명시된 Deprecated 기간 동안만 유지한다.
- 데이터 의미가 달라지는 변환은 단순 Rename으로 취급하지 않는다.
- 미지원 Record를 삭제하지 않고 Quarantine한다.
- 일부 Record 오류를 전체 성공으로 보고하지 않는다.
- 동일 Migration의 재실행 조건을 명시한다.

## Current Baseline

현재 `V1MigrationService`는 JSON·JSONL·Markdown 입력을 checksum으로 추적하고, 잘못된 항목을 quarantine하며, dry-run과 적용을 분리한다. 적용 전 검증된 Backup을 만들고 Migration 실행 결과를 저장한다.

v1.7 Migration Registry는 additive Schema Version `1 → 2`를 순차 Transaction으로 적용하고 `database_migrations`에 결과를 기록한다. 실패한 Migration은 전체 Rollback 후 `database_migration_failures`에 유형을 기록한다. Startup에서는 Migration을 적용하지 않으며 Settings의 명시적 승인 작업으로만 실행한다.

실제 사용자 Database에는 이 Migration을 실행하지 않았다. 테스트에서는 격리된 임시 Database에 성공, 중복 방지, 실패 Rollback을 검증했다.

## Test Requirements

- Dry-run이 데이터에 Write하지 않음
- 동일 입력 checksum이 재현됨
- 성공 Migration이 목표 Version과 건수를 충족함
- 중복 실행이 차단되거나 안전함
- 잘못된 입력이 Quarantine됨
- 중간 실패가 부분 데이터를 남기지 않음
- Backup 실패 시 Migration을 시작하지 않음
- Rollback 또는 Restore 후 Integrity가 유지됨
- Legacy compatibility가 승인 기간 동안 유지됨

## Release Gate

Migration이 포함된 Release는 Migration Plan, Backup, Restore, Rollback, Test Result, Known Issue와 사용자 승인을 갖춰야 한다.

## Related Documents

- [Database Schema](Database_Schema.md)
- [Backup and Restore](Backup_Restore.md)
- [Database Testing](Database_Testing.md)
- [Database Workflow](Database_Workflow.md)
