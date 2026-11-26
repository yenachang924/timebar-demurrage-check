# 브리프 — 유조선 체선료 청구 서류 검증 (TimeBar)

상태: **v2 · 2026-11-26**. 워크플로는 Studio 설정 #7로 동작하고(2026-11-26 오후에 판정 지시문을 보강해 #4에서 올림), 라이브러리 승인 요청까지 냈다. v1(2026-11-25)은 만들기 전에 쓴 계획이었고, 이 판은 만든 뒤의 실제 상태다. 바뀐 경위는 `docs/decisions.md`에 있다.

출처 표기: 각 사실 뒤 `[번호]`는 맨 아래 출처 목록의 번호다. 목록의 URL은 조사 에이전트가 2026-11-25에 실제로 연 페이지다. 2026-11-26에 판결문 4건과 Aramco·S-OIL 공식 문서 3건을 다시 열어 발표에 쓰는 주장을 대조했다.

**근거 원칙(2026-11-26 사용자 결정)**: 발표와 설계의 근거는 판결문과 회사 공식 문서만 쓴다. 조사 중 본 그 밖의 자료(P&I 클럽 해설, 가격 평가 기관, 소프트웨어 회사 글)는 맨 아래 "쓰지 않는 자료"에 따로 둔다.

## 1. 누구의 어떤 순간인가

- 직무: 원유를 배로 받는 화주(용선자) 쪽 체선료 정산 담당자.
- 순간: 양하가 끝난 뒤 선주가 체선료 청구서와 증빙 묶음을 보내왔을 때.
- 지금 방식: 담당자가 서류 대여섯 개를 나란히 놓고 눈으로 맞춰 본다는 것은 **팀의 가정**이다. 현업에서 확인하지 못했다(`미확인`, 11/26 멘토링 기획 질문 1번).

## 2. 문제 정의의 논리

| 단계 | 주장 | 근거 |
|---|---|---|
| 1. 규칙 | 청구서와 모든 증빙 서류가 양하 완료 후 90일 안에 화주에게 도착해야 한다. 아니면 화주는 책임을 면한다("discharged and released from all liability") | BPVOY4 20.1조, The Adventure 판결문이 인용한 조문 [1] |
| 2. 집행 | 법원은 서류 한 가지가 빠졌다는 이유로 청구 전체를 기각했다 | 판결 3건 [3][4][10], 아래 표 |
| 3. 누구의 일인가 | 세 사건 모두 화주가 빠졌거나 서명이 없는 서류를 근거로 들었고 체선료 청구는 소멸했다. 청구액 합계 USD 535,784.54(법원이 인정한 금액이 아니라 청구된 금액). 이 확인이 자동화 대상이다 | 같은 판결 3건 |
| 4. 왜 에너지 회사인가 | 사실 둘과 추론 하나다. 사실: Bahri는 Aramco가 도착지 인도로 파는 원유의 독점 운송사이고 2025년 Aramco 그룹에서 매출 47억 2,700만 리얄을 올렸다. 사실: Bahri의 회계 정책상 용선자가 정박 시간 초과 지연을 보상한다. 추론: Aramco 그룹은 용선자 쪽에 있다. 지급액은 공시에 없다. 현업에 담당 부서가 있다는 것은 멘토에게 확인했다(2026-11-26) | Bahri 재무제표 주석 27·4.2 [24], 연차보고서 p.56 [23], Aramco 연차보고서 [18] |
| 5. 왜 "거절"을 내지 않나 | 같은 기한 항변이 받아들여지지 않은 판결도 있다 | The Amalie Essberger [6] |

**판결**

