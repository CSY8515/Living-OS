# Living OS v1.7 Database Metadata Standard

## Purpose

본 문서는 Database 구성요소, Schema, Record와 운영 실행을 식별하고 추적하기 위한 공통 Metadata 기준을 정의한다. 업무 Entity의 고유 Field는 각 Module Schema에서 정의한다.

## Metadata Layers

| Layer | Purpose |
| --- | --- |
| Component Metadata | Subsystem·Engine·Interface 식별 |
| Schema Metadata | Data Owner, Entity, Schema Version과 Validation 추적 |
| Record Metadata | 개별 Record의 상태·Version·시간·소유권 추적 |
| Execution Metadata | Database 작업의 시작·결과·오류 추적 |
| Operational Metadata | Health·Performance·Capacity 측정 근거 추적 |

## Common Metadata

모든 주요 자산은 다음 공통 항목을 고려한다.

- ID
- Name 또는 Title
- Type
- Parent
- Version
- Status
- Created At
- Updated At
- Owner
- Tags
- Source
- Documentation Reference

## Record Metadata

최소 항목:

- Record ID
- Owner Module
- Entity Type
- Record Version
- Schema Version
- Status
- Privacy Class
- Created At
- Updated At
- Created By 또는 Source
- Soft Deleted At, 해당 시
- Retention Class

Tags는 선택적 검색 Metadata이며 권한, 소유권 또는 무결성 판단을 대체하지 않는다.

## Execution Metadata

Database 관련 주요 실행은 다음을 기록한다.

- Execution ID
- Trace ID
- Source System
- Capability
- Module
- Subsystem
- Engine
- Function
- Operation
- Input Reference
- Output Reference
- Status
- Started At
- Completed At
- Duration
- Error Reference
- Product Version
- Schema Version

Input·Output Reference는 원문 복제가 아니라 안전한 Record·Document·Backup·Migration Reference를 사용한다.

## Migration Metadata

- Migration ID
- Source Version과 Target Version
- Input Checksum
- Backup Reference
- Dry-run Result Reference
- Approval Reference
- Accepted·Rejected·Quarantined Count
- Rollback Reference
- Execution ID

## Backup Metadata

- Backup ID
- Format Version
- Product·Schema Version
- Source Reference
- Created At과 Created By
- Manifest Reference
- Checksum
- Size
- Verification Status
- Retention Class
- Encryption 또는 Protection Status
- Restore Test Reference

## Operational Metadata

- Measurement ID
- Database Reference
- Metric Name과 Unit
- Value
- Threshold Version
- Health Status
- Measured At
- Collector Version
- Execution ID

## Time, ID and Status Rules

- Timestamp는 공유 Timestamp Standard를 따르고 하나의 시간 기준을 사용한다.
- ID는 생성 후 변경하지 않는다.
- Schema Version과 Record Version을 혼합하지 않는다.
- Status는 승인된 상태 전이만 허용한다.
- Source는 원본 또는 생성 Execution까지 추적 가능해야 한다.
- Metadata 변경도 필요한 경우 Audit과 Version을 가진다.

## Privacy and Logging

- Secret, API Key, Password, Token은 Metadata에 저장하지 않는다.
- 개인정보 원문을 Tags, Error, Trace에 복제하지 않는다.
- Privacy Class와 Permission은 Metadata 조회에도 적용한다.
- Analytics에는 필요한 최소 식별자와 집계값만 전달한다.

## Validation

- 필수 Metadata 누락 거부
- Owner·Parent Reference 유효성 검사
- Version 형식과 상태 전이 검사
- Created At 불변성 검사
- Updated At 단조성 검사
- Execution ID·Trace ID 형식 검사
- 민감정보 패턴 검사

## Related Documents

- [Database Schema](Database_Schema.md)
- [Database Interface](Database_Interface.md)
- [Migration](Migration.md)
- [Backup and Restore](Backup_Restore.md)
