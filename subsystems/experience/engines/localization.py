from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any, Callable


UI_TEXT: dict[str, str] = {
    # Primary navigation and products
    "Command Center": "대시보드", "Dashboard": "대시보드", "Daily Log": "일일 기록",
    "Decision Log": "결정 기록", "Reports": "리포트", "Archive": "보관함",
    "Analytics": "분석", "Timeline": "타임라인", "Global Timeline": "통합 타임라인",
    "Search": "검색", "Global Search": "통합 검색", "Review": "검토",
    "AI Analysis": "AI 분석", "AI Briefing": "AI 브리핑", "Documents": "문서",
    "Finance": "재무", "Food": "식사", "Health": "건강", "Housing": "주거",
    "Vehicle": "차량", "Knowledge": "지식", "Routine": "루틴",
    "Investment": "투자", "Job": "직업", "Personal Growth": "자기계발",
    "Collaboration": "협업", "Database": "데이터베이스", "Module Manager": "모듈 관리",
    "Settings": "설정", "Investment Management": "투자 관리", "Job Management": "직업 관리",
    "Knowledge Management": "지식 관리", "Routine Management": "루틴 관리",
    "Personal Growth Management": "자기계발 관리", "Growth Management": "자기계발 관리",
    "Collaboration Management": "협업 관리", "Database Management": "데이터베이스 관리",
    "Database Contract": "데이터베이스 계약", "Settings / Hub Administration": "설정 / 허브 관리",
    "Journal": "일지", "Decision": "결정",

    # Shared controls
    "Menu": "메뉴", "Record Browser": "기록 탐색기", "Search all records": "모든 기록 검색",
    "Search Jobs": "직업 기록 검색", "Search Knowledge": "지식 검색", "Search": "검색",
    "Status": "상태", "Sort": "정렬", "Sort by": "정렬 기준", "Order": "정렬 순서",
    "Descending": "내림차순", "Detail": "상세 보기", "Detail view": "상세 보기",
    "Result detail": "결과 상세", "From": "시작일", "To": "종료일",
    "Subsystem": "하위 시스템", "Category": "분류", "Report Type": "리포트 유형",
    "Report range": "리포트 기간", "Report date / week ending": "리포트 기준일 / 주간 종료일",
    "Report month": "리포트 월", "Select record": "기록 선택", "OpenAI Model": "OpenAI 모델",
    "Title": "제목", "Name": "이름", "Description": "설명", "Content": "내용",
    "Summary": "요약", "Notes": "메모", "Note": "메모", "Source": "출처",
    "Tags": "태그", "Kind": "유형", "Privacy": "공개 범위", "Date": "날짜",
    "Month": "월", "Amount": "금액", "Currency": "통화", "Quantity": "수량",
    "Current Price": "현재 가격", "Unit Cost": "단가", "Asset Type": "자산 유형",
    "Symbol": "종목 코드", "Company": "회사", "Employment Type": "고용 형태",
    "Location": "근무지", "Frequency": "주기", "Interval days": "반복 간격(일)",
    "Priority": "우선순위", "Progress": "진행률", "Reflection": "회고",
    "Next action": "다음 행동", "Purpose": "목적", "Growth area": "성장 영역",
    "Goal title": "목표 제목", "Partner / team": "파트너 / 팀",
    "Shared objective": "공동 목표", "Coordination notes": "협업 메모",
    "App Name": "앱 이름", "Default Report Range": "기본 리포트 기간",
    "OpenAI API Key": "OpenAI API 키", "New owner passphrase": "새 소유자 암호문",
    "Confirm owner passphrase": "소유자 암호문 확인", "Confirm passphrase": "암호문 확인",
    "Owner passphrase": "소유자 암호문", "Device name": "기기 이름",
    "Component database": "구성요소 데이터베이스", "Verified component restore candidate": "검증된 구성요소 복원 후보",
    "Verified restore candidate": "검증된 복원 후보", "Lifecycle action": "수명주기 작업",
    "Choose a document": "문서 선택", "Promotion reason": "승격 사유", "Review note": "검토 메모",
    "Review status": "검토 상태", "Update status": "상태 변경", "Decision": "결정",
    "Reason": "이유", "Expected Result": "예상 결과", "Actual Result": "실제 결과",
    "Journal Entry": "일지 내용", "Transaction type": "거래 유형", "Budget category": "예산 분류",
    "Budget amount": "예산 금액", "Savings type": "저축 유형", "Savings name": "저축 이름",
    "Target or principal": "목표액 또는 원금", "Monthly contribution": "월 납입액",
    "Annual interest rate (%)": "연이율(%)", "Opened on": "개설일", "Maturity date": "만기일",
    "Measured on": "측정일", "Weight (kg)": "체중(kg)", "Weight note": "체중 메모",
    "Weight record to manage": "관리할 체중 기록", "Corrected date": "수정 날짜",
    "Corrected weight (kg)": "수정 체중(kg)", "Corrected note": "수정 메모",
    "InBody date": "인바디 측정일", "Skeletal muscle (kg)": "골격근량(kg)",
    "Body fat (%)": "체지방률(%)", "Checkup date": "건강검진일", "Checkup title": "건강검진 제목",
    "Assessment": "소견", "Follow-up required": "추적 확인 필요", "Follow-up date": "추적 확인일",
    "Metrics (optional JSON object)": "측정값(선택, JSON 객체)", "Checkup note": "건강검진 메모",
    "Bedtime (ISO with timezone)": "취침 시각(시간대 포함 ISO)", "Wake time (ISO with timezone)": "기상 시각(시간대 포함 ISO)",
    "Exercise date": "운동일", "Activity": "활동", "Duration (minutes)": "운동 시간(분)",
    "Repetitions (optional)": "반복 횟수(선택)", "Exercise note": "운동 메모",
    "Meal date": "식사일", "Health meal type": "건강 식사 유형", "Nutrition note": "영양 메모",
    "Related Health goal (optional)": "연결할 건강 목표(선택)", "Goal name": "목표 이름",
    "Target weight (kg)": "목표 체중(kg)", "Target body fat (%)": "목표 체지방률(%)",
    "Candidate name": "후보 이름", "Deposit": "보증금", "Monthly rent": "월세",
    "Maintenance fee": "관리비", "Maintenance fee is known": "관리비 확인됨",
    "Commute minutes": "통근 시간(분)", "Parking available": "주차 가능",
    "Options memo": "선택사항 메모", "Special notes": "특이사항",
    "Candidate to manage": "관리할 주거 후보", "Contract name": "계약 이름",
    "Contract address": "계약 주소", "Contract start": "계약 시작일", "Contract end": "계약 종료일",
    "Contract deposit": "계약 보증금", "Monthly maintenance": "월 관리비", "Charge contract": "비용 계약",
    "Charged on": "비용 발생일", "Charge type": "비용 유형", "Charge amount": "비용 금액",
    "Vehicle name": "차량 이름", "Manufacturer": "제조사", "Model": "모델", "Model year": "연식",
    "Powertrain": "동력원", "Vehicle to archive": "보관할 차량", "Vehicle to restore": "복원할 차량",
    "Vehicle": "차량", "Odometer (km)": "주행거리(km)", "Recorded on": "기록일",
    "Service type": "정비 유형", "Serviced on": "정비일", "Service odometer (km)": "정비 시 주행거리(km)",
    "Service cost": "정비 비용", "Provider": "정비처", "Service note": "정비 메모",
    "Scheduled service": "예정 정비", "Use due date": "예정일 사용", "Due on": "예정일",
    "Use due odometer": "예정 주행거리 사용", "Due odometer (km)": "예정 주행거리(km)",
    "Schedule to complete": "완료할 정비 일정", "Completion record": "완료 기록",
    "Energy type": "연료/에너지 유형", "Energy date": "주유/충전일", "Quantity (L or kWh)": "수량(L 또는 kWh)",
    "Energy cost": "주유/충전 비용", "Energy odometer (km)": "주유/충전 시 주행거리(km)",
    "Energy note": "주유/충전 메모", "Report vehicle": "리포트 차량", "Trip vehicle": "운행 차량",
    "Driven on": "운행일", "Start odometer": "출발 주행거리", "End odometer": "도착 주행거리",
    "Trip purpose": "운행 목적", "Ingredient name": "식재료 이름", "Base quantity": "기준 수량",
    "Base unit": "기준 단위", "Calories": "열량", "Protein": "단백질", "Carbohydrate": "탄수화물",
    "Fat": "지방", "Ingredient to archive": "보관할 식재료", "Ingredient to restore": "복원할 식재료",
    "Recipe name": "레시피 이름", "Recipe servings": "레시피 인분", "Instructions": "조리 방법",
    "Recipe": "레시피", "Ingredient": "식재료", "Ingredient quantity": "식재료 수량",
    "Ingredient unit": "식재료 단위", "Recipe to restore": "복원할 레시피", "Cooked recipe": "조리한 레시피",
    "Cooked on": "조리일", "Servings produced": "조리 인분", "Cooking note": "조리 메모",
    "Eaten on": "섭취일", "Meal type": "식사 유형", "Meal recipe (optional)": "식사 레시피(선택)",
    "Servings consumed": "섭취 인분", "Meal note": "식사 메모",

    # Actions
    "Add": "추가", "Create": "생성", "Save": "저장", "Restore": "복원", "Archive": "보관",
    "Update": "수정", "Delete": "삭제", "Close month": "월 마감", "Schedule": "일정 등록",
    "Pause": "일시정지", "Complete": "완료", "Skip": "건너뛰기", "Revoke": "해제",
    "Save Valuation": "평가액 저장", "Save Status": "상태 저장", "Save progress": "진행률 저장",
    "Save collaboration": "협업 저장", "Create goal": "목표 생성", "Growth portfolio": "성장 포트폴리오",
    "New collaboration": "새 협업", "Active work": "진행 중인 협업", "Create collaboration": "협업 생성",
    "Add Investment": "투자 추가", "Add Job": "직업 기록 추가", "Create Knowledge": "지식 생성",
    "Create Routine": "루틴 생성", "Save Journal Entry": "일지 저장", "Save Decision": "결정 저장",
    "Save Decision Revision": "결정 수정 저장", "Save Knowledge Item": "지식 항목 저장",
    "Promote Reviewed Knowledge": "검토된 지식 승격", "Save Report": "리포트 저장",
    "Generate AI Report Draft": "AI 리포트 초안 생성", "Save AI Draft (Explicit Approval)": "AI 초안 저장(명시적 승인)",
    "Request Read-only Analysis": "읽기 전용 분석 요청", "Add Document": "문서 추가",
    "Apply Lifecycle Change": "수명주기 변경 적용", "Save Preferences": "환경설정 저장",
    "Enable Owner Security": "소유자 보안 활성화", "Run Migration Dry Run": "마이그레이션 사전 점검",
    "Create Verified Backup and Migrate": "검증 백업 생성 후 마이그레이션",
    "Apply Approved Database Migration": "승인된 데이터베이스 마이그레이션 적용",
    "Create and Verify Component Backup": "구성요소 백업 생성 및 검증",
    "Restore Selected Component Backup": "선택한 구성요소 백업 복원",
    "Initialize and Verify Component Schema": "구성요소 스키마 초기화 및 검증",
    "Run and Record Database Health Check": "데이터베이스 상태 점검 및 기록",
    "Create and Verify Database Backup": "데이터베이스 백업 생성 및 검증",
    "Restore Selected Database Backup": "선택한 데이터베이스 백업 복원",
    "Generate Database Management Report": "데이터베이스 관리 리포트 생성",
    "Run health check": "상태 점검 실행", "Create verified backup": "검증 백업 생성",
    "Record transaction": "거래 기록", "Create budget": "예산 생성", "Create savings account": "저축 계좌 생성",
    "Migrate legacy Finance budget": "기존 재무 예산 마이그레이션", "Record weight": "체중 기록",
    "Update weight record": "체중 기록 수정", "Delete incorrect weight record": "잘못된 체중 기록 삭제",
    "Record InBody": "인바디 기록", "Record health checkup": "건강검진 기록", "Record sleep": "수면 기록",
    "Record exercise": "운동 기록", "Record nutrition": "영양 기록", "Create Health goal": "건강 목표 생성",
    "Add candidate": "후보 추가", "Update status": "상태 수정", "Delete candidate": "후보 삭제",
    "Dry run legacy Housing migration": "기존 주거 데이터 마이그레이션 사전 점검",
    "Apply reviewed Housing migration": "검토된 주거 데이터 마이그레이션 적용",
    "Create rental contract": "임대차 계약 생성", "Record housing charge": "주거 비용 기록",
    "Add vehicle": "차량 추가", "Archive vehicle": "차량 보관", "Restore vehicle": "차량 복원",
    "Record odometer": "주행거리 기록", "Record maintenance": "정비 기록", "Create schedule": "정비 일정 생성",
    "Complete schedule": "정비 일정 완료", "Record fuel / charge": "주유 / 충전 기록", "Record trip": "운행 기록",
    "Add ingredient": "식재료 추가", "Archive ingredient": "식재료 보관", "Restore ingredient": "식재료 복원",
    "Add recipe": "레시피 추가", "Set as recipe ingredient": "레시피 식재료로 설정",
    "Restore recipe": "레시피 복원", "Record cooking": "조리 기록", "Record meal": "식사 기록",
    "Secure This Hub": "이 허브 보호", "Pair and Open Hub": "기기 연결 후 허브 열기",

    # Headings, metrics and sections
    "Total": "전체", "Active": "활성", "Archived": "보관됨", "Completed": "완료",
    "Executions": "실행", "Registry": "레지스트리", "Pipeline": "진행 단계", "Due Actions": "예정 작업",
    "Offers": "제안", "Accepted": "수락", "Execution Success": "실행 성공", "Execution Failure": "실행 실패",
    "Due": "예정", "Failed": "실패", "Best Streak": "최장 연속", "Average Progress": "평균 진행률",
    "Overdue": "기한 초과", "Blocked": "차단됨", "Components": "구성요소", "Integrity": "무결성",
    "Schema": "스키마", "Size": "크기", "Verified Backups": "검증된 백업", "Income": "수입",
    "Expense": "지출", "Net Cash Flow": "순현금흐름", "Budget Remaining": "남은 예산",
    "Results": "결과", "Subsystems": "하위 시스템", "Timeline events": "타임라인 이벤트",
    "Current": "현재", "Previous": "이전", "Growth": "증감", "12-month growth": "12개월 증감",
    "Activity": "활동", "Decisions Needing Review": "검토가 필요한 결정", "Environment": "실행 환경",
    "Durability": "내구성", "Backup": "백업", "Authentication": "인증",
    "Status overview": "상태 요약", "Recent activity": "최근 활동", "Recent Activity": "최근 활동",
    "Status history": "상태 이력", "Cross Subsystem Summary": "하위 시스템 종합 요약",
    "Monthly Summary": "월간 요약", "Yearly Summary": "연간 요약", "Health checkups": "건강검진",
    "Sleep": "수면", "Exercise": "운동", "Nutrition": "영양", "Health reports": "건강 리포트",
    "Trip log": "운행 기록", "Archived vehicles": "보관된 차량", "Archived ingredients": "보관된 식재료",
    "Archived recipes": "보관된 레시피", "Legacy Finance migration": "기존 재무 데이터 마이그레이션",
    "Rental contract and monthly charges": "임대차 계약 및 월별 비용", "Runtime Storage and Release Gate": "실행 저장소 및 릴리스 게이트",
    "Application Preferences": "앱 환경설정", "OpenAI Configuration": "OpenAI 설정",
    "Owner Security and Paired Devices": "소유자 보안 및 연결 기기", "Data Store Migration": "데이터 저장소 마이그레이션",
    "Core Status": "핵심 상태", "Optional AI Report Draft": "선택형 AI 리포트 초안",
    "Deterministic Report": "결정론적 리포트", "Unsaved AI Draft": "저장되지 않은 AI 초안",
    "Registered component databases": "등록된 구성요소 데이터베이스",

    # Empty, loading, success and guidance
    "No records yet.": "아직 기록이 없습니다.", "No investment records yet.": "아직 투자 기록이 없습니다.",
    "No job records match this view.": "현재 조건과 일치하는 직업 기록이 없습니다.",
    "No Knowledge records match this view.": "현재 조건과 일치하는 지식 기록이 없습니다.",
    "No routines yet.": "아직 루틴이 없습니다.", "No growth goals yet. Create a focused goal to start.": "아직 자기계발 목표가 없습니다. 집중할 목표를 만들어 시작해 보세요.",
    "No collaboration records yet.": "아직 협업 기록이 없습니다.", "No recent activity yet. Use a quick action to create your first record.": "아직 최근 활동이 없습니다. 빠른 실행으로 첫 기록을 만들어 보세요.",
    "No timeline activity matches these filters. Expand the date range or clear filters.": "필터와 일치하는 타임라인 활동이 없습니다. 기간을 늘리거나 필터를 해제해 보세요.",
    "No matching records. Try fewer words or remove a filter.": "일치하는 기록이 없습니다. 검색어를 줄이거나 필터를 해제해 보세요.",
    "No subsystem activity exists for this report period yet.": "이 리포트 기간에는 하위 시스템 활동이 없습니다.",
    "No saved reports yet. Generate and save a report when ready.": "아직 저장된 리포트가 없습니다. 준비되면 리포트를 생성하고 저장하세요.",
    "No data yet.": "아직 데이터가 없습니다.", "No trend data exists in this period.": "이 기간에는 추세 데이터가 없습니다.",
    "No canonical records are available.": "사용 가능한 공식 기록이 없습니다.", "Choose a document first.": "먼저 문서를 선택하세요.",
    "No component database contracts are registered yet.": "아직 등록된 구성요소 데이터베이스 계약이 없습니다.",
    "No registered database backup exists yet.": "아직 등록된 데이터베이스 백업이 없습니다.",
    "Add an active vehicle before recording Vehicle data.": "차량 데이터를 기록하려면 먼저 활성 차량을 추가하세요.",
    "Add an active vehicle before generating a status report.": "상태 리포트를 생성하려면 먼저 활성 차량을 추가하세요.",
    "Add an active vehicle first.": "먼저 활성 차량을 추가하세요.",
    "Add an active recipe before recording cooking linked to a recipe.": "레시피와 연결된 조리를 기록하려면 먼저 활성 레시피를 추가하세요.",
    "The start date cannot be after the end date.": "시작일은 종료일보다 늦을 수 없습니다.",
    "Passphrases do not match.": "암호문이 일치하지 않습니다.", "Owner authentication failed.": "소유자 인증에 실패했습니다.",
    "Explicit migration approval is required.": "명시적인 마이그레이션 승인이 필요합니다.",
    "Explicit component restore approval is required.": "구성요소 복원에 대한 명시적인 승인이 필요합니다.",
    "Explicit restore approval is required.": "복원에 대한 명시적인 승인이 필요합니다.",
    "Configure an OpenAI API key in Settings first.": "먼저 설정에서 OpenAI API 키를 구성하세요.",

    "Portfolio valuation by currency": "통화별 포트폴리오 평가액", "Status and asset allocation": "상태 및 자산 배분",
    "Include archived": "보관 기록 포함", "Active position": "활성 포지션", "Activate now": "지금 활성화",
    "Follow-up queue": "추적 확인 대기열", "Correction-only deletion": "오입력 정정 전용 삭제",
    "I reviewed the pending database migration and approve applying it.": "대기 중인 데이터베이스 마이그레이션을 검토했으며 적용을 승인합니다.",
    "I reviewed the dry run and approve backup plus migration.": "사전 점검 결과를 검토했으며 백업 및 마이그레이션을 승인합니다.",
    "I understand this permanently deletes the selected candidate.": "선택한 후보가 영구 삭제됨을 이해했습니다.",
    "I approve a safety backup and restore for this component database.": "이 구성요소 데이터베이스의 안전 백업 및 복원을 승인합니다.",
    "I approve a safety backup followed by restoring this verified database archive.": "안전 백업 후 검증된 데이터베이스 보관본 복원을 승인합니다.",
    "I confirm this weight entry is incorrect.": "이 체중 기록이 잘못 입력되었음을 확인합니다.",
    "Growth / Workspace": "자기계발 / 작업 공간", "Growth / Management": "자기계발 / 관리",
    "Collaboration / Workspace": "협업 / 작업 공간", "Collaboration / Management": "협업 / 관리",
    "System / Database": "시스템 / 데이터베이스", "System / Control Plane": "시스템 / 제어 영역",
    "Turn intentions into measurable progress and clear next actions.": "의도를 측정 가능한 진행과 명확한 다음 행동으로 연결합니다.",
    "Portfolio health, distribution, priorities, and data contract status.": "포트폴리오 상태, 분포, 우선순위와 데이터 계약 상태를 확인합니다.",
    "Coordinate partners, commitments, due dates, and blockers from one view.": "파트너, 약속, 기한과 차단 요인을 한 화면에서 조율합니다.",
    "Pipeline health, blockers, partner distribution, and control status.": "진행 단계 상태, 차단 요인, 파트너 분포와 제어 상태를 확인합니다.",
    "Execution Database, schema, registry, and integrity observability.": "실행 데이터베이스, 스키마, 레지스트리와 무결성을 관찰합니다.",
    "Health checks, verified backup readiness, restore safety, and operational reporting.": "상태 점검, 검증 백업 준비도, 복원 안전성과 운영 리포트를 관리합니다.",
    # Descriptions
    "Owner-managed investment positions and valuations. Values are grouped by currency.": "소유자가 관리하는 투자 포지션과 평가액입니다. 통화별로 구분해 표시합니다.",
    "Job opportunities, applications, interviews, offers, and next actions.": "채용 기회, 지원, 면접, 제안과 다음 행동을 관리합니다.",
    "Structured information, notes, learning material, ideas, and sources.": "구조화된 정보, 메모, 학습 자료, 아이디어와 출처를 관리합니다.",
    "Recurring personal, work, learning, and health routines.": "개인, 업무, 학습과 건강의 반복 루틴을 관리합니다.",
    "Daily operating records saved through explicit audited commands.": "명시적으로 감사되는 명령을 통해 일상 운영 기록을 저장합니다.",
    "Versioned decisions with evidence, review, outcomes, and audit.": "근거, 검토, 결과와 감사 이력이 있는 버전형 결정을 관리합니다.",
    "Notes, archive material, cases, and governed Living Rule promotion.": "메모, 보관 자료, 사례와 관리되는 생활 규칙 승격을 다룹니다.",
    "Search and filter activity across every connected subsystem.": "연결된 모든 하위 시스템의 활동을 검색하고 필터링합니다.",
    "One search surface for Timeline and connected subsystem records.": "타임라인과 연결된 하위 시스템 기록을 한 화면에서 검색합니다.",
    "Deterministic summaries built from existing data; no AI is required.": "기존 데이터로 생성하는 결정론적 요약이며 AI가 필요하지 않습니다.",
    "Read-only trend, comparison, monthly, yearly, and growth analysis.": "추세, 비교, 월간, 연간과 증감 분석을 읽기 전용으로 제공합니다.",
    "Human review queue derived from canonical records.": "공식 기록에서 생성한 사용자 검토 대기열입니다.",
    "Source-attributed, explicit, read-only AI analysis.": "출처가 표시되고 명시적으로 실행되는 읽기 전용 AI 분석입니다.",
    "Content-integrity foundation with versioned references and privacy classification.": "버전형 참조와 공개 범위를 갖춘 콘텐츠 무결성 기반입니다.",
    "Validated lifecycle and health; no future roadmap modules are installed.": "검증된 수명주기와 상태를 관리하며 향후 로드맵 모듈은 설치하지 않습니다.",
    "Explicit migration, backup, credentials, and storage status.": "명시적 마이그레이션, 백업, 인증 정보와 저장소 상태를 관리합니다.",
}