| 사건 | 계약 양식 | 문제 서류 | 결과 | 청구액 |
|---|---|---|---|---|
| The Sabrewing, Waterfront Shipping v Trafigura [2007] EWHC 2482 (Comm) [4] | BPVOY3 (서류 목록은 16조, 기한은 23조) | 펌핑 기록에 서명이 전혀 없다고 본 전제(약식 판결을 위해 가정한 사실, 선주는 다툼), 대신할 항의서도 없음 | 체선료 청구 전체 소멸 (판결문 32문단) | USD 114,887.40 |
| The Adventure, Kassiopi Maritime v Fal Shipping [2015] EWHC 318 (Comm) [3] | 수정 BPVOY4 | 항의서에 언급된 포트 로그·타임시트 미제출(검역 메모도 함께 문제 됨) | 20.1조로 청구 전체 소멸 (41~47문단). 선주가 일부 시간을 이미 양보해 실제 다툰 금액은 청구서보다 적음 | USD 364,847.78 |
| MTM Hong Kong, Tricon Energy v MTM Trading [2020] EWHC 700 (Comm) [10] | 수정 Asbatankvoy | 선하증권 사본 2건 미제출 | 청구 전체 소멸 (35문단). 화주가 항소에서 이김. 법원은 "이 사건 조항에 한정"이라고 밝힘 (36문단) | USD 56,049.36 |
| The Ocean Neptune, Lukoil Asia Pacific v Ocean Tankers [2018] EWHC 163 (Comm) [5] | — | 터미널이 연서한 시간 기록(또는 항의서) 미제출 | 기한 조항 적용, 소멸 | 선주 청구 USD 772,327.87 (발표에는 쓰지 않음) |
| The Amalie Essberger [2019] EWHC 3402 (Comm) [6] | 수정 Asbatankvoy | 펌핑 기록·항의서가 청구서에 첨부되지 않았다는 주장 | 화주의 약식 판결 신청 기각, 청구가 기한으로 소멸하지 않음 (63~64문단). **선주가 체선료를 받은 것은 아니다**(다른 항변이 재판에 남음, 4문단) | USD 154,875.00 |

- 세 판결의 계약 양식은 서로 다르다. 같은 것은 "기한 안에 증빙을 다 보내지 않으면 청구가 소멸한다"는 조항의 구조다. "세 건 모두 BPVOY4"라고 말하면 틀린다.
- The Adventure 판결은 The Sabrewing의 전체 소멸 법리에 의문을 표한다(44~45문단, 방론). "세 판결이 같은 규칙을 확립했다"고 말하면 안 된다.
- 위 문단 번호와 금액은 2026-11-26에 판결문 원문(The National Archives)을 다시 열어 대조했다.
- 기한 초과·서류 미비 청구의 비율, 담당자 한 사람의 처리 건수, 수작업 검토 시간: 공식 자료에서 찾지 못했다(`미확인`). 주장하지 않는다.

## 3. Aramco와의 연결

모두 회사 공식 문서(aramco.com, s-oil.com, bahri.sa)에서 확인한 것이다.

