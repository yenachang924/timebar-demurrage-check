# 브리프 — 유조선 체선료 청구 서류 검증 (TimeBar)

상태: v1 · 2026-11-25. 주제와 팀명은 사용자가 확정(디스코드 게시). 판정 기준 3번은 조사 결과에 따라 (가)로 확정.
출처 표기: 각 사실 뒤 `[번호]`는 맨 아래 출처 목록의 번호다. 목록의 URL은 조사 에이전트가 2026-11-25에 실제로 연 페이지다. 인용문을 원문 PDF와 글자 단위로 대조하지는 않았다.

## 1. 누구의 어떤 순간인가

- 직무: 원유·제품을 배로 실어 보내는 화주(용선자) 쪽 체선료 정산 담당자.
- 순간: 양하가 끝난 뒤 선주가 체선료 청구서와 증빙 묶음을 보내왔을 때.
- 지금 방식: 담당자가 청구서를 용선계약 조항, 도착 통지서, 항만 시간 기록, 펌핑 기록과 눈으로 맞춰 보고 지급·보완 요청·거절을 정한다. (현업 확인 `미확인` — 11/26 Aramco 멘토에게 물을 것)

## 2. 문서

| 문서 | 보는 값 |
|---|---|
| 체선료 청구서 (Demurrage Claim Invoice) | 청구 번호, 선박명, 항차, 양하 완료 일시, 청구 금액 |
| 접수 기록 (Claim Receipt Record, 화주 측 대장) | 양하 완료 일시, 기한일(90일), 접수일 |
| 도착 통지서 (Notice of Readiness) | 도착·통지 일시, 선장 서명 |
| 항만 시간 기록 (Statement of Facts) | 도착, 접안, 호스 연결·분리 일시, 선장·터미널 서명 |
| 펌핑 기록 (Cargo Pumping Log) | 시간대별 압력·유량, 본선 사관·터미널 서명 |
| 항의서 (Letter / Note of Protest) | 사유, 발행 일시 |

실무에서 체선료 청구에 붙이라고 권고되는 서류 목록(도착 통지서, 항의서, 타임시트, 시간 기록, 양하 기록, 펌핑 기록, 포트 로그)은 P&I 클럽 자료에 있다 [8][9]. BPVOY4 자체는 이 목록을 열거하지 않는다(4번 참고).

## 3. 판정

청구 건 하나(서류 묶음 PDF 1개)에 대해 지급 검토로 넘겨도 되는지 판정한다.

- `지급 검토 가능` — 서류·서명·기한·일시가 모두 맞음
- `보완 요청` — 필수 서류 누락 또는 서명 없음(기한은 남아 있음)
- `기한 위험` — 접수일이 기한일을 넘김
- `검토 필요` — 서류 간 일시 불일치, 판독 불가, 다른 선박 서류 혼입

자동 "부인"은 내지 않는다. 같은 유형의 다툼에서 선주가 이긴 판결도 있기 때문이다 [6].

## 4. 판정 기준

1. **청구 기한**: 청구와 증빙이 양하 완료 후 90일 안에 용선자에게 도착해야 한다. 넘기면 용선자는 책임에서 벗어난다("discharged and released from all liability"). — BPVOY4 20.1조 [1][2]
2. **증빙 완비**: 20.1조는 청구의 모든 구성 부분을 입증하는 "all supporting documentation"을 요구한다. 법원은 이를 필수 서류 몇 가지로 한정하지 않았다 [3][7]. 필수 5종(청구서, 접수 기록, 도착 통지서, 시간 기록, 펌핑 기록)은 P&I 클럽 권고 목록 [8][9]에서 고른 **우리 가상 화주사의 접수 기준**이다.
3. **펌핑 기록 서명**: 본선 선임사관과 터미널 대표가 서명한 펌핑 기록이 있어야 한다. — BPVOY4 19.7.1조 [1][2]. 이 조항은 펌핑 등 화물 작업의 추가 시간 청구에 대한 것이다.
   - ⚠ "터미널 서명이 없으면 항의서로 대체한다"는 문구는 BPVOY4가 아니라 **BPVOY3 16조(a)**에 있다 [4]. BPVOY4 19.6조는 항의서(NOP)에 터미널 서명을 못 받으면 그 사실을 적은 추가 항의서를 내라는 규정이다 [2]. 그래서 무서명 + 항의서 첨부(set06)는 통과로 보지 않고 `검토 필요`로 넘긴다.
