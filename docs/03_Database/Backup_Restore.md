# Living OS v1.7 Backup and Restore Standard

## Purpose

본 문서는 Database와 Migration 대상 데이터의 Backup, 검증, Restore, Rollback 기준을 정의한다. Backup 파일의 존재가 아니라 실제 복구 가능성을 완료 조건으로 사용한다.

## Backup Principles

- 일관된 시점의 Snapshot을 생성한다.
- Backup은 원본과 분리된 위치에 저장한다.
- Manifest에 Format, Version, 생성 시각, 대상과 checksum을 기록한다.
- Backup 결과는 생성 직후 검증한다.
- Secret과 민감 데이터는 접근 통제 및 보호 정책을 적용한다.
- Retention과 Archive 정책에 따라 Version을 유지한다.
- Migration과 Restore 전에 안전 Backup을 만든다.

## Backup Types

| Type | Purpose |
| --- | --- |
| Release Backup | Stable Release 상태의 장기 보관 |
| Pre-migration Backup | Schema·데이터 전환 전 복구점 |
| Pre-restore Safety Backup | Restore 실패 또는 잘못된 선택에 대비 |
| Operational Backup | 정기 운영 복구점 |
| Export Archive | 승인된 교환 형식; Database Backup을 대체하지 않음 |

## Backup Manifest

최소 항목:

- Backup ID
- Format Version
- Product Version
- Schema Version
- Created At
- Created By
- Source Database Reference
- Included Files
- File Size와 Checksum
- Encryption·Protection Status
- Retention Class
- Verification Status와 Verified At
- Execution ID와 Trace ID

## Backup Workflow

`Request → Permission → Consistent Snapshot → Package → Checksum → Verify → Register → Retain/Archive`

실패한 Backup은 사용 가능한 복구점으로 등록하지 않는다.

## Restore Workflow

1. Restore 대상과 승인 근거를 확인한다.
2. Archive Manifest와 모든 checksum을 검증한다.
3. Path traversal와 인식되지 않은 파일을 차단한다.
4. 현재 상태의 안전 Backup을 생성하고 검증한다.
5. 격리된 임시 위치에 복원한다.
6. Schema Version과 Database Integrity를 검사한다.
7. 원자적으로 대상과 교체한다.
8. App 연결, 핵심 Query와 Execution 기록을 검증한다.
9. 실패하면 원 상태로 Rollback한다.
10. 결과와 Recovery Report를 기록한다.

## Recovery Objectives

RPO와 RTO는 환경·데이터 중요도별 Configuration으로 정의한다. 값이 승인되기 전에는 보장 수치로 문서화하지 않는다.

- RPO: 허용 가능한 데이터 손실 시점
- RTO: 허용 가능한 서비스 복구 시간

## Security and Privacy

- Backup에 API Key나 불필요한 Secret을 포함하지 않는다.
- 민감 데이터 Backup은 원본과 동일하거나 더 강한 Permission을 사용한다.
- 외부 Media 또는 Cloud 이동은 사용자 승인과 Audit을 요구한다.
- 영구 폐기는 Retention 만료, 승인, Audit과 복구 불가성 확인을 요구한다.

## Current Baseline

현재 `BackupService`는 SQLite online backup으로 Snapshot을 만들고 ZIP Manifest와 SHA-256으로 파일을 검증한다. Restore는 임시 파일에 staging하고 SQLite Integrity Check를 수행하며, 적용 전에 safety backup을 만들고 실패 시 원본 복구를 시도한다.

v1.7 Backup 이름은 `living_os_v1_7_database_<UTC timestamp>.zip` 형식을 사용하며 Manifest에 format, product, schema Version, 생성 시각, file checksum을 기록한다. 기본 경로는 `backups/v1.7/database/`이다.

Backup과 Restore 결과는 Execution Database 및 history Table에 기록한다. Restore는 candidate checksum, Schema v2, SQLite Integrity를 사전 검증하고, 현재 Database의 safety backup을 만든 후 staging·교체·검증을 수행한다. Restore 이후 기존 control-plane history를 병합하여 Backup·Execution Audit이 사라지지 않도록 한다.

## Required Tests

- 빈 Database와 populated Database Backup
- Manifest와 checksum 검증
- 손상 Archive 거부
- 알 수 없는 파일과 안전하지 않은 경로 거부
- Restore 전 safety backup 생성
- Restore 후 Integrity와 핵심 Query 확인
- 중간 파일 교체 실패 시 Rollback
- Version 불일치 처리
- Permission과 민감정보 보호
- 정기 Restore Drill

## Acceptance Criteria

- 검증되지 않은 Backup으로 Restore하지 않음
- Restore 성공을 파일 복사만으로 판정하지 않음
- 최근 검증된 복구점과 Restore Test 결과를 찾을 수 있음
- 실패 시 원본 또는 safety backup으로 복구 가능함
- 모든 작업이 Execution ID와 Audit 근거를 가짐

## Related Documents

- [Migration](Migration.md)
- [Database Management Subsystem](Database_Management_Subsystem.md)
- [Database Testing](Database_Testing.md)