- **Aramco 터미널 규정에 체선료 청구가 한 번 나온다.** 2025년판 §11.1.2(Loading Rates)는 Aramco 자체 터미널에서 선적이 느릴 때를 다룬다. "만약 그 선박이 Saudi Aramco를 상대로 체선료 청구를 한다면" 느린 선적 속도를 허용 정박 시간 소급 가산에 고려한다는 문장이다. 여기서 Aramco는 **선적항의 터미널 운영자**이고, 이 워크플로의 사용자(양하 후 청구 묶음을 받는 화주)와 자리가 다르다. 규정집 전체에서 demurrage는 이 한 문장뿐이다. 이 조항으로 "Aramco가 청구를 받아 검토한다"를 입증할 수는 없다 [17].
- 24시간 전 도착 통지를 하지 않으면 허용 정박 시간이 늘어날 수 있다(can)는 조항도 있다(§6.3.2) [17].
- **도착 통지서의 시각 규칙이 규정집에 있다.** 통지 시각은 이메일로 터미널 플래너와 대리점에 보내고, 항계 도착 전에는 통지할 수 없다(§7.2.1, §7.2.2) [17].
- **물량**: 2025년 Aramco 원유 수출 평균 하루 630만 배럴(연차보고서 p.62, 회사 단독 기준) [18]. 본선 인도 조건으로 판 물량은 운송과 체선 책임이 사는 쪽에 있으므로, 수출량이 곧 Aramco가 받는 청구 건수는 아니다.
- **한국 접점 (발표에는 쓰지 않음, 업무와의 연결이 약함)**: Aramco의 S-OIL 지분은 61.6%(Aramco 2025 연차보고서 p.57 그래픽, S-OIL 공시의 보통주 기준은 63.41%)이고, S-OIL은 울산 온산 산업단지에 하루 669,000배럴의 원유 정제 시설을 두고 있으며, S-OIL은 Saudi Aramco와 20년 장기 원유 공급 계약(2012년 체결)을 맺고 있다 [18][19][20][21].
- **운송 (발표의 주된 근거, 2026-11-26 원문 대조)**: Bahri는 도착지 인도 조건으로 팔리는 Saudi Aramco 원유의 독점 운송사이고(연차보고서 p.56), 운송 계약 가운데 가장 큰 것이 Saudi Aramco와의 계약이다(p.30). 2025년 Aramco와 그 자회사에서 올린 매출은 4,727,083천 리얄이다(재무제표 주석 27, 2024년 4,238,859천). Aramco Trading에 원유 운송 서비스를 제공한다(연차보고서 p.144). Aramco는 Bahri 지분 20%를 보유한다(p.56). 회계 정책상 용선자가 허용 정박 시간을 넘긴 지연을 보상하고, 체선료는 운임 수익의 변동 대가로 잡는다(주석 4.2). 문서·승인·보고 업무 자동화 방침도 밝혔다(연차보고서 p.107) [23][24].
  - **적혀 있지 않은 것**: Aramco가 낸 체선료 금액, 체선료 수익을 Aramco와 연결한 주석, 청구 서류나 기한. "Aramco 그룹은 용선자로서 체선료 청구를 받는 쪽"은 위 사실들에서 끌어낸 추론이다.

**말하면 안 되는 것**

- "S-OIL이 이런 청구를 이렇게 검토한다" — 확인된 것은 지분, 정제 능력, 공급 계약뿐이다.
- "Aramco 서식을 본떠 문서를 만들었다" — 규정집의 양식(Form 32 Protest Letter, Form 39 General and Cargo Log)은 Aramco가 작성하는 터미널 측 양식이다. 도착 통지서, 시간 기록, 펌핑 기록 양식은 규정집에 없다 [16b].
- Aramco나 Aramco Trading의 체선료 청구 기한 조항, 내부 검토 절차, 터미널 서류 디지털화 계획 — 찾지 못했다(`미확인`).

## 4. 문서

청구 1건 = PDF 1개(서류 묶음) = 판정 1건.

| 문서 | 뽑는 값 |
|---|---|
| 체선료 청구서 (Demurrage Claim Invoice) | 청구 번호, 선박명, 항차, 양하 완료 일시, 청구 금액 |
| 접수 기록 (Claim Receipt Record, 화주 측 대장) | 양하 완료 일시, 기한일, 접수일 |
| 도착 통지서 (Notice of Readiness) | 선박명, 항차, 통지 일시, 서명 |
| 항만 시간 기록 (Statement of Facts) | 선박명, 항차, 호스 분리 일시, 서명, 판독 가능 여부 |
| 펌핑 기록 (Cargo Pumping Log) | 선박명, 항차, 본선 선임사관 서명, 터미널 서명 |
| 항의서 (Letter of Protest) | 사유, 발행 일시 |

- 앞의 다섯 가지를 **필수 서류**로 본다. 이 목록은 조항이나 판결이 열거한 것이 아니라 **팀이 가상 화주사의 접수 기준으로 정한 것**이다. BPVOY4 20.1조가 요구하는 것은 "all supporting documentation"이고, 법원은 이를 몇 가지 서류로 한정하지 않았다 [3]. 다섯 가지는 판결에서 실제로 문제가 된 서류(펌핑 기록 [4], 시간 기록 [5], 포트 로그·타임시트 [3])와 겹친다.
- 테스트 문서는 모두 가상이다. 시간 기록, 펌핑 기록, 항의서는 실제 서식의 칸 구성을 따랐고, 로고는 쓰지 않았다. 기관명은 발행 기관으로 쓰지 않았지만, 표준 양식의 시간 기록(set01·02·03·04·06·08·09) 하단에는 서식 출처를 밝히는 문구 'BIMCO/FONASBA standard short form … FICTIONAL SAMPLE'이 한 줄 있다.