4. **일시 일치**: 청구서의 양하 완료 일시가 시간 기록의 호스 분리 일시와 같아야 한다. — 팀이 정한 기준(조항 근거 아님)
5. **동일 청구 건**: 서류의 선박명·항차가 청구서와 같아야 한다. — 팀이 정한 기준

판정 순서: 다른 선박 서류·판독 불가·일시 불일치·무서명 + 항의서 → `검토 필요` / 기준 1 위반 → `기한 위험` / 기준 2·3 위반 → `보완 요청` / 모두 통과 → `지급 검토 가능`.

참고(범위 밖): 정박 시간은 유효한 도착 통지서가 효력을 얻고 6시간 뒤, 또는 양하 개시 중 빠른 때에 시작한다(BPVOY4 7.3.2조) [2]. 체선 시간·금액 검산은 이 워크플로가 하지 않고 담당자에게 넘긴다.

## 5. 예외

- 누락: 빠진 서류 이름을 목록으로 내고 `보완 요청`. 기한이 지났으면 `기한 위험`.
- 불일치: 어느 서류의 어느 값이 다른지 내고 `검토 필요`.
- 저품질 스캔: 일시·서명을 읽지 못하면 추정하지 않고 `검토 필요`.
- 다른 선박·항차 서류 혼입: `검토 필요`.
- 대상 밖 문서: Other로 분류해 안내만 남기고 판정에 쓰지 않는다.

## 6. 왜 지금 방식으로는 안 되나

서류 한 가지 때문에 청구 전체가 사라진 영국 상사법원 판결이 있다.

| 사건 | 문제 서류 | 결과 | 청구액 |
|---|---|---|---|
| The Sabrewing, Waterfront Shipping v Trafigura [2007] EWHC 2482 (Comm), BPVOY3 [4] | 펌핑 기록에 본선·터미널 서명이 모두 없고 대신할 항의서도 없음 | 체선료 청구 전체 소멸 | USD 114,887.40 |
| The Adventure, Kassiopi Maritime v Fal Shipping [2015] EWHC 318 (Comm), 수정 BPVOY4 [3] | 항의서에 언급된 포트 로그·타임시트 미제출 | 청구 전체 소멸 | USD 364,847.78 |
| The Ocean Neptune, Lukoil Asia Pacific v Ocean Tankers [2018] EWHC 163 (Comm) [5] | 터미널이 연서한 시간 기록(또는 항의서) 미제출 | 기한 조항 적용, 소멸 | 선주 청구 USD 772,327.87 |
| MTM Hong Kong, Tricon Energy v MTM Trading [2020] EWHC 700 (Comm), 수정 Asbatankvoy [10] | 선하증권 사본 2건 미제출 | 청구 전체 소멸 | USD 56,049.36 |
| The Amalie Essberger [2019] EWHC 3402 (Comm) [6] | 펌핑 기록·항의서가 청구서에 첨부되지 않았다는 주장 | **선주 승소**(이미 기한 안에 따로 보냈음) | USD 154,875.00 |

- 90일 같은 짧은 기한과 상세 서류 요구는 유조선 거래에서 흔하고, 엄격히 지키지 않으면 청구가 실패하는 일이 잦다는 P&I 클럽 설명이 있다 [7]. 정성적 진술이다.
- 기한 초과·서류 미비 청구의 **비율 통계는 찾지 못했다**(`미확인`).
- "청구 1건에 3시간 이상", "한 포트폴리오에서 1년간 기한 실패 45만 달러", "시간 기록의 99%가 수기"는 모두 **출처를 밝히지 않은 벤더 주장**이다 [11][12][13]. 발표에 쓰려면 벤더 주장이라고 밝힌다.
- 담당자 한 사람의 처리 건수, Aramco 내부의 실제 절차: `미확인`.