STATUS_TEXT = {
    "ALL": "전체", "ACTIVE": "활성", "ARCHIVED": "보관됨", "COMPLETED": "완료",
    "READY": "준비됨", "REGISTERED": "등록됨", "MISSING": "없음", "PENDING": "대기",
    "FAILED": "실패", "ERROR": "오류", "HEALTHY": "정상", "NORMAL": "정상",
    "ATTENTION": "확인 필요", "ONLINE": "온라인", "DEGRADED": "주의", "WARNING": "경고",
    "PAUSED": "일시정지", "PLANNED": "계획됨", "NEW": "신규", "REVIEW": "검토",
    "ORGANIZED": "정리됨", "DRAFT": "초안", "WATCHLIST": "관심 목록", "SAVED": "저장됨",
    "APPLIED": "지원함", "INTERVIEW": "면접", "OFFER": "제안", "ACCEPTED": "수락",
    "REJECTED": "거절", "WITHDRAWN": "철회", "BLOCKED": "차단됨", "UNKNOWN": "알 수 없음",
    "SUCCESS": "성공", "INFO": "안내", "OPEN": "열림", "CLOSED": "종료",
}

WORD_TEXT = {
    "management": "관리", "system": "시스템", "workspace": "작업 공간", "control": "제어",
    "plane": "영역", "growth": "성장", "collaboration": "협업", "personal": "개인",
    "database": "데이터베이스", "adapter": "어댑터", "status": "상태", "allocation": "배분",
    "portfolio": "포트폴리오", "valuation": "평가액", "currency": "통화", "pipeline": "진행 단계",
    "upcoming": "예정", "actions": "작업", "categories": "분류", "recent": "최근",
    "execution": "실행", "results": "결과", "record": "기록", "records": "기록",
    "browser": "탐색기", "detail": "상세", "view": "보기", "active": "활성",
    "archived": "보관됨", "restore": "복원", "archive": "보관", "create": "생성",
    "add": "추가", "save": "저장", "update": "수정", "delete": "삭제", "search": "검색",
    "report": "리포트", "summary": "요약", "monthly": "월간", "yearly": "연간",
    "timeline": "타임라인", "global": "통합", "category": "분류", "subsystem": "하위 시스템",
    "activity": "활동", "current": "현재", "previous": "이전", "total": "전체",
    "owner": "소유자", "security": "보안", "device": "기기", "migration": "마이그레이션",
    "backup": "백업", "verified": "검증됨", "component": "구성요소", "integrity": "무결성",
    "health": "건강", "finance": "재무", "food": "식사", "housing": "주거", "vehicle": "차량",
    "knowledge": "지식", "routine": "루틴", "investment": "투자", "job": "직업",
    "module": "모듈", "settings": "설정", "application": "앱", "preferences": "환경설정",
    "optional": "선택", "required": "필수", "available": "사용 가능", "first": "먼저",
    "selected": "선택한", "open": "열기", "close": "닫기", "empty": "비어 있음",
    "loading": "불러오는 중", "success": "성공", "error": "오류", "failed": "실패",
    "warning": "경고", "ready": "준비됨", "connected": "연결됨", "registered": "등록됨",
    "new": "신규", "planned": "계획됨", "completed": "완료", "due": "예정",
    "analytics": "분석", "review": "검토", "day": "일", "busiest": "활동이 가장 많은",
    "enabled": "활성화", "disabled": "비활성화", "foundation": "기반", "admin": "관리",
    "done": "완료", "note": "메모",
}

