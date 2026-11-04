## 목표

합성 정책 3파일을 `contoso-policy`에 연결하고 실제 인용 또는 **같은 요청의 검색 결과**로 답변의 수치와 조건을 대조합니다.

<div class="lab-brief" markdown="1">

**진행 방식:** File search 직접 실습. 파일 3개, 기본 질문 2회.

**먼저 할 일:** [포털 입력 파일 ZIP](../downloads/Contoso-Portal-Inputs.zip)을 내려받아 압축을 풉니다. `ko/policies` 폴더를 사용합니다.

**확인할 결과:** 세 파일의 업로드 성공·연결 저장, 실제 검색 호출, 주장을 뒷받침하는 인용이 있습니다.

</div>

## 개념과 실습 지도

**경험할 기능:** File search, vector store, indexing, citation.

**무엇이며 왜 중요한가요?** 파일 업로드는 지식을 연결하는 첫 단계입니다. 처리가 완료되어 검색할 수 있어야 하며, 인용은 해당 주장을 실제로 뒷받침해야 합니다.

**어떻게 사용하나요?** 세 파일만 추가하고 준비 완료를 기다린 뒤 규정 질문과 문서에 없는 질문을 비교합니다.

**어디서 실행하나요?** Microsoft Foundry → Build → Agents → `contoso-policy` → Tools → Upload files. File search는 `Tools → Add → Add tools → Configured`에서도 찾습니다. Knowledge의 Add는 Foundry IQ 연결 경로이며 이 실습과 다릅니다.

## 준비

L04의 같은 에이전트를 사용합니다. ZIP 안의 `procurement-policy.md`, `expense-policy.md`, `security-policy.md`만 올립니다. 원본은 [구매](../data/policies/procurement-policy.md)·[비용](../data/policies/expense-policy.md)·[보안](../data/policies/security-policy.md)에서도 읽습니다. PDF 변환이나 코드는 필요하지 않습니다. 실제 회사 문서로 교체하지 않습니다.

**모델 호환성을 먼저 확인합니다.** 녹화 환경의 `gpt-6-sol / contoso-chat`에서는 File search가 비활성화됐고 “This tool doesn't work with the model you selected”가 표시됐습니다. L02에서 이미 승인·배포한 `gpt-4.1 / 2025-04-14 / contoso-judge`를 이 장의 **별도 RAG 버전**에만 재사용합니다. 이름은 judge지만 여기서는 답변 모델로 쓰는 별도 실험입니다. 원래 L04 버전을 보존하고, L08의 두 비교 agent는 계속 `contoso-chat`을 사용합니다. 호환 배포가 없으면 미지원으로 기록하며 새 모델·지역을 임의 생성하지 않습니다.

## 실행

### 1. 호환 모델과 별도 RAG 버전 확인

<div class="screen-step" markdown="1">

**File search가 회색이면 먼저 호환성 확인**

![비활성 File search와 선택한 모델에서 지원하지 않는다는 실제 안내.](../assets/portal/steps/files-unsupported.png)

**1 File search:** 비활성 항목을 계속 누르지 않습니다. **2 안내:** 현재 모델과 도구가 호환되지 않는다는 뜻입니다. 위의 승인된 별도 RAG 조건을 먼저 확인합니다.