## 7. 5패턴 중 무엇인가

대조 + 검증. Parse → Classify(분할 후 분류, 6종 + Other) → Extract ×6 → Merge → Instruct(청구_판정) → Instruct ×4(판정값별 후속 문서) / Other → Instruct(미분류_안내).
예시팀 워크플로와 같은 뼈대다. 검증(Validate) 노드 추가는 오피스아워 답을 보고 정한다.

## 8. 출발한 카드

Use Case Explorer `U038 컨테이너 지체료 무료기간 검산`(물류·운송, 대조) [14].
바꾼 점: 화물을 컨테이너에서 원유 유조선으로, 판정을 금액 검산에서 증빙 완결성·서명·청구 기한·일시 일치로 바꿈. 문서 3종 → 6종. 카드 예외 3개 대신 무서명, 항의서, 기한 경계값, 다른 선박 서류, 가려진 스캔, 다른 터미널 양식을 더함.

## 9. Studio에서 2일 안에 돌아가는가

Studio 실행은 아직 0회다. 가장 불확실한 것:

1. 직접 작성한 설정 JSON이 가져와지는가.
2. 서류 6종이 합쳐진 PDF가 쪽 단위로 나뉘는가, 한 건의 실행 시간이 시간초과 기준 안인가.
3. 스캔본에서 서명 유무와 가려진 칸이 의도대로 읽히는가.

## Aramco와의 연결

조사일 2026-11-25. 아래는 모두 1차 자료(aramco.com, s-oil.com, bahri.sa)나 가격 평가 기관 자료에서 확인한 것이다.

- **Aramco는 체선료 청구를 받는 당사자다.** Aramco 터미널 규정집(2025년판)에 선박이 "Saudi Aramco를 상대로 체선료 청구를 하는 경우" 느린 선적 속도를 정박 시간 가산 사유로 본다는 조항이 있다(§11.1.2). 24시간 전 도착 통지를 하지 않으면 허용 정박 시간이 늘어날 수 있다는 조항도 있다(§6.3.2) [17].
- **도착 통지서의 시각 규칙이 규정집에 있다.** 통지 시각은 이메일로 터미널 플래너와 대리점에 보내고, 항계 도착 전에는 통지할 수 없다(§7.2.1, §7.2.2) [17].
- **물량**: 2025년 Aramco 원유 수출 평균 하루 630만 배럴, 원유·제품 거래 평균 하루 740만 배럴(그룹 기준) [18].
- **하루 지연의 값**: 초대형 유조선 체선료는 중동→동아시아 항로 하루 USD 45,000, 대서양→아시아 하루 USD 60,000(Argus, 2025-07-24) [22]. 2026년 수치는 `미확인`.
- **한국 접점**: Aramco는 S-OIL 지분 61.6%를 보유(Aramco 2025 연차보고서 기준, S-OIL 공시의 보통주 기준은 63.41%)하고, 온산 정유소 정제 능력은 하루 669,000배럴이며, S-OIL은 Saudi Aramco와 20년 장기 원유 공급 계약(2012년 체결)을 맺고 있다 [18][19][20][21].
- **운송**: Aramco는 Bahri 지분 20%를 보유하고, Bahri는 도착지 인도 조건으로 팔리는 Aramco 원유의 독점 운송사다(초대형 유조선 50척). Bahri는 체선료를 추정이 필요한 변동 대가로 회계 처리하고, 2025년 연차보고서에서 문서·승인·보고 업무 자동화 방침을 밝혔다 [23][24].

**주의할 점**
- Aramco 규정집의 양식(Form 32 Protest Letter, Form 39 General and Cargo Log)은 **Aramco가 작성하는 터미널 측 양식**이다. 도착 통지서, 시간 기록, 펌핑 기록 양식은 규정집에 없다. 이 서류들은 선박·대리점 쪽 문서다. "Aramco 서식을 본떠 문서를 만들었다"고 말하면 안 된다 [16b].
- Aramco나 Aramco Trading의 체선료 청구 기한 조항, 터미널 서류 디지털화 발표는 찾지 못했다(`미확인`).
- "Aramco Trading 하루 약 600만 배럴"은 2023년 2월 CEO 발언으로 오래된 수치다. 쓰지 않는다.