## 5. 판정과 기준

| 순서 | 판정 | 조건 | 근거 |
|---|---|---|---|
| 1 | `검토 필요` | 다른 선박·항차의 서류가 섞임 / 판정에 필요한 값을 읽을 수 없음 / 청구서의 양하 완료 일시 ≠ 시간 기록의 호스 분리 일시 / 펌핑 기록에 터미널 서명이 없고 항의서가 첨부됨 | 앞의 셋은 팀이 정한 기준. 넷째는 아래 설명 |
| 2 | `기한 위험` | 접수일이 기한일보다 늦음 | BPVOY4 20.1조 [1] |
| 3 | `보완 요청` | 필수 서류 누락 / 펌핑 기록에 터미널 서명이 없고 항의서도 없음 | 20.1조의 "all supporting documentation" [1], 19.7.1조의 서명 요건 [1] |
| 4 | `지급 검토 가능` | 모두 통과. 기한 당일 접수는 기한 내로 본다 | — |

- **무서명 + 항의서를 `검토 필요`로 두는 이유**: "터미널 서명이 없으면 항의서로 대신한다"는 문구는 BPVOY4가 아니라 BPVOY3 16조(a)에 있다 [4]. BPVOY4 19.7.1조는 본선 선임사관과 터미널 대표가 서명한 펌핑 기록을 요구하고(화물 작업 추가 시간 청구에 관한 조항) [1], 항의서가 서명을 대신하는지는 판결문 인용 범위에서 확인되지 않는다. 그래서 추측하지 않고 사람에게 넘긴다. (2026-11-25 사용자 결정)
- **기한일은 계산하지 않는다.** 접수 기록에 적힌 기한일과 접수일을 읽어 비교한다. 언어 모델이 90일을 세다 틀리는 일을 피하려는 설계다. 접수 기록이 틀리면 판정도 틀린다는 한계가 있다.
- **"거절"은 내지 않는다.** 2번 표의 5단계 참고.
- **범위 밖**: 정박 시간과 체선료 금액 계산. 담당자가 한다.

## 6. 출력

판정 노드(Instruct `청구_판정`) 하나가 키 5개를 낸다. 정답지 키와 대소문자·밑줄까지 같다.

| 키 | 형식 |
|---|---|
| `claim_no` | 문자열, 예: `DMG-2026-0417` |
| `vessel_name` | 문자열 |
| `decision` | 판정값 4개 중 하나 |
| `reason` | 한 줄 문장 |
| `missing_documents` | JSON 배열. 빠진 서류의 영문 이름, 없으면 `[]` |

판정 뒤에 Instruct 4개가 판정별 후속 문서를 쓴다(채점 대상 아님): 지급 검토 메모, 선주에게 보내는 영문 보완 요청 서신 초안, 기한 위험 메모, 검토 필요 메모. 대상 밖 문서는 미분류 안내로 간다.

## 7. 워크플로

Parse(OCR 강제) → Classify(분할 후 분류, 6종 + Other) → Extract × 6 → Merge → Instruct(판정) → Instruct × 4(후속 문서) / Other → Instruct(미분류 안내).

- 주최 측 예시팀 워크플로와 같은 뼈대다. Validate 노드는 쓰지 않았다. 날짜 비교와 누락 판정을 Validate로 옮길 수 있는지는 오피스아워 질문으로 남아 있다.
- Studio 워크플로: https://studio.upstage.ai/agents/agt_PwGSpcwWfFRCqXPfkjCpX8 · 제출 설정은 #4.
- 라이브러리 링크(승인 대기 중): https://studio.upstage.ai/library/agt_4GHMtEjnPkTQzV9KnQgXzn

## 8. 출발한 카드

Use Case Explorer `U038 컨테이너 지체료 무료기간 검산`(물류·운송, 대조) [14].

