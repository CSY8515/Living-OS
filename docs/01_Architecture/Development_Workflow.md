# Living OS v1.7

# Standard Development Workflow

## Official Workflow

Requirement

↓

Architecture

↓

MASTER DESIGN

↓

Structure

↓

Roadmap

↓

Implementation

↓

Validation

↓

Testing

↓

Codex Review

↓

User Approval

↓

GitHub Commit

↓

GitHub Push

↓

GitHub Release

↓

Streamlit Deploy

↓

Stable Verification

↓

Archive

↓

Next Version

## Requirement

사용자 요구사항을 정의한다.

기록 항목:

- 목적
- 문제
- 기대 결과
- 범위
- 제외 범위
- 우선순위
- 위험
- 완료 조건

## Architecture

기존 공유 Architecture를 확인하고 새 요구사항이 위치할 계층을 결정한다.

검토 항목:

- Capability
- Module
- Subsystem
- Engine Group
- Engine
- Function
- Shared Foundation
- Dependency
- Data Flow
- Execution Flow

## MASTER DESIGN

확정 Architecture를 기반으로 공식 구현 기준을 작성한다.

MASTER DESIGN은 해당 Version의 Single Source of Truth이다.

## Structure

Repository, Directory, Package, Module, Database, Document 구조를 확정한다.

## Roadmap

Implementation 순서와 Milestone을 정의한다.

Roadmap은 기능 나열이 아니라 의존성과 위험을 고려한 실행 순서이다.

## Implementation

확정 문서를 기준으로 구현한다.

Implementation 중 Architecture 변경이 필요하면 임의로 변경하지 않고 Architecture 단계로 되돌아간다.

## Validation

구현 결과가 Requirement와 Architecture를 충족하는지 확인한다.

검증 항목:

- Input
- Output
- Validation
- Error Handling
- Database Integrity
- Execution Record
- Security
- Permission
- Rollback

## Testing

필수 테스트:

- Unit Test
- Integration Test
- Regression Test
- Migration Test
- Backup Test
- Restore Test
- Failure Test
- Permission Test
- Performance Test

## Codex Review

Codex Review에서는 다음을 확인한다.

- Architecture 준수
- Code Quality
- Security
- Error Handling
- Test Coverage
- Data Integrity
- Documentation 일치
- 불필요한 중복
- 위험한 변경

## User Approval

Release 전 사용자의 최종 승인을 받는다.

사용자 승인 없이 공식 Stable Release로 확정하지 않는다.

## GitHub Operations

User Approval

↓

GitHub Commit

↓

GitHub Push

↓

GitHub Release

Commit은 변경 목적이 명확해야 한다.

Release에는 Version, 변경사항, Migration, Known Issues, Rollback 정보를 포함한다.

## Streamlit Deploy

Release 완료 후 Streamlit에 배포한다.

배포 환경과 Repository Release 상태가 일치해야 한다.

## Stable Verification

배포 후 다음을 확인한다.

- App 실행
- 주요 기능
- Database 연결
- Migration 상태
- Error Log
- Performance
- Mobile / Desktop 접근
- Version 표시
- Rollback 가능성

## Archive

Release 문서, 검토 결과, 테스트 결과, Decision, Migration 기록을 Archive한다.

## Next Version

현재 Version의 완료 조건이 충족된 후 다음 Version으로 이동한다.

## Optimization Principle

빠른 개발은 단계 생략을 의미하지 않는다.

최적화 대상:

- 중복 문서 제거
- 반복 작업 자동화
- 공통 Template 사용
- Shared Foundation 재사용
- Test 자동화
- Release 자동화
- 대형 단위 작업
- 불필요한 확인 질문 제거

최적화 금지 대상:

- Safety
- Validation
- Testing
- Backup
- Restore
- User Approval
- Data Integrity
- Audit
- Rollback
