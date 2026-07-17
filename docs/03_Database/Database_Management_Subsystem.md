# Living OS v1.7 Database Management Subsystem

## Purpose

Database Management Subsystem은 Database의 운영 상태를 관찰하고 유지보수·복구 작업을 조정하는 관리 전용 Subsystem이다. 업무 데이터의 의미와 소유권은 변경하지 않는다.

## Responsibility

- Database Health Monitor
- Performance Monitor
- Capacity Monitor
- Database Operational Analytics
- Index·Query Optimization 제안
- 승인된 Cleanup 실행
- Maintenance 일정과 상태 관리
- Recovery 조정
- Operational Statistics 생성

## Prohibited Responsibilities

- 업무 데이터 값을 임의로 변경하지 않는다.
- Owner Module의 Validation을 우회하지 않는다.
- 승인되지 않은 Schema나 Index를 적용하지 않는다.
- 관찰 결과를 근거로 자동 영구 삭제하지 않는다.
- Information Management의 분류·Knowledge Asset 책임을 대신하지 않는다.

## Control-plane Boundary

Database Management는 일반 CRUD 요청의 필수 중간 계층이 아니다.

- Data plane: `Module → Database Interface → Database Subsystem`
- Control plane: `Monitor → Analysis → Recommendation → Approval/Rule → Maintenance Interface`

관찰과 변경을 분리한다. Monitor는 상태를 측정하고, 변경은 Permission·Validation·Execution Record·Rollback을 갖춘 Maintenance 작업으로 수행한다.

## Health Model

최소 Health 상태:

- `HEALTHY`: 모든 필수 검사 통과
- `DEGRADED`: 서비스는 가능하지만 성능·용량·지연 위험 존재
- `UNHEALTHY`: 필수 기능 실패 또는 Integrity 위험 존재
- `RECOVERING`: 승인된 복구 절차 실행 중
- `UNKNOWN`: 최근 검사 결과 없음

Health 판단에는 검사 시각, 대상 Database Version, 검사 항목, 측정값, 임계값과 근거 Execution ID를 포함한다.

## Monitoring Scope

| Area | Example signals |
| --- | --- |
| Health | connection, integrity, transaction, migration state |
| Performance | query latency, transaction duration, lock wait |
| Capacity | database size, free space, record growth, backup size |
| Reliability | failure rate, retry rate, restore readiness |
| Maintenance | stale data candidates, index status, last optimization |

임계값은 코드에 고정하지 않고 Configuration을 통해 Version 관리한다.

## Maintenance and Recovery

모든 변경 작업은 다음 흐름을 따른다.

`Detection → Analysis → Recommendation → Permission/Approval → Backup → Execution → Validation → Report`

위험 작업은 중지·수동 전환·Rollback이 가능해야 한다. Recovery는 [Backup and Restore](Backup_Restore.md)의 검증된 절차만 호출한다.

## Execution Integration

Monitor 결과와 Maintenance 작업은 공통 Execution Database에 기록한다.

- 상태 측정은 원본 업무 데이터를 포함하지 않는다.
- 변경 작업은 이전·이후 상태 참조와 승인 근거를 가진다.
- Error는 recoverable, retryable, severity와 Trace ID를 포함한다.
- Alert·Report는 원 Execution ID를 참조한다.

## Actual Implementation and Deferred Scope

공식 facade는 `subsystems/database_management/subsystem.py`의 `DatabaseManagementSubsystem`이다. `engines/health.py`는 연결, 파일, Schema, Migration, Integrity, Backup, Restore, 검사 시간과 Capacity 상태를 읽고, `engines/report.py`는 권장 조치가 포함된 운영 보고를 생성한다.

Settings는 상태 조회, 명시적 Migration, 기록되는 Health Check, Backup, Restore candidate와 승인, Report 생성을 제공한다. 연속 Background Monitor, 자동 Optimization, 자동 Cleanup, 분산 Capacity 관리와 자동 Recovery orchestration은 v1.7 범위에서 제외한다.

## Acceptance Criteria

- Database Subsystem의 업무 데이터 책임을 침범하지 않음
- Health 상태와 판정 근거를 추적할 수 있음
- Performance·Capacity 측정 단위와 임계값이 Version 관리됨
- Maintenance 전에 Backup·Permission·Rollback을 확인함
- Recovery 결과가 Validation과 Report로 연결됨
- Monitor 장애가 Database CRUD를 불필요하게 차단하지 않음

## Related Documents

- [Database Subsystem](Database_Subsystem.md)
- [Backup and Restore](Backup_Restore.md)
- [Database Workflow](Database_Workflow.md)
- [Database Testing](Database_Testing.md)
- [Database Roadmap](Database_Roadmap.md)