바꾼 점: 화물을 컨테이너에서 원유 유조선으로, 판정을 금액 검산에서 증빙 완결성·서명·청구 기한·일시 일치로 바꿨다. 문서 3종 → 6종. 카드 예외 3개 대신 무서명, 무서명 + 항의서, 기한 경계값, 다른 선박 서류, 가려진 스캔, 다른 터미널 양식을 더했다.

## 9. 테스트 데이터와 결과

청구 10건, 서류 51개. 유형은 단순 28, 여러 양식 8, 예외 10, 저품질 6(한 건은 두 유형에 함께 들어간다).

| 세트 | 상황 | 정답 |
|---|---|---|
| set01 | 서류 완비 | 지급 검토 가능 |
| set02 | 펌핑 기록 터미널 서명 없음, 항의서 없음 | 보완 요청 |
| set03 | 기한일 하루 뒤 접수 (약한 스캔본 포함) | 기한 위험 |
| set04 | 기한 당일 접수 (약한 스캔본 포함) | 지급 검토 가능 |
| set05 | 도착 통지서 누락 (다른 터미널 양식) | 보완 요청, `["Notice of Readiness"]` |
| set06 | 터미널 서명 없음 + 항의서 첨부 | 검토 필요 |
| set07 | 청구서 일시가 시간 기록보다 6시간 늦음 (다른 터미널 양식) | 검토 필요 |
| set08 | 다른 선박의 펌핑 기록 혼입 | 검토 필요 |
| set09 | 기울고 흐린 스캔, 호스 분리 일시가 가려짐 | 검토 필요 |
| set10 | 다른 터미널 양식, 관계없는 영수증 포함 | 지급 검토 가능 |

**실행 결과**

- 설정 #2: 9/10. set03이 `검토 필요`로 나왔다. 추출 단계가 깨끗하지만 빽빽한 펌핑 기록을 판독 불가로 표시했기 때문이다.
- 설정 #3: 펌핑 기록에서 판독 표시 항목을 빼고 10/10.
- 설정 #7(제출, 2026-11-26 오후): 판정 지시문에 값 공란·접수 기록 청구 번호 대조·중복 서류·청구서 부재 규약과 판정 순서 고정 문장을 더함. 제출 10건 두 번 20/20, 경계값 21건 세 번 64/64(네 키 기준, Studio 응답 원문, `work/runs/run09_v7_full.json`, `run10_v7_repeat.json`). 다른 노드는 #4와 같다.
- 설정 #4(이전 제출): 누락 목록을 JSON 배열로 고정. 2026-11-26에 현재 문서 10건 전체를 두 번 실행해 두 번 모두 `decision`과 `missing_documents`가 10/10 일치(서로 다른 실행 20건, `work/runs/run03_v4_full.json`, `run04_v4_repeat.json`).
- 청구 1건당 25~50초.

**결과의 한계**

- 문서와 정답지를 팀이 만들었다. 워크플로가 이 문서 양식에 맞춰졌을 수 있다. 정답지는 모델 출력이 아니라 규칙 코드(`work/gen/cases.py`)에서 나온다.
- `reason` 문장은 정답지와 자동 대조하지 않았다. 운영진의 LLM 채점 결과는 알 수 없다.
- 두 번 일치가 운영진 재실행에서도 같다는 보장은 아니다. 판정 노드가 언어 모델이다.
- 판정 노드 결과 화면에서 키 5개 뒤에 판정값이 한 줄 더 붙는다. 채점기가 이를 어떻게 읽는지 확인하지 못했다.
- (해결) 게시물 설정 창의 "#1 게시됨"은 게시본(복사본) 안의 설정 번호다. 게시본의 내용이 제출 설정과 같음을 대조했다.

## 10. 남은 결정

- 멘토 답에 따라 무서명 + 항의서 기준을 바꿀지 (지금은 `검토 필요`).
- 필수 서류 5종 목록의 근거를 발표에서 어떻게 말할지 (지금은 "팀이 정한 접수 기준, 판결에서 문제가 된 서류와 겹침").
- Validate 노드로 옮길지 (오피스아워 답 이후).