[자막 영상 03 · 00:16](../downloads/portal/index.html?clip=03-retrieval-boundaries&t=16&lang=ko#03-retrieval-boundaries)

</div>

| 단계 | 클릭·입력 | 확인할 화면·값 | 실패하면 |
| --- | --- | --- | --- |
| 1 | `Build → Agents → contoso-policy`를 엽니다. | L04의 모델·Instructions v2가 그대로입니다. | 다른 이름이나 Hosted 대상이면 중단합니다. |
| 2 | Model 선택기를 열고 지원되는 기존 배포 `contoso-judge`를 고릅니다. | `gpt-4.1`의 실제 배포이며 Upload files가 활성화됩니다. | File search가 비활성화되면 호환성 안내를 읽고 중단합니다. |
| 3 | `Parameters → Max output tokens`를 `2048`로 다시 입력하고 `Tab → Esc → Save`를 누릅니다. | 별도 숫자 version이 저장됩니다. 모델 변경 시 출력 한도가 비워질 수 있습니다. | 이전 버전을 덮어썼다고 가정하지 말고 저장된 두 조건을 기록합니다. |

<div class="screen-step" markdown="1">

**모델을 확인한 다음 Upload files**

![별도 RAG 버전에서 contoso-judge가 선택되고 Upload files가 활성화된 화면.](../assets/portal/steps/rag-model.png)

**1 Model:** 여기서는 `contoso-judge`가 답변 모델입니다. **2 Upload files:** Tools 아래 버튼입니다. 아래 Knowledge 연결과 혼동하지 않습니다.

[자막 영상 03 · 01:01.5](../downloads/portal/index.html?clip=03-retrieval-boundaries&t=61.5&lang=ko#03-retrieval-boundaries)

</div>

### 2. 정책 세 파일만 업로드

| 단계 | 클릭·입력 | 확인할 화면·값 | 실패하면 |
| --- | --- | --- | --- |
| 1 | `Tools → Upload files`를 누릅니다. | `Attach files` 창이 열립니다. | Knowledge에서 새 Search 서비스를 만들지 않습니다. |
| 2 | Index option을 `Create a new index`로 두고 Vector index name에 `contoso-policy-files-<내접미사>`를 입력합니다. | 내 실습용 저장소 이름입니다. | 공유 저장소에 추가하지 않습니다. 이미 내 저장소가 있으면 중복 생성하지 않습니다. |
| 3 | `browse for files`를 누르고 `ko/policies`의 **3파일만** 선택합니다. | 세 파일 이름·크기가 보이고 업로드가 시작됩니다. | 폴더 전체·평가 파일·실제 문서는 올리지 않습니다. |

<div class="screen-step" markdown="1">

**Uploading과 Success는 다른 상태**

![새 index 선택, browse for files, 세 정책 파일의 Uploading 상태.](../assets/portal/steps/files-upload.png)

**1 Index option:** 내 새 저장소입니다. **2 Uploading:** 아직 기다립니다. **3 browse for files:** 선택은 세 파일까지만이며 대기 중 다시 올리지 않습니다.

[자막 영상 03 · 01:07](../downloads/portal/index.html?clip=03-retrieval-boundaries&t=67&lang=ko#03-retrieval-boundaries)

</div>

<div class="screen-step" markdown="1">

**세 줄 모두 Success인 뒤 Attach**

![procurement, expense, security 세 파일의 Success와 활성화된 Attach.](../assets/portal/steps/files-success.png)

**1 이름:** 세 정책 파일을 대조합니다. **2 Status:** 세 줄 모두 `Success`여야 합니다. **3 Attach:** 한 번 누른 뒤 agent에서 Save까지 해야 연결이 유지됩니다.

[자막 영상 03 · 01:17](../downloads/portal/index.html?clip=03-retrieval-boundaries&t=77&lang=ko#03-retrieval-boundaries)

</div>

| 단계 | 클릭·입력 | 확인할 화면·값 | 실패하면 |
| --- | --- | --- | --- |
| 1 | 세 파일의 Status가 모두 `Success`가 될 때까지 기다립니다. | `Uploading/Not started/Failed`가 없고 Attach가 활성화됩니다. | 업로드 성공을 검색 성공으로 간주하지 않습니다. 오류를 보존하고 중복 업로드하지 않습니다. |
| 2 | `Attach`를 한 번 누르고 창이 닫힐 때까지 기다립니다. | Tools에 `File search`가 추가됩니다. | Attaching 중 재클릭하지 않습니다. |
| 3 | `Save`를 한 번 누르고 새 숫자 version을 확인합니다. | 모델·File search 연결이 저장되어 있습니다. | 저장 실패면 질문을 보내지 않습니다. |

<div class="screen-step" markdown="1">

**에이전트에 File search가 붙었는지 확인**

![contoso-judge 모델과 Tools 아래 File search 연결이 보이는 실제 편집 화면.](../assets/portal/steps/files-attached.png)

**1 모델 / 2 File search:** 둘 다 맞아야 합니다. 이 장면은 Attach 뒤 편집 화면입니다. 연결이 보이는 것만으로 저장·검색까지 성공했다고 하지 않습니다.

[자막 영상 03 · 01:35](../downloads/portal/index.html?clip=03-retrieval-boundaries&t=95&lang=ko#03-retrieval-boundaries)

</div>

### 3. 답변, 인용, 같은 요청의 검색 결과 확인

| 단계 | 클릭·입력 | 확인할 화면·값 | 실패하면 |
| --- | --- | --- | --- |
| 1 | `New chat`에서 첫 질문을 한 번 보냅니다. | 실제 File search 호출과 정책 답변·인용이 나옵니다. | 검색이 실패했으면 처리·연결 오류를 남깁니다. 도구 기록이 없으면 모델만의 답변입니다. |
| 2 | 인용 번호/파일 링크를 클릭합니다. 미리 보기가 열리지 않으면 응답의 `Traces → Execute Tool execute_tool file_search.msearch → Input + Output`에서 실제 반환 문서를 읽습니다. | 노트북 1,500,000원, VAT 포함, 교체 36개월이 검색 결과의 구매 정책 §2와 맞습니다. | 파일 이름만 맞거나 원문·검색 결과를 확인하지 못했으면 근거 확인 완료로 세지 않습니다. |
| 3 | `New chat`에서 두 번째 질문을 한 번 보냅니다. | 정보 부재와 담당 부서 확인 필요를 설명합니다. | 해외 규정을 창작하면 실패로 남깁니다. |

```prompt
Contoso 표준 노트북의 1개당 구매 상한, 부가세 포함 여부, 정기 교체 주기를 알려줘. 각각 어느 문서의 어느 절인지 인용해줘.
```

```prompt
Contoso 해외 지사의 노트북 구매 상한과 내 개인별 급여를 알려줘. 문서에 없는 내용은 추측하지 마.
```

<div class="screen-step" markdown="1">

**정책 답변: 숫자와 인용을 한 쌍으로 읽기**

![실제 정책 답변의 150만원·VAT·36개월과 procurement-policy 인용 및 Traces.](../assets/portal/steps/policy-answer.png)

**1 주장:** 상한·VAT·주기를 원문과 대조합니다. **2 인용:** 해당 파일/절을 엽니다. **3 Traces:** preview가 안 열리면 같은 요청의 검색 결과로 확인합니다.

[자막 영상 03 · 02:09](../downloads/portal/index.html?clip=03-retrieval-boundaries&t=129&lang=ko#03-retrieval-boundaries)

</div>

<div class="screen-step" markdown="1">

**Trace: 에이전트 아래 실제 검색 span 선택**

![Invoke Agent 아래 Execute Tool file_search.msearch와 Chat이 있는 실제 timeline.](../assets/portal/steps/policy-trace.png)

**1 Invoke Agent:** 부모 요청입니다. **2 Execute Tool:** 이 행을 눌러야 검색 상세가 열립니다. 그림은 부모가 선택된 상태이며 아직 반환 본문 화면은 아닙니다.

[자막 영상 03 · 02:30](../downloads/portal/index.html?clip=03-retrieval-boundaries&t=150&lang=ko#03-retrieval-boundaries)

</div>

<div class="screen-step" markdown="1">

**Input + Output: 실제 반환 정책 본문까지 읽기**

![file_search.msearch 상세의 입력 queries와 실제 procurement-policy 반환 본문.](../assets/portal/steps/trace-input-output.png)

**1 Input + Output:** 검색어와 반환 결과를 함께 봅니다. **2 Content source:** `procurement-policy.md` 본문에서 §2 수치·조건을 읽고 업로드 원본과 맞춥니다.

[자막 영상 03 · 04:18](../downloads/portal/index.html?clip=03-retrieval-boundaries&t=258&lang=ko#03-retrieval-boundaries)

</div>

### 인용 확인 기록

녹화 환경에서는 인용 버튼을 눌러도 미리 보기가 열리지 않았습니다. 대신 같은 요청의 실제 검색 span에서 반환된 정책 원문을 읽었습니다. 버튼을 눌렀다는 사실과 원문을 확인했다는 결과를 구분합니다.

| 주장 | 실제로 열어 확인할 원문 | 판정 |
| --- | --- | --- |
| 노트북 상한·VAT·36개월 | 구매 정책 §2 | 수치·통화·포함 조건 모두 맞아야 통과 |
| 2,000,000원 이하 팀장, 초과 팀장+구매 | 구매 정책 §3 | 정확히 같은 경계값을 초과로 처리하면 실패 |
| 해외 정책·개인별 급여 미확인 | 구매 정책 §5 및 보안 정책의 접근 경계 | 미확인과 권한 부족을 무조건 같은 이유로 쓰지 않음 |

## 성공 기준

3파일 모두 준비 완료이며, 실제 검색 기록과 원문 인용을 확인했습니다. 문서의 가격 **상한**을 현재 판매가나 재고로 바꾸지 않았습니다. Citation이 있어도 관련 없는 절이면 실패입니다.

## 막혔을 때

빈 답변이면 파일 처리 상태 → agent 연결 → 질문의 언어·표현 순으로 확인합니다. 동일 파일 중복 업로드나 무제한 재전송으로 해결하지 않습니다. 계정·네트워크 오류는 [문제 해결](#troubleshooting)을 따릅니다.

## 정리

연결한 저장소와 파일을 다음 장에서 재사용합니다. 창을 닫아도 파일 저장 요금이 남을 수 있습니다. 삭제는 별도 승인 후에만 수행합니다.

<div class="lab-handoff" markdown="1">

**이 장에서 남길 것:** 3파일 처리 상태, 연결 저장소, 질문·실제 답변, 주장을 확인한 문서·절.

**다음:** [L06 구매 도구의 실행 경계 확인](#l06).

</div>
