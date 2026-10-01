> **기초 출처 확인: 2026-09-29 / 실행 API 재확인: 2026-09-30, Asia/Seoul.** 확인 날짜가 영구적인 최신성을 보장하지는 않습니다.

## 최신성을 판단한 방식

Microsoft Learn의 개요, capability reference, GA 표, 기능 문서와 공식 SDK 예제를 대조했습니다.
포털 GA와 개별 기능 GA를 구분하고, API·지역·접근 조건이 다르면 더 좁은 범위로 설명합니다.
당시 월간 What's new는 2026년 8월까지였으며 이를 9월 전체 변경 목록으로 바꾸지 않았습니다.

## 기억할 경계

| 항목 | 처리 |
| --- | --- |
| 새 포털 GA | 개별 기능의 GA와 구분 |
| 포털 Workflows 종료 예정 | 2026-12-01, 새 구현은 MAF 검토 |
| Foundry IQ | 일부 API GA, 포털 경험 Preview |
| Memory·Voice·Agent guardrails | 해당 API의 Preview·접근 조건 구분 |
| Agent Optimizer | Limited preview, 선택 실습 |
| Content Understanding | 2025-11-01 GA와 2026-06-01-preview 구분 |
| SDK | 설치 가능한 기본·advanced 조합 분리 |

## 현재 지침과 검증

학습 지침은 **v1 기준선과 개선 v2**만 사용합니다. L08에서 같은 질문·문맥·모델·체크리스트로 한 번 비교합니다.
지침 파일 이름이 v2라는 사실만으로 평가 점수가 올랐다고 판단하지 않습니다.

[현재 지침 상태]({validation})에는 새 v2의 준비 상태와 실제 비교 여부를 기록합니다.
현재 수정본에 대한 새 Azure 비교는 수행하지 않았습니다. 로컬 구조·브라우저·PDF 검사는 `{documentation_validation}/`에만 두며 Azure 결과가 아닙니다.

[가장 최근 실제 실행 원본](validation/current/report.json)은 수정 전 지침으로 수행한 기록입니다.
Dev 합산 39/40 및 critical 근거 실패와 Optimizer 오류 판정은 원래대로 유지합니다. 새 v2의 통과 결과로 바꾸지 않습니다.
현재 파일 목록에는 이 최신 묶음만 두고, 이전 원본은 [고정된 Git 이력]({historical_validation})에 보존합니다.

화면 이미지는 촬영 당시의 실제 포털 관찰입니다. 새 v2 실행 화면이나 새 모델 품질 증거로 사용하지 않습니다.
선택 기능, 조직 정책·권한, 비용 조회, 리소스 삭제, 저장소 병합·게시는 각각 별도 승인 범위입니다.

## 공개 공식 출처

{source_table}

## 다음 교육 전에 확인하기

GA 표, capability reference, 필요한 기능 문서, 지역·모델 지원, SDK 조합 순으로 확인합니다.
실제 변경이 있을 때 해당 소스와 실습 내용을 함께 수정합니다. 실습을 위해 검증 번호나 내역을 계속 늘릴 필요는 없습니다.