## 출처

### 근거로 쓰는 공식 문서

판결문은 영국 국립기록원(The National Archives) 공개본이다.

1. The Adventure 판결문 8문단이 인용한 BPVOY4 19.7조·20.1조 — https://caselaw.nationalarchives.gov.uk/ewhc/comm/2015/318
3. Kassiopi Maritime Co Ltd v Fal Shipping Co Ltd (The Adventure) [2015] EWHC 318 (Comm) — https://caselaw.nationalarchives.gov.uk/ewhc/comm/2015/318
4. Waterfront Shipping Co Ltd v Trafigura AG (The Sabrewing) [2007] EWHC 2482 (Comm) — https://caselaw.nationalarchives.gov.uk/ewhc/comm/2007/2482
5. Lukoil Asia Pacific Pte Ltd v Ocean Tankers (Pte) Ltd (The Ocean Neptune) [2018] EWHC 163 (Comm) — https://caselaw.nationalarchives.gov.uk/ewhc/comm/2018/163
6. "Amalie Essberger" Tankreederei GmbH & Co KG v Marubeni Corporation [2019] EWHC 3402 (Comm) — https://caselaw.nationalarchives.gov.uk/ewhc/comm/2019/3402
10. Tricon Energy Ltd v MTM Trading LLC (MTM Hong Kong) [2020] EWHC 700 (Comm) — https://caselaw.nationalarchives.gov.uk/ewhc/comm/2020/700
14. Upstage Studio Use Case Explorer — https://studio-usecase-explorer.vercel.app
15. ASBATANKVOY 6조(도착 통지 후 6시간)를 인용한 Front Commander 판결 — https://caselaw.nationalarchives.gov.uk/ewca/civ/2006/944
16. Shellvoy 5 15(3)조(60일 통지, 90일 서류)를 인용한 AET v Arcadia (Eagle Valencia) [2010] EWCA Civ 713 — https://caselaw.nationalarchives.gov.uk/ewca/civ/2010/713
17. Saudi Aramco Ports and Terminals – Rules, Regulations and General Information, 2025 Edition, General Rules (§4.6, §6.3.2, §7.2, §11.1.2) — https://www.aramco.com/-/media/downloads/working-with-us/ports-and-terminals-july-2025/02a--general-rules-and-information-compressed.pdf · 안내 페이지 https://www.aramco.com/en/what-we-do/operations/ports-and-terminals
16b. 같은 규정집의 Forms and Documents 섹션(Form 1~43, 46) — https://www.aramco.com/-/media/downloads/working-with-us/ports-and-terminals-july-2025/02b--forms-compressed.pdf
18. Aramco Annual Report 2025, Results 섹션 (p.57, p.62) — https://www.aramco.com/-/media/publications/corporate-reports/reports-and-presentations/2025/fy/sections/ara-2025-results-english.pdf
19. S-OIL 2024 사업보고서 (p.28, p.159, p.337) — https://www.s-oil.com/common/page/FileDownload.aspx?FileName=638785171900103493.pdf&PathType=BOARD&TFileName=2024+%EC%82%AC%EC%97%85%EB%B3%B4%EA%B3%A0%EC%84%9C.pdf&PIndex=6
20. S-OIL 회사 소개(온산 정제 능력) — https://s-oil.com/en/company/Company.aspx
21. S-OIL 보도자료, 20년 장기 원유 공급 계약 (2012-02-09) — https://www.s-oil.com/en/relation/NewsView.aspx?PageNo=24&SCategory=&SType=&SWord=&BoardDataIndex=12613
23. Bahri Annual Report 2025 — https://www.bahri.sa/media/tn5n3xus/2025_bahri_annual_report_english-pdf.pdf
24. Bahri 연결재무제표 FY2025 (수익 인식 §4.2, Note 8, 특수관계자 주석) — https://www.bahri.sa/media/z0ehqyl5/consolidated-financial-statements-and-independent-auditor-s-report-for-the-year-ended-31-december-2025.pdf

