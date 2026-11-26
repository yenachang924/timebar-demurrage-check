# 멘토링·오피스아워 사전 질문

- **현재 제출본은 2026-11-26 수정본이다.** 사용자가 폼에서 직접 고쳐 제출했다. 아래 문구는 수정 직전에 정리한 안이며, 폼에 실제로 들어간 문구와 다른 곳이 있으면 폼이 기준이다.
- 소속 팀: `41 장예나 (1인팀)`
- 답을 받으면 각 질문 아래 `답:` 줄에 적는다. 답에 따라 바꿀 것은 맨 아래 표를 본다.
- 11/25 첫 제출본은 이 파일 끝에 남겨 두었다.

## 한 줄 소개

원유 화물 양하 후 선주가 보내는 체선료 청구 서류 묶음(청구서·도착 통지서·항만 시간 기록·펌핑 기록·항의서)을 화주 측 정산 담당자를 위해 검증합니다. 필수 서류·서명 누락, 90일 청구 기한, 서류 간 시각 불일치를 판정하고 보완 요청서 초안을 만듭니다. 현재 Studio 워크플로우가 가상 청구 10건(서류 51개)에서 판정 10건 모두 정답과 일치합니다.

We verify tanker demurrage claim packages (invoice, NOR, statement of facts, pumping log, letter of protest) for the charterer's claims handler: missing or unsigned documents, the 90-day time bar, and time mismatches, then draft a request for missing evidence. The Studio workflow currently matches the answer key on all 10 test claim packages (51 documents).

## 기획 질문 (Aramco·고려대 멘토, 11/26 현장)

1. **[실제 업무와 맞는가]** Aramco 터미널 규정집(2025년판 §11.1.2)에 "Saudi Aramco에 대한 체선료 청구"가 언급되어 있어 이 업무를 골랐습니다. 다만 Aramco나 정유사 안에서 이 청구를 누가, 어떤 서류로 검토하는지는 공개 자료로 확인하지 못했습니다. 실제로도 청구서, 도착 통지서, 시간 기록, 펌핑 기록 묶음으로 들어오나요? 제가 틀리게 가정한 부분이 있다면 알려 주세요.
   I chose this task because Aramco's Ports and Terminals Rules (2025, §11.1.2) refer to demurrage claims against Saudi Aramco. However, I could not confirm from public sources who reviews these claims inside Aramco or a refinery, or with which documents. Do claims really arrive as a bundle of invoice, NOR, statement of facts and pumping log? Please tell me if any of my assumptions are wrong.
   - 답 (2026-11-26 현장 멘토, 사용자 메모 그대로):
     - 현업에 이런 업무를 담당하는 부서가 있다.
     - 자동화를 도입하기 전까지 검증 과정이 필요하고 고도화가 필요하다. 사람이 하던 것과 맞는지, 오류가 없는지를 봐야 한다.
     - 자동화되어 빨라지면 불필요한 절차가 사라지고, 병목을 풀고, 사람의 실수를 없애면서 빠르게 갈 수 있다.
     - 발표 기조: 에너지 산업이 있고, 이 과정이 위험이 될 수 있다. 이 과정에서 생기는 위험에 따른 효율 감소를 먼저 밝히고 들어가면 의의가 선다. 에너지 → 판례 순서.
     - 에너지 산업과의 연계는 약점이지만 강점일 수도 있다. 문제 정의를 앞쪽에서 들고 들어가면 좋다.
     - 전체적으로 좋다는 피드백.
   - 반영: 2번 슬라이드 원고를 산업 → 위험 → 판례 순서로 바꿈. Aramco 접점 근거를 Bahri 공시로 바꿈.
   - 아직 모르는 것: 멘토의 이름·소속을 발표에서 말해도 되는지, 어느 부서인지, 질문 2~4에 대한 답.

2. **[가장 흔한 문제]** 현업에서 체선료 청구가 거절되거나 지연되는 가장 흔한 서류 문제는 무엇인가요? (서명 누락, 청구 기한 초과, 서류 간 시각 불일치 중)
   In practice, which document issue most often causes a demurrage claim to be rejected or delayed: missing signatures, a missed time bar, or time discrepancies between documents?
   - 답:

3. **[검토 필요의 기준]** 펌핑 기록에 터미널 서명이 없고 항의서가 첨부된 청구는 `검토 필요`로 사람에게 넘기도록 했습니다. BPVOY4에는 항의서가 서명을 대신한다는 문구가 없기 때문입니다. 현업에서는 이런 건을 바로 보완 요청하나요, 아니면 사람이 판단하나요? 또 테스트 10건 중 4건이 `검토 필요`인데, 자동화 도구로서 너무 많다고 보시나요?
   When the pumping log has no terminal signature but a letter of protest is attached, my workflow returns "review needed" and hands the case to a person, because BPVOY4 does not say a protest replaces the signature. In practice, would you request the signed log right away, or is this a judgment call? Also, 4 of my 10 test cases end in "review needed". Is that too many for an automation tool?
   - 답:

4. **[후속 문서]** 판정마다 후속 문서를 만듭니다. 서류가 부족하면 선주에게 보내는 영문 보완 요청 서신 초안, 기한 위험과 검토 필요는 내부 메모, 문제가 없으면 지급 검토 메모입니다. 현장에서 화면을 보여 드릴 테니, 담당자가 그대로 쓸 수 있는 수준인지와 빠진 내용을 알려 주실 수 있을까요?
   Each decision produces a follow-up document: a draft letter to owners in English when documents are missing, an internal memo for time-bar risk or review needed, and a payment-review memo when the claim is clear. I will show the screen on site. Could you tell me whether a handler could use these as they are, and what is missing?
   - 답:

## 기술 질문 (Upstage 온라인 오피스아워, 11/26 15:00)

1. **[날짜 비교와 Validate]** 현재 판정을 Instruct 노드 하나가 냅니다. 기한일은 접수 기록 서류에 적힌 값을 읽어 접수일과 비교합니다. 이 날짜 비교와 서류 누락 판정을 Validate 노드로 옮길 수 있나요? Instruct로 두면 "설계 논리" 평가에서 불리한가요?
   - 답:

2. **[출력 끝에 판정값 반복]** 판정 Instruct의 결과 화면에 키 5개가 나온 뒤 판정값이 한 줄 더 붙습니다(예: `missing_documents: []` 다음 줄에 `검토 필요`). 결정값(enum)이 따로 표시되는 것으로 보입니다. 채점기는 이 노드의 무엇을 읽나요? `missing_documents` 값이 `[]`로 정확히 읽히는지 확인하고 싶습니다.
   - 답:

3. **[reason 채점]** 정답지의 `reason`은 "필수 서류 누락: Notice of Readiness. 기한 내 접수(접수일 …, 기한일 …)"처럼 짧게 썼고, 워크플로우는 같은 근거를 두세 문장으로 풀어 씁니다. 근거는 같고 길이가 다른 경우 LLM 채점에서 정답으로 보나요? 정답지를 워크플로우 문체에 맞춰 길게 쓰는 편이 안전한가요?
   - 답:

4. **[라이브러리 게시]** (1) 가이드 표에는 게시 이름이 `[도메인] 자동화 워크플로우 이름`으로 적혀 있는데, 현재 이름은 `TimeBar_최종제출_유조선 체선료 청구 서류 검증`입니다. 대괄호 형식으로 바꿔야 하나요? (2) 워크플로우에 이전 판 문서와 녹화용 파일이 5개 남아 있습니다. 샘플 문서에서 체크만 빼면 채점에서 제외되나요? 한 파일에 실행 기록이 여러 개면 어느 실행이 복사되나요?
   - 답:

## 현장에서 추가로 물을 것 (폼에 없음)

5. **[게시된 설정 버전]** 게시 창에서 설정 #4를 골라 승인 요청을 냈는데, 게시물 설정 창에는 "#1 게시됨"으로 보입니다. #4가 올라간 것이 맞나요? "#1"은 게시물 자체의 판 번호인가요?
   - 답:

## 답에 따라 바꿀 것

| 답 | 바꿀 것 |
|---|---|
| 기획 1: 서류 구성이 실제와 다르다 | 발표 3번 슬라이드 문구, 원고의 "A claim arrives as a bundle" 문단, 설계서 1번 칸 |
| 기획 2: 가장 흔한 문제 | 발표 2번에서 그 문제를 앞에 세우고, Q&A "What would you do next?" 답을 고친다 |
| 기획 3: 무서명 + 항의서는 바로 보완 요청한다 | 판정 기준 변경은 결정 사항이다(사용자 결정 → `decisions.md`). 바꾸면 set06 정답, 프롬프트, 설계서 4번 칸, 유형표, 발표 5·6번을 함께 고치고 10건을 다시 돌린다 |
| 기획 3: 4건은 너무 많다 | 데이터셋은 그대로 두고, 발표에서 "어려운 사례를 일부러 넣었다"를 먼저 말한다 |
| 기술 1: Validate로 옮길 수 있다 | 마감 전 시간이 되면 옮기고 10건 재실행. 안 되면 발표 6번에서 "다음 단계"로 말한다 |
| 기술 2: 채점기가 텍스트 전체를 읽는다 | 판정 노드 출력 형식을 고치고 10건 재실행, 설정 번호가 올라가면 JSON 다시 내보내기·재게시 |
| 기술 3: 정답지를 길게 쓰는 편이 안전하다 | `work/gen/cases.py`의 reason 문구를 고치고 정답지 재생성 |
| 기술 4·5: 이름 형식, 게시 버전 | 이름을 바꾸면 설계서 "워크플로우 이름" 칸도 고친다. 버전이 틀렸으면 게시 취소 후 재게시 |

---

## 첫 제출본 (2026-11-25, 참고용)

- 제출: 2026-11-25 저녁, 구글폼 「해커톤 멘토링·오피스아워 사전 질문」. "응답이 기록되었습니다" 확인.
- 마감은 11/25 18:00였고 그 뒤에 제출했다. 멘토에게 전달됐는지는 미확인.
- 소속 팀: `41 장예나 (1인팀)`
- 답을 받으면 각 질문 아래 `답:` 줄에 적는다.

### 한 줄 소개

원유 화물 양하 후 선주가 보내는 체선료 청구 서류 묶음(청구서·도착 통지서·항만 시간 기록·펌핑 기록·항의서)을 화주 측 정산 담당자를 위해 검증합니다. 필수 서류·서명 누락, 90일 청구 기한, 서류 간 시각 불일치를 판정하고 보완 요청서 초안을 만듭니다.

We verify tanker demurrage claim packages (invoice, NOR, statement of facts, pumping log, letter of protest) for the charterer's claims handler: missing or unsigned documents, the 90-day time bar, and time mismatches, then draft a request for missing evidence.

### 기획 질문 (Aramco·고려대 멘토, 11/26 오전 현장)

- 어려운 영역: 문제 정의 및 주제 선정 / 타깃 사용자·현업 페인포인트 파악 / 서비스 차별성·기대 효과 정리
- 진행 단계: 주제 확정, 세부 기획 중
- 심각도: 4 / 5

1. 원유 화물의 터미널 작업 서류(도착 통지서·항만 시간 기록·펌핑 기록)로 체선료 청구를 검증하는 업무가 이번 대회의 "운영" 또는 "공급망" 분야 주제로 적합한지 궁금합니다. 에너지 현장의 문제로 보이려면 무엇을 강조해야 할까요?
   Is verifying demurrage claims against terminal cargo-operation documents (NOR, statement of facts, pumping log) a good fit for the "Operations" or "Supply chain" track? What should we emphasize so that it reads as an energy-operations problem?
   - 답:

2. 현업에서 체선료 청구가 거절되거나 지연되는 가장 흔한 서류 문제는 무엇인가요? (서명 누락, 청구 기한 초과, 서류 간 시각 불일치 중)
   In practice, which document issue most often causes a demurrage claim to be rejected or delayed: missing signatures, a missed time bar, or time discrepancies between documents?
   - 답: 

3. 범위를 용선계약 양식 하나(BPVOY4)와 세 가지 확인(서류 완결성, 90일 청구 기한, 시각 일치)으로 좁혔고, 금액 검산은 사람에게 넘깁니다. 현업에서 의미 있는 범위일까요?
   We limited the scope to one charter party form (BPVOY4) and three checks (completeness, 90-day time bar, time consistency), leaving the amount calculation to the handler. Is this scope meaningful in practice?
   - 답:

4. 워크플로우 결과로 담당자가 바로 다음 일을 하려면 어떤 후속 문서가 가장 쓸모 있을까요? (선주에게 보내는 보완 요청 서신, 내부 지급 검토 메모 등)
   Which follow-up document would be most useful to the handler right after the check: a request letter to owners for missing evidence, or an internal payment-review memo?
   - 답:

### 기술 질문 (Upstage 온라인 오피스아워, 11/26 15:00)

- 어려운 영역: Upstage Studio 활용 / 문서 파싱·정보 추출 / 성능 개선(정확도·속도·비용) / Claude Code 등 AI 코딩 도구 활용
- 기술 스택: Upstage Studio (Parse, Classify, Extract, Merge, Instruct), Claude Code, Python (테스트 문서 PDF·정답지 생성, 실행 결과 채점 스크립트)
- 진행 단계: 프로토타입 제작 중
- 심각도: 4 / 5

1. [날짜 계산] 목표: "양하 완료일로부터 90일 이내에 청구가 접수됐는가"를 판정합니다. 문제: 예시팀 워크플로우는 고정 날짜와의 비교만 하고, 두 날짜의 일수 차이를 계산하는 예시가 없습니다. 시도: 문서에 기한일을 미리 적어 두고 Instruct가 날짜 두 개만 비교하도록 설계했습니다. Validate 노드에서 날짜 차이를 규칙으로 계산할 수 있나요? 가능하다면 권장 설정을, 어렵다면 권장 구성을 알고 싶습니다.
   - 답:

2. [서명 유무] 스캔 문서에서 서명란에 서명이 있는지 없는지를 Extract의 boolean 항목으로 안정적으로 뽑는 방법이 있나요? 서명란이 빈 선만 있는 경우와 손글씨가 있는 경우를 구분해야 합니다.
   - 답:

3. [분할 후 분류] PDF 하나에 서류 6종(각 1쪽)이 합쳐진 케이스에서 Classify의 분할 후 분류가 쪽 단위로 안정적으로 나뉘게 하려면 문서종 설명을 어떻게 쓰는 것이 좋은가요? 케이스 1건의 실행 시간 제한(시간초과 기준)은 얼마인가요?
   - 답:

4. [재실행 일관성] 채점 때 전체 데이터를 다시 실행한다고 들었습니다. 판정 Instruct의 결과가 실행마다 흔들리지 않게 하는 권장 설정이 있나요? reason처럼 문장인 값은 정답지와 어느 정도 같아야 정답으로 인정되나요?
   - 답:

5. [데이터셋 건수] 최종 제출 데이터셋이 LMS "결과물 제출 안내" 페이지에는 20종, 산출물 제출 가이드 문서에는 문서 10건 이상으로 적혀 있습니다. 어느 쪽이 맞나요?
   - 답:

6. [설정 가져오기] 예시팀 workflow.json과 같은 구조로 직접 작성한 설정 JSON을 "설정 가져오기"로 넣어도 되나요? 제출용 파일은 Studio에서 다시 내보낸 것을 내겠습니다.
   - 답:

### 뺀 질문

- Claude Code 사용이 규정상 허용되는지 — 폼의 선택지에 "Claude Code 등 AI 코딩 도구 활용"이 있어 허용으로 보고 뺐다.

### 추가 전달 사항

비워 둠.