_ALLOWED_ENGLISH = re.compile(r"\b(?:Living OS|OS|AI|OpenAI|API|SQLite|JSON|ISO|BMI|KRW|URL|v\d+(?:\.\d+)*|kg|km|kWh|L)\b", re.I)


def ui_text(value: Any, *, context: str = "label") -> Any:
    """Translate presentation text without changing stored values or contracts."""
    if not isinstance(value, str) or not value:
        return value
    if value in UI_TEXT:
        return UI_TEXT[value]
    upper = value.strip().upper()
    if upper in STATUS_TEXT:
        return STATUS_TEXT[upper]

    translated = value
    # Replace complete known phrases inside icon-decorated navigation labels and dynamic captions.
    for source in sorted(UI_TEXT, key=len, reverse=True):
        if source in translated:
            translated = translated.replace(source, UI_TEXT[source])
    for source, target in STATUS_TEXT.items():
        translated = re.sub(rf"\b{re.escape(source)}\b", target, translated, flags=re.I)
    for source, target in WORD_TEXT.items():
        translated = re.sub(rf"\b{re.escape(source)}\b", target, translated, flags=re.I)

    residue = _ALLOWED_ENGLISH.sub("", translated)
    if re.search(r"[A-Za-z]{2,}", residue):
        generic = {
            "error": "요청을 처리하지 못했습니다. 입력값과 현재 상태를 확인해 주세요.",
            "warning": "진행하기 전에 현재 상태와 안내 내용을 확인해 주세요.",
            "success": "요청이 정상적으로 완료되었습니다.",
            "info": "현재 조건에 해당하는 항목이 없습니다.",
            "caption": "현재 상태와 관련 정보를 확인하세요.",
            "help": "입력 조건을 확인하세요.",
        }
        if context in generic:
            return generic[context]
    return translated


