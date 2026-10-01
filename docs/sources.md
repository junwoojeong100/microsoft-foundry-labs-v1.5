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
현재 v1/v2는 국문·영문 각각 12개 질문으로 버전 고정 GPT-6 Sol Prompt Agent를 통해 실측했습니다. 한국어 native 관련성은 4.9167/5→5.0/5로 한 문항만 변했고, 다른 한국어 지표와 영어 지표는 모두 5.0/5 동점입니다. 로컬 체크는 국문 33/40 동점·영문 29/40→28/40입니다. critical 플래그 변화는 원응답을 수동 대조했고 일부는 정규식의 표현 누락으로 확인했습니다. 비교 원문·Agent 버전·문항별 native 이유·토큰·지연은 [최신 보고서](validation/current/report.json)와 연결된 언어별 파일에서 확인합니다. 로컬 구조·브라우저·PDF 검사는 `{documentation_validation}/`에 따로 두며 Azure 결과가 아닙니다.

[가장 최근 실제 실행 원본](validation/current/report.json)은 이 국문·영문 비교의 응답과 native 판정을 연결합니다.
48개 대상 응답은 한 번씩 수집했고 Native 평가 두 건은 각 24행으로 완료했습니다. v2 토큰과 평균 지연 증가는 한국어 +7,376·+0.427초, 영어 +5,157·+0.496초였습니다. Optimizer와 봉인 holdout은 새로 실행하지 않았습니다.
이전 direct-response 비교의 지침과 측정 원본은 [보존된 기준선 커밋](https://github.com/junwoojeong100/microsoft-foundry-labs-v1.5/tree/39b2bd1a1c85cb18d3d46d8bf876a6e274d32958/validation)에 그대로 남습니다. 이번 제한적 한국어 관련성 관측은 독립 holdout 통과·통계적 유의성·출시 승인이 아닙니다.

화면 이미지는 촬영 당시의 실제 포털 관찰입니다. 새 v2 실행 화면이나 새 모델 품질 증거로 사용하지 않습니다.
선택 기능, 조직 정책·권한, 비용 조회, 리소스 삭제, 저장소 병합·게시는 각각 별도 승인 범위입니다.

## 공개 공식 출처

{source_table}

## 다음 교육 전에 확인하기

GA 표, capability reference, 필요한 기능 문서, 지역·모델 지원, SDK 조합 순으로 확인합니다.
실제 변경이 있을 때 해당 소스와 실습 내용을 함께 수정합니다. 실습을 위해 검증 번호나 내역을 계속 늘릴 필요는 없습니다.
