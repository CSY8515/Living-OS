# Korean UI Guideline

## Language hierarchy

- Brand and product name: **Living OS**
- User actions, guidance, validation, errors, and status explanations: Korean
  first
- Established technical identifiers shown only in management contexts may remain
  English with a Korean explanation

## Voice

Use concise, respectful, direct language. Explain what happened, whether data was
saved, and what the user can do next. Avoid blaming the user or exposing stack
traces, schema names, Python exceptions, and developer abbreviations.

## Standard action terms

- Create: 추가 / 기록
- Save: 저장
- Update: 수정
- Archive: 보관
- Restore: 복원
- Delete: 삭제
- Retry: 다시 시도
- Cancel: 취소
- Review: 검토

The selected noun must identify the affected record. Destructive actions state
their consequence before confirmation.

## Status and feedback

- Success: “저장했습니다.” or “[대상]을 저장했습니다.”
- Validation: required field and acceptable format
- Failure: action that failed, confirmation that existing data was preserved,
  and a safe next step
- Loading: present-tense action, not an indefinite “처리 중”

## Korean typography

- Do not rely on forced word-breaking in headings or buttons.
- Allow phrase-aware wrapping and adequate line height.
- Avoid single-character orphan lines.
- Test common mobile widths with real Korean labels.
- Keep mixed Korean/English punctuation and spacing consistent.

This document does not authorize the excluded full Korean patch in v2.0.5.