### 쓰지 않는 자료 (조사 기록)

발표와 설계의 근거로 쓰지 않는다. 번호는 v1과 같게 두었다.

2. BPVOY4 Voyage Charter Party 전문의 제3자 사본 — https://silo.tips/download/bpvoy4-voyage-charter-party · BP 공식 호스팅본은 찾지 못했다. 6.3조, 7.3.2조, 19.6조처럼 판결문에 인용되지 않은 조문은 이 사본에서만 봤으므로 근거로 쓰지 않는다.
7. Skuld P&I, "Timebar for demurrage claims" (2015-05-27) — https://www.skuld.com/topics/legal/pi-and-defence/timebar-for-demurrage-claims/
8. Steamship Mutual, The Adventure 해설 (2015-03) — https://www.steamshipmutual.com/publications/articles/adventureperilstimebars0315
9. Steamship Mutual, "Demurrage time bars FAQs" (2024-08-07) — https://www.steamshipmutual.com/publications/articles/demurrage-time-bars-faqs
11. Marcura, 체선료 스프레드시트와 소프트웨어 비교 글 — https://marcura.com/resources/blog/demurrage-spreadsheets-vs-software
12. Marcura, 체선료 청구 누수 글 — https://marcura.com/blog/demurrage-claims-leakage
13. Hellenic Shipping News (2023-08-29), 소프트웨어 회사 발표 게재 — https://www.hellenicshippingnews.com/?p=1000236
22. Argus Tanker Freight, Issue 25-144 (2025-07-24), 초대형 유조선 체선료 하루 USD 45,000 — https://view.argusmedia.com/rs/584-BUW-606/images/APAC-EVNT-PRO-2025-06-27-SIN-BIO-Argus-Biofuels-Forum-Argus%20Tanker%20Freight.pdf?version=0

### 이전 메모에서 틀렸던 것

- "The Ocean Neptune (Lia Oil v ERG Petroli)"는 틀린 이름이었다. 올바른 사건명은 5번이다.
- "BPVOY4 19.7조에 터미널 서명 거부 시 항의서로 대체" — 틀림. BPVOY3 16조(a)의 문구이고, 원문은 "거부"가 아니라 터미널이나 용선자 대표의 "서명이 없을 때"다.
- "BPVOY4 19.7조가 체선료 청구의 필수 증빙 목록" — 부정확. 화물 작업 추가 시간 청구의 증빙 조항이고, 체선료 청구 일반은 20.1조의 "all supporting documentation"이 기준이다.
- The Sabrewing은 BPVOY4가 아니라 BPVOY3 사건이고, 터미널 서명만이 아니라 서명이 전혀 없었다.
- 금액은 반올림 표기였다. 위 표가 판결문 기준이다.
- "Aramco 터미널 서식집에 도착 통지서·화물 기록 양식이 있어 그대로 본뜰 수 있다" — 틀림. 규정집 양식은 Aramco가 작성하는 것이고, 도착 통지서·시간 기록·펌핑 기록 양식은 없다.
- "Aramco Trading 하루 약 600만 배럴" — 2023년 수치. 2025년 공식 수치는 원유 수출 630만, 거래 740만 배럴이다.
- S-OIL 지분은 출처에 따라 61.6%(Aramco)와 63.41%(S-OIL, 보통주)로 다르다.
- v1은 필수 서류 5종의 근거로 P&I 클럽 권고 목록을 들었다. 공식 문서가 아니므로 v2에서는 "팀이 정한 접수 기준"으로 고쳐 적었다.
- v2 초안은 "Aramco는 체선료 청구를 받는 당사자다", "The Amalie Essberger는 선주 승소", "화주가 한 푼도 내지 않았다"라고 적었다. 원문 대조 결과 셋 다 과장이었고 위와 같이 고쳤다.
- 연차보고서 쪽수를 p.61, p.56~57로 적었으나 p.62, p.57이 맞다.
- Aramco와의 연결을 S-OIL 지분으로 설명했으나 업무와의 연결이 약해, Bahri의 재무제표와 연차보고서로 바꿨다(2026-11-26).
