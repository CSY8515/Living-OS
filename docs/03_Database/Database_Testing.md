# Living OS v1.7 Database Testing Standard

## Purpose

본 문서는 Database Foundation이 Architecture, 무결성, 복구 가능성과 운영 품질을 충족하는지 검증하는 필수 테스트 기준을 정의한다.

## Test Principles

- 테스트는 격리된 임시 Database와 Backup 위치를 사용한다.
- Production 데이터와 운영 Secret을 사용하지 않는다.
- 성공 경로뿐 아니라 실패·취소·부분 장애를 검증한다.
- Test Result는 Product, Schema, Migration, Interface Version을 기록한다.
- 테스트가 생성한 파일과 상태는 종료 후 정리한다.
- Stable 판정에는 실제 Restore Test가 필요하다.

## Required Test Matrix

| Area | Required verification |
| --- | --- |
| CRUD | Create, Read, Update, Soft Delete, not-found, duplicate ID |
| Integrity | Primary·Foreign·Unique·Check Constraint, invalid payload |
| Transaction | atomic commit, rollback, nested workflow boundary |
| Concurrency | expected version success and conflict rejection |
| Migration | dry-run, checksum, apply, idempotency, quarantine, rollback |
| Backup | snapshot consistency, manifest, checksum, retention metadata |
| Restore | staging, integrity, safety backup, rollback, post-restore query |
| Performance | representative query latency and transaction duration |
| Capacity | growth, free-space threshold, large result limit |
| Failure Recovery | corrupted input, I/O error, lock, interrupted operation |
| Permission | unauthorized read/write/admin operation rejection |
| Security | Secret redaction, unsafe archive path, malformed input |
| Execution | Execution ID, Trace ID, state transition, error reference |
| Compatibility | legacy import path and approved deprecated behavior |

## Unit Tests

- Schema Validator와 Registry
- Metadata Validator
- Repository CRUD와 Version check
- Error mapping
- checksum과 Manifest 검증
- Migration transform
- Health 상태 판정
- Retention 계산

외부 Storage와 시간은 가능한 한 명시적인 Adapter 또는 주입 가능한 경계로 격리한다.

## Integration Tests

- Module Service → Database Interface → Storage
- Write → Domain Event/Audit → Execution Record
- Migration → Backup → Storage → Validation
- Restore → Integrity Check → App reconnect
- Database Reference → Information Management handoff
- Monitor → Recommendation → 승인된 Maintenance

## Regression Tests

현재 지원하는 Module 데이터, 기존 Database 파일, compatibility alias와 공개 Interface가 승인된 범위에서 계속 동작하는지 검증한다.

Migration이나 Schema 변경 시 영향을 받는 모든 Module의 Regression Test를 수행한다.

## Migration Tests

- Dry-run은 Write와 Backup을 생성하지 않음
- Source checksum과 대상 건수가 재현됨
- 잘못된 입력은 삭제되지 않고 quarantine됨
- Backup 검증 실패 시 apply 금지
- Transaction 중 실패 시 부분 Record가 남지 않음
- 성공 시 Migration Run과 Version이 일치함
- 중복 실행 정책이 지켜짐
- Rollback 후 이전 Integrity가 유지됨

## Backup and Restore Tests

- Backup 생성 직후 Verify 통과
- 한 Byte라도 변조된 Archive 거부
- Manifest 누락과 잘못된 Format 거부
- 안전하지 않은 상대 경로 거부
- Restore 전 safety backup 생성 및 검증
- Staged Database의 Integrity Check
- Restore 후 핵심 Record와 Version 확인
- 파일 교체 실패 시 원본 복구
- WAL·temporary artifact 정리

## Performance and Capacity

정확한 임계값은 MASTER DESIGN과 운영 환경 Configuration에서 승인한다. 테스트는 최소한 다음 측정값을 남긴다.

- dataset size와 record count
- query와 transaction p50/p95 또는 동등한 분포
- backup·restore·migration duration
- database와 backup size
- lock·retry·failure count
- 측정 환경과 Version

숫자 기준이 없는 측정은 관찰 결과이며 PASS 보장으로 사용하지 않는다.

## Failure Recovery Tests

- Database unavailable
- disk full 또는 write failure 모사
- concurrent lock timeout
- corrupted backup
- invalid migration input
- process interruption 경계
- monitor unavailable
- rollback failure escalation

복구 불가능한 실패는 조용히 무시하지 않고 `RECOVERY_REQUIRED`와 명확한 운영 지침을 남긴다.

## Test Evidence

Test Report에는 다음을 포함한다.

- Test Run ID와 Execution ID
- 대상 Product·Schema·Interface Version
- 환경과 Configuration Reference
- 수행 항목과 결과
- 실패 원인과 재현 방법
- 생성된 Backup·Migration·Report Reference
- 잔여 위험과 Known Issue
- Reviewer와 승인 상태

## Stable Gate

- 필수 Unit, Integration, Regression Test 통과
- Migration, Backup, Restore, Failure, Permission Test 통과
- 승인된 Performance·Capacity 기준 충족
- High/Critical 미해결 결함 없음
- Test Evidence와 Documentation 동기화
- Codex Review와 User Approval 완료

## Current Baseline

v1.7 Stable은 Database Foundation 전용 10개 테스트를 포함한 전체 98개 테스트를 통과했다. 전용 테스트는 초기화·중복 초기화·Schema·Index·CRUD·Search·Archive·Transaction Rollback·optimistic concurrency·Migration 성공/실패 Rollback·Backup 성공/실패·Restore 성공/실패·Integrity·손상 파일·Health·Schema Registry·Capacity warning·운영 보고·기존 5개 Subsystem 독립성을 검증한다.

전체 Suite는 Architecture dependency, 기존 Module, Security, Migration, Backup/Restore, Streamlit 모든 페이지와 no-write page-load 회귀를 포함한다. 결과는 [v1.7 Test Report](../releases/v1.7/TEST_REPORT.md)에 기록한다.

## Related Documents

- [Database Workflow](Database_Workflow.md)
- [Migration](Migration.md)
- [Backup and Restore](Backup_Restore.md)
- [Design Review Standard](../01_Architecture/Design_Review_Standard.md)
