# 멘토링·오피스아워 사전 질문 (제출본)

- 제출: 2026-11-25 저녁, 구글폼 「해커톤 멘토링·오피스아워 사전 질문」. "응답이 기록되었습니다" 확인.
- 마감은 11/25 18:00였고 그 뒤에 제출했다. 멘토에게 전달됐는지는 미확인.
- 소속 팀: `41 장예나 (1인팀)`
- 답을 받으면 각 질문 아래 `답:` 줄에 적는다.

## 한 줄 소개

원유 화물 양하 후 선주가 보내는 체선료 청구 서류 묶음(청구서·도착 통지서·항만 시간 기록·펌핑 기록·항의서)을 화주 측 정산 담당자를 위해 검증합니다. 필수 서류·서명 누락, 90일 청구 기한, 서류 간 시각 불일치를 판정하고 보완 요청서 초안을 만듭니다.

We verify tanker demurrage claim packages (invoice, NOR, statement of facts, pumping log, letter of protest) for the charterer's claims handler: missing or unsigned documents, the 90-day time bar, and time mismatches, then draft a request for missing evidence.

## 기획 질문 (Aramco·고려대 멘토, 11/26 오전 현장)

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

## 기술 질문 (Upstage 온라인 오피스아워, 11/26 15:00)

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

## 뺀 질문

- Claude Code 사용이 규정상 허용되는지 — 폼의 선택지에 "Claude Code 등 AI 코딩 도구 활용"이 있어 허용으로 보고 뺐다.

## 추가 전달 사항

비워 둠.