## 사용자가 정해야 할 것

- 기준 3번(무서명 + 항의서): **(가)로 확정(2026-11-25)**. set06의 정답은 `검토 필요`. 항의서가 서명을 대신하는지는 BPVOY4에 명시가 없어 추측하지 않고 담당자에게 넘긴다.
- 판정값 4개와 판정 순서: `유지` / `다시`
- 자동 "부인"을 내지 않는 방침: `유지` / `다시`

## 출처

조사일 2026-11-25. 1차 = 판결문·계약 양식, 2차 = P&I 클럽·보험사 자료, 벤더 = 체선료 관리 소프트웨어 회사.

1. [1차] The Adventure 판결문 8문단이 인용한 BPVOY4 19.7조·20.1조 — https://caselaw.nationalarchives.gov.uk/ewhc/comm/2015/318
2. [1차 양식의 제3자 사본] BPVOY4 Voyage Charter Party, 1st Edition June 1998 (6.3, 7.3.2, 19.6, 19.7, 20.1, 20.2조) — https://silo.tips/download/bpvoy4-voyage-charter-party · BP/BIMCO 공식 호스팅본은 찾지 못함
3. [1차] Kassiopi Maritime Co Ltd v Fal Shipping Co Ltd (The Adventure) [2015] EWHC 318 (Comm) — https://caselaw.nationalarchives.gov.uk/ewhc/comm/2015/318
4. [1차] Waterfront Shipping Co Ltd v Trafigura AG (The Sabrewing) [2007] EWHC 2482 (Comm) — https://caselaw.nationalarchives.gov.uk/ewhc/comm/2007/2482
5. [1차] Lukoil Asia Pacific Pte Ltd v Ocean Tankers (Pte) Ltd (The Ocean Neptune) [2018] EWHC 163 (Comm) — https://caselaw.nationalarchives.gov.uk/ewhc/comm/2018/163
6. [1차] "Amalie Essberger" Tankreederei GmbH & Co KG v Marubeni Corporation [2019] EWHC 3402 (Comm) — https://caselaw.nationalarchives.gov.uk/ewhc/comm/2019/3402
7. [2차] Skuld P&I, "Timebar for demurrage claims" (2015-05-27) — https://www.skuld.com/topics/legal/pi-and-defence/timebar-for-demurrage-claims/
8. [2차] Steamship Mutual, The Adventure 해설 (2015-03) — https://www.steamshipmutual.com/publications/articles/adventureperilstimebars0315
9. [2차] Steamship Mutual, "Demurrage time bars FAQs" (2024-08-07) — https://www.steamshipmutual.com/publications/articles/demurrage-time-bars-faqs
10. [1차] Tricon Energy Ltd v MTM Trading LLC (MTM Hong Kong) [2020] EWHC 700 (Comm) — https://caselaw.nationalarchives.gov.uk/ewhc/comm/2020/700
11. [벤더] Marcura, 체선료 스프레드시트와 소프트웨어 비교 글 — https://marcura.com/resources/blog/demurrage-spreadsheets-vs-software
12. [벤더] Marcura, 체선료 청구 누수 글 — https://marcura.com/blog/demurrage-claims-leakage
13. [벤더 발표의 업계지 게재] Hellenic Shipping News (2023-08-29) — https://www.hellenicshippingnews.com/?p=1000236
14. Upstage Studio Use Case Explorer — https://studio-usecase-explorer.vercel.app
15. [1차] ASBATANKVOY 6조(도착 통지 후 6시간)를 인용한 Front Commander 판결 — https://caselaw.nationalarchives.gov.uk/ewca/civ/2006/944
16. [1차] Shellvoy 5 15(3)조(60일 통지, 90일 서류)를 인용한 AET v Arcadia (Eagle Valencia) [2010] EWCA Civ 713 — https://caselaw.nationalarchives.gov.uk/ewca/civ/2010/713
17. [1차] Saudi Aramco Ports and Terminals – Rules, Regulations and General Information, 2025 Edition, General Rules (§4.6, §6.3.2, §7.2, §11.1.2) — https://www.aramco.com/-/media/downloads/working-with-us/ports-and-terminals-july-2025/02a--general-rules-and-information-compressed.pdf · 안내 페이지 https://www.aramco.com/en/what-we-do/operations/ports-and-terminals
16b. [1차] 같은 규정집의 Forms and Documents 섹션(Form 1~43, 46) — https://www.aramco.com/-/media/downloads/working-with-us/ports-and-terminals-july-2025/02b--forms-compressed.pdf
18. [1차] Aramco Annual Report 2025, Results 섹션 (p.56~57, p.61) — https://www.aramco.com/-/media/publications/corporate-reports/reports-and-presentations/2025/fy/sections/ara-2025-results-english.pdf
19. [1차] S-OIL 2024 사업보고서 (p.28, p.159, p.337) — https://www.s-oil.com/common/page/FileDownload.aspx?FileName=638785171900103493.pdf&PathType=BOARD&TFileName=2024+%EC%82%AC%EC%97%85%EB%B3%B4%EA%B3%A0%EC%84%9C.pdf&PIndex=6
20. [1차] S-OIL 회사 소개(온산 정제 능력) — https://s-oil.com/en/company/Company.aspx
21. [1차] S-OIL 보도자료, 20년 장기 원유 공급 계약 (2012-02-09) — https://www.s-oil.com/en/relation/NewsView.aspx?PageNo=24&SCategory=&SType=&SWord=&BoardDataIndex=12613
22. [가격 평가 기관] Argus Tanker Freight, Issue 25-144 (2025-07-24), Demurrage 표 — https://view.argusmedia.com/rs/584-BUW-606/images/APAC-EVNT-PRO-2025-06-27-SIN-BIO-Argus-Biofuels-Forum-Argus%20Tanker%20Freight.pdf?version=0
23. [1차] Bahri Annual Report 2025 — https://www.bahri.sa/media/tn5n3xus/2025_bahri_annual_report_english-pdf.pdf
24. [1차] Bahri 연결재무제표 FY2025 (수익 인식 §4.2, Note 8, 특수관계자 주석) — https://www.bahri.sa/media/z0ehqyl5/consolidated-financial-statements-and-independent-auditor-s-report-for-the-year-ended-31-december-2025.pdf