def localize_data(value: Any) -> Any:
    """Create a display-only Korean projection of tables and JSON data."""
    if isinstance(value, Mapping):
        return {ui_text(str(key)): localize_data(item) for key, item in value.items()}
    if isinstance(value, list):
        return [localize_data(item) for item in value]
    if isinstance(value, tuple):
        return tuple(localize_data(item) for item in value)
    if isinstance(value, str) and value.strip().upper() in STATUS_TEXT:
        return STATUS_TEXT[value.strip().upper()]
    return value


_LABEL_METHODS = {
    "title", "header", "subheader", "caption", "info", "warning", "error", "success",
    "button", "download_button", "form_submit_button", "text_input", "text_area", "number_input",
    "date_input", "time_input", "checkbox", "toggle", "selectbox", "multiselect", "radio",
    "select_slider", "slider", "file_uploader", "metric", "expander", "toast", "page_link",
}
_OPTION_METHODS = {"selectbox", "multiselect", "radio", "select_slider", "segmented_control"}
_DATA_METHODS = {"dataframe", "table", "json"}


class KoreanStreamlitProxy:
    """Translate Streamlit presentation calls while preserving widget return values."""

    def __init__(self, target: Any):
        object.__setattr__(self, "_target", target)

    def __enter__(self) -> "KoreanStreamlitProxy":
        entered = self._target.__enter__()
        return _wrap(entered)

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> Any:
        return self._target.__exit__(exc_type, exc, traceback)

    def __getattr__(self, name: str) -> Any:
        value = getattr(self._target, name)
        if not callable(value):
            return _wrap(value)

        def call(*args: Any, **kwargs: Any) -> Any:
            mutable = list(args)
            if name in _LABEL_METHODS and mutable and isinstance(mutable[0], str):
                mutable[0] = ui_text(mutable[0], context=name)
            if "placeholder" in kwargs:
                kwargs["placeholder"] = ui_text(kwargs["placeholder"], context="help")
            if "help" in kwargs:
                kwargs["help"] = ui_text(kwargs["help"], context="help")
            if name == "tabs" and mutable and isinstance(mutable[0], Sequence):
                mutable[0] = [ui_text(item) for item in mutable[0]]
            if name in _OPTION_METHODS:
                original: Callable[[Any], Any] = kwargs.get("format_func", str)
                kwargs["format_func"] = lambda item, render=original: ui_text(str(render(item)))
            if name in _DATA_METHODS and mutable:
                data = mutable[0]
                try:
                    import pandas as pd
                    if isinstance(data, pd.DataFrame):
                        data = data.rename(columns={column: ui_text(str(column)) for column in data.columns})
                    else:
                        data = localize_data(data)
                except ImportError:
                    data = localize_data(data)
                mutable[0] = data
            if name == "write" and mutable and isinstance(mutable[0], str):
                mutable[0] = ui_text(mutable[0])
            if name == "markdown" and mutable and isinstance(mutable[0], str):
                text = mutable[0]
                if "<" not in text and "{" not in text and not text.lstrip().startswith("```"):
                    mutable[0] = ui_text(text)
            return _wrap(value(*mutable, **kwargs))

        return call


def _wrap(value: Any) -> Any:
    if isinstance(value, KoreanStreamlitProxy):
        return value
    if isinstance(value, list):
        return [_wrap(item) for item in value]
    if isinstance(value, tuple):
        return tuple(_wrap(item) for item in value)
    module = type(value).__module__
    if module.startswith("streamlit") and type(value).__name__ == "DeltaGenerator":
        return KoreanStreamlitProxy(value)
    return value


_PROXY: KoreanStreamlitProxy | None = None


def localized_streamlit() -> KoreanStreamlitProxy:
    global _PROXY
    if _PROXY is None:
        import streamlit as st
        _PROXY = KoreanStreamlitProxy(st)
    return _PROXY