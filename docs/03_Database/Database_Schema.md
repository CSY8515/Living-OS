# Living OS v1.7 Database Schema Standard

## Purpose

본 문서는 Living OS Database Schema의 설계, 등록, Version 변경과 호환성 기준을 정의한다. 개별 Module의 업무 Entity 목록이나 세부 Column은 해당 Module MASTER DESIGN에서 정의한다.

## Schema Ownership

모든 Schema는 하나의 Data Owner를 가진다.

- Schema Key: `Module ID + Entity Type + Schema Version`
- Owner Module만 Schema 변경을 제안한다.
- Database Subsystem은 Schema 등록·Validation·Migration 실행을 담당한다.
- Information Management는 Metadata와 관계를 사용하지만 저장 Schema의 Owner가 아니다.

## Required Definition

각 Entity Schema는 최소한 다음을 정의한다.

- Schema ID
- Owner Module
- Entity Type
- Schema Version
- Purpose
- Field 이름과 Data Type
- Required와 Default
- Validation Rule
- Primary Key
- Unique·Foreign Key·Check Constraint
- Index
- Privacy Classification
- Retention과 Archive
- Created At과 Updated At
- Status와 Record Version
- Migration Reference

## Common Field Policy

공유 Standard가 더 엄격한 기준을 정의하지 않는 한 다음 개념을 지원한다.

| Concept | Requirement |
| --- | --- |
| ID | Entity 범위에서 안정적이고 고유해야 함 |
| Version | Schema Version과 Record Version을 구분해야 함 |
| Status | 승인된 상태 집합만 허용 |
| Created At | 생성 시각을 변경하지 않음 |
| Updated At | 변경 시각을 UTC 기준으로 갱신 |
| Owner | Data Owner 또는 소유 범위를 식별 |
| Tags | 검색용이며 업무 무결성 기준으로 사용하지 않음 |

Timestamp 표현, ID 형식과 Status 값은 OS Ecosystem Shared Database Standard를 우선한다.

## Version Rules

- Schema Version은 단조 증가한다.
- 호환 변경과 비호환 변경을 분류한다.
- 기존 Field 의미를 조용히 바꾸지 않는다.
- Rename은 명시적 Mapping을 가진다.
- 제거는 Deprecated 기간과 Migration을 거친다.
- Schema 변경은 Code·Docs·Migration·Test Version과 함께 Release한다.

## Integrity Rules

- Database가 보장할 수 있는 무결성은 Constraint로 표현한다.
- 업무 규칙은 Module Validation에 위치하며 Database Constraint와 충돌하지 않는다.
- Foreign Key는 소유권과 삭제 정책을 명시한다.
- Referential Integrity가 없는 외부 Reference는 Type과 Owner를 Metadata로 추적한다.
- JSON Payload는 등록된 Schema Validator를 통과해야 한다.
- 무결성 실패는 부분 Write 없이 Error Standard에 따라 기록한다.

## Index Rules

Index는 실제 Query와 측정 결과를 근거로 추가한다.

- Primary·Unique Constraint에 필요한 Index
- 빈번한 Filter·Join·Sort에 필요한 Index
- Write 비용과 저장 용량 영향
- 개인정보 노출과 검색 권한 영향
- 추가·제거 Migration과 Rollback

사용되지 않는 Index를 관성적으로 유지하지 않으며, Database Management는 변경을 직접 적용하지 않고 제안과 근거를 생성한다.

## Implemented Schema

Foundation Schema Registry는 `(module_id, entity_type, version)`으로 Validator를 등록한다. Schema v2는 기존 Table을 보존하고 다음을 추가한다.

Schema v3는 component registration 및 Execution 조회 Index를 추가하고, 등록 계약을 canonical `RecordRepository`의 `component_registration` record로 관리한다. 각 도메인 Schema의 실제 version은 해당 `*_meta` Table에서 읽어 선언 version과 비교한다.

- `records`: `status`, `owner`, `source`, `archived_at`, `correlation_id`
- `database_migrations`
- `execution_records`
- `backup_history`
- `restore_history`
- `ix_records_status`, `ix_records_updated`
- `ix_execution_status`, `ix_execution_action`

기존 system metadata, canonical records, domain events, audit entries, relationships, module states, documents, migration runs, projection checkpoints, paired devices는 삭제하거나 이름을 변경하지 않는다.

## Change Procedure

`Requirement → Owner Review → Schema Design → Migration Design → Backup/Restore Review → Test Plan → User Approval → Implementation`

Level 3 구조 변경으로 분류되는 Schema 변경은 Design Review와 User Approval을 요구한다.

## Acceptance Criteria

- Data Owner와 Schema Version이 명확함
- Constraint와 업무 Validation 책임이 분리됨
- Migration·Rollback·Backup 영향이 문서화됨
- 개인정보, Retention, Archive 기준이 정의됨
- 기존 데이터와 신규 데이터가 같은 Validator를 통과함
- Query 근거 없이 Index를 추가하지 않음

## Related Documents

- [Migration](Migration.md)
- [Database Metadata](Database_Metadata.md)
- [Database Interface](Database_Interface.md)
- [Database Testing](Database_Testing.md)