### 이전 메모에서 틀렸던 것

- "The Ocean Neptune (Lia Oil v ERG Petroli)"는 틀린 이름이었다. 올바른 사건명은 5번이다.
- "BPVOY4 19.7조에 터미널 서명 거부 시 항의서로 대체" — 틀림. BPVOY3 16조(a)의 문구다.
- "BPVOY4 19.7조가 체선료 청구의 필수 증빙 목록" — 부정확. 화물 작업 추가 시간 청구의 증빙 조항이고, 체선료 청구 일반은 20.1조의 "all supporting documentation"이 기준이다.
- The Sabrewing은 BPVOY4가 아니라 BPVOY3 사건이고, 터미널 서명만이 아니라 서명이 전혀 없었다.
- 금액은 반올림 표기였다. 위 표가 판결문 기준이다.
- "Aramco 터미널 서식집에 도착 통지서·화물 기록 양식이 있어 그대로 본뜰 수 있다" — 틀림. 규정집 양식은 Aramco가 작성하는 것이고, 도착 통지서·시간 기록·펌핑 기록 양식은 없다.
- "Aramco Trading 하루 약 600만 배럴" — 2023년 수치. 2025년 공식 수치는 원유 수출 630만, 거래 740만 배럴이다.
- S-OIL 지분은 출처에 따라 61.6%(Aramco)와 63.41%(S-OIL, 보통주)로 다르다.
