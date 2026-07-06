# Living OS v0.2 Core

Living OS v0.2 Core는 매일 실제로 사용할 수 있는 개인 운영 시스템을 목표로 하는 Python + Streamlit 기반 로컬 앱입니다.

v0.2는 v0.1을 폐기한 새 프로젝트가 아닙니다. v0.1의 Streamlit 구조, JSON 저장 구조, Dashboard, Report System, README, 기존 데이터 자산을 기반으로 Core 기능을 정리하고 확장한 버전입니다.

## v0.2 목표

Living OS v0.2의 목표는 “실제로 매일 사용하는 Core Operating System”입니다.

이번 버전에서는 AI 추천, 자동화, 캐릭터, 루틴, 알림, Expansion Pack, 실제 Vehicle/Food/Finance OS 구현은 제외합니다. 대신 매일 기록하고, 결정하고, 보고서를 만들고, 검색하고, 백업할 수 있는 핵심 구조를 완성합니다.

## 실행 방법

```powershell
pip install -r requirements.txt
streamlit run app.py
```

필요한 JSON/JSONL 파일은 실행 시 자동 생성됩니다.

## 프로젝트 구조

```text
living-os-mvp-skeleton/
├── app.py
├── README.md
├── ROADMAP.md
├── KNOWN_ISSUES.md
├── requirements.txt
├── backups/
├── config/
│   └── module_registry.json
├── data/
│   ├── archive.json
│   ├── daily_logs.json
│   ├── finance_budget.json
│   └── housing_candidates.json
├── logs/
│   └── decision_log.jsonl
├── modules/
│   ├── archive.py
│   ├── daily_log.py
│   ├── dashboard.py
│   ├── decision_log.py
│   ├── finance.py
│   ├── formatting.py
│   ├── housing.py
│   ├── module_manager.py
│   ├── report_system.py
│   ├── settings.py
│   └── storage.py
├── reports/
│   └── report_index.json
├── state/
│   └── settings.json
├── dummy/
├── profile/
└── rules/
```

## 구현 기능

### Dashboard

- 오늘 날짜와 상태
- 오늘 Daily Log 수
- 최근 Daily Log
- 최근 Decision
- 최근 Report
- 재검토 가능한 Decision 수

### Daily Log

- 일지 작성
- 날짜 저장
- 태그 저장
- 오늘 상태 저장
- JSON 저장
- 최근 일지 조회

저장 파일:

```text
data/daily_logs.json
```

### Decision Log

- 결정 기록
- 이유 기록
- 예상 결과
- 실제 결과
- 재검토 메모
- 상태 관리
- JSONL 저장

저장 파일:

```text
logs/decision_log.jsonl
```

### Report System

- 일일 보고서
- 주간 보고서
- 월간 보고서
- 복붙 가능한 텍스트 출력
- Markdown 파일 저장

저장 위치:

```text
reports/
```

### Archive

- JSON 기반 아카이브 저장
- 제목, 내용, 출처, 태그 저장
- 검색
- 조회

저장 파일:

```text
data/archive.json
```

### Module Manager

현재 버전에서는 실제 확장 모듈을 구현하지 않습니다.

대신 향후 다음 모듈을 쉽게 추가할 수 있도록 레지스트리 구조만 제공합니다.

- Vehicle OS
- Food OS
- Finance OS
- Health OS
- Housing OS
- Learning OS

저장 파일:

```text
config/module_registry.json
```

### Settings

- 기본 설정
- 데이터 파일 상태 확인
- 백업 생성
- 백업 JSON 복원

저장 위치:

```text
state/settings.json
backups/
```

## v0.1에서 유지한 자산

- Streamlit 기반 구조
- JSON / JSONL 저장 방식
- Dashboard 기본 구조
- Report System 개념
- README / Roadmap / Known Issues 문서 체계
- 기존 `finance.py`, `housing.py` 구현 파일
- 기존 Finance / Housing 데이터 파일

Finance와 Housing은 v0.2 메뉴에서는 제외되어 있지만, 향후 Finance OS / Housing OS로 승격할 수 있는 자산으로 보존합니다.

## v0.2에서 정리한 것

- Dummy Data Generator UI 제거
- Dummy Generator 코드 제거
- 더미 샘플 데이터 제거
- v0.2 Core 메뉴로 단순화
- Report System을 일일/주간/월간 보고서 중심으로 재구성
- Module Manager 추가
- Settings / Backup / Restore 추가

## 이번 버전에서 제외한 기능

- AI Recommendation
- AI Decision Engine
- Automation
- Character
- Habit
- Routine
- Notification
- Expansion Pack
- 실제 Vehicle OS
- 실제 Food OS
- 실제 Finance OS

## 현재 버전

```text
Living OS v0.2 Core
```

이 버전은 GitHub Release 및 Streamlit 배포를 목표로 정리 중인 Core 버전입니다.
