# Known Issues

## Living OS v0.7

### Review Workspace limitations

- Review is read-only and does not edit source records.
- Date-range filters exclude records whose existing date fields are missing or malformed.
- Recent Report ordering and filtering use each report file's local modification time.
- Decision review is limited to the existing `draft`, `active`, and `review` statuses.
- No existing JSON or JSONL schema was changed for v0.7.

The local single-user, JSON/JSONL, backup, and intentionally excluded feature limitations documented below remain applicable.

## Historical v0.2 notes

Living OS v0.2 Core의 현재 한계와 의도적으로 제외한 기능을 정리합니다.

## 현재 한계

### 1. 로컬 단일 사용자 앱

현재 Living OS는 로컬에서 한 명의 사용자가 실행하는 Streamlit 앱입니다.

미구현:

- 로그인
- 사용자 계정
- 권한 관리
- 팀 공유

### 2. JSON / JSONL 저장

현재는 JSON과 JSONL 파일을 사용합니다.

장점:

- 단순함
- 백업이 쉬움
- GitHub에서 구조 확인이 쉬움

한계:

- 동시 편집에 약함
- 대용량 검색에 적합하지 않음
- 복잡한 관계형 질의가 어려움

### 3. Finance / Housing은 v0.2 메뉴에서 제외

v0.1의 Finance와 Housing 구현 파일은 보존되어 있습니다.

하지만 v0.2 Core에서는 실제 Finance OS, Housing OS를 구현하지 않습니다.

이 기능들은 향후 모듈화 버전에서 정리합니다.

### 4. Module Manager는 구조만 제공

Module Manager는 향후 모듈을 추가하기 위한 레지스트리입니다.

현재는 실제 Vehicle OS, Food OS, Finance OS 등을 구현하지 않습니다.

### 5. AI 기능 없음

v0.2에서는 AI 기능을 넣지 않습니다.

미구현:

- AI Recommendation
- AI Decision Engine
- 자동 판단
- 자동 요약
- 자동 분류

### 6. 자동화 없음

현재 제외:

- Automation
- Notification
- Routine
- Habit
- Character

### 7. Backup / Restore는 기본형

Settings에서 백업 JSON을 만들고 복원할 수 있습니다.

현재 한계:

- 전체 파일 시스템 백업은 아님
- 첨부파일 백업 없음
- 충돌 감지 없음
- 복원 전 상세 diff 없음

## 공개 전 확인할 점

- `streamlit run app.py` 실행 확인
- `requirements.txt` 기준 의존성 설치 확인
- 샘플 개인 데이터 제거
- `__pycache__` 제외
- 실제 민감 정보가 JSON에 없는지 확인

## 의도적으로 제외한 기능

| 기능 | 상태 |
| --- | --- |
| AI Recommendation | 제외 |
| AI Decision Engine | 제외 |
| Automation | 제외 |
| Character | 제외 |
| Habit | 제외 |
| Routine | 제외 |
| Notification | 제외 |
| Expansion Pack | 제외 |
| 실제 Vehicle OS | 제외 |
| 실제 Food OS | 제외 |
| 실제 Finance OS | 제외 |

## 결론

Living OS v0.2 Core는 완성형 자동화 플랫폼이 아니라, 매일 기록하고 결정하고 보고서를 만드는 Core OS입니다.

현재 목표는 안정적인 Core 구조를 완성하는 것입니다.
