# Living OS v1.7 Database Workflow

## Purpose

본 문서는 Database 요청, 변경, 운영 관리와 Execution 기록이 연결되는 표준 Workflow를 정의한다.

## Standard Data Workflow

`Request → Permission → Input Validation → Schema Validation → Transaction → Storage → Integrity Check → Execution Record → Response`

### Request

Caller, Owner Module, Operation, Entity Reference, Interface Version과 Trace ID를 식별한다.

### Validation

Permission, Input Schema, Size Limit, Record Version, 상태 전이와 업무 Validation을 확인한다.

### Transaction

다중 Write는 하나의 원자적 경계에서 처리한다. 실패하면 전체를 Rollback한다.

### Storage and Integrity

공식 Repository와 Storage Adapter만 사용한다. Constraint와 중요한 불변조건을 검사한다.

### Execution Record and Response

상태, 결과 Reference, Error, Duration과 Version을 기록한 후 표준 Output을 반환한다.

## Read Workflow

`Read Request → Permission → Query Validation → Repository → Projection → Response`

- Read도 Privacy Class와 Data Owner 정책을 적용한다.
- 필요한 Field만 Projection한다.
- 대량 Query는 Pagination, Limit과 Timeout을 적용한다.
- Cross Module 검색은 승인된 Search 또는 Read Model을 사용한다.

## Write Workflow

`Write Request → Permission → Validation → Expected Version Check → Transaction → Event/Execution Record → Commit → Response`

- concurrency conflict는 덮어쓰지 않고 명시적 Error로 반환한다.
- Domain Event와 Audit이 필요한 경우 업무 Write와 같은 Transaction 경계를 사용한다.
- Commit 후 Notification 실패가 업무 Write를 되돌릴지 여부는 Workflow 정책에 명시한다.

## Information Handoff

`Database Reference → Information Management Interface → Classification → Linking → Knowledge Asset`

Database는 저장된 값의 의미를 재분류하지 않는다. Information Management에는 승인된 Reference와 필요한 Metadata만 전달한다.

## Execution Database Integration

Execution Lifecycle:

RECEIVED

↓

VALIDATING

↓

QUEUED

↓

RUNNING

↓

COMPLETED

또는 `FAILED` 또는 `CANCELLED`

Database 업무 데이터와 Execution Record는 역할을 분리한다. Execution Record는 원본 전체를 복제하지 않고 Input·Output Reference를 저장한다.

## Maintenance Workflow

`Monitor → Detect → Analyze → Recommend → Review/Approval → Backup → Maintain → Validate → Report`

- Monitor는 Read-only를 기본으로 한다.
- Optimization, Cleanup, Recovery는 별도 관리 Interface를 사용한다.
- 위험 작업은 User Approval, Audit과 Rollback을 요구한다.

## Migration Workflow

`Plan → Dry Run → Review → User Approval → Backup/Verify → Apply → Validate → Complete or Rollback`

세부 기준은 [Migration](Migration.md)을 따른다.

## Backup and Restore Workflow

- Backup: `Request → Snapshot → Manifest → Checksum → Verify → Register`
- Restore: `Approve → Verify Archive → Safety Backup → Stage → Integrity Check → Replace → Verify → Report`

세부 기준은 [Backup and Restore](Backup_Restore.md)를 따른다.

## Failure Handling

| Failure point | Required action |
| --- | --- |
| Validation | Write 없이 실패 반환 |
| Permission | Audit 가능한 거부 결과 기록 |
| Transaction | 전체 Rollback |
| Integrity | Commit 금지 및 Error 기록 |
| Migration | 중지 후 Rollback 또는 Recovery Required |
| Backup verify | 복구점 등록 금지 |
| Restore | 원본 또는 safety backup 복구 |
| Monitor | 상태를 UNKNOWN/DEGRADED로 표시; 업무 데이터 임의 변경 금지 |

## Approval Boundaries

영구 삭제, Production Migration, Restore, Recovery, 외부 Backup 전송, Permission 변경은 사용자 승인 또는 사전 승인된 명확한 Rule을 요구한다.

## Related Documents

- [Database Interface](Database_Interface.md)
- [Migration](Migration.md)
- [Backup and Restore](Backup_Restore.md)
- [Database Testing](Database_Testing.md)
