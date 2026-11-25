# TimeBar — Tanker Demurrage Claim Evidence Check

[Aramco × KU × Upstage] 2026 Energy AI Workflow Hackathon 제출작 (팀 TimeBar, 1인팀).

원유 화물을 내린 뒤 선주가 화주에게 보내는 **체선료 청구 서류 묶음**을 화주 측 정산 담당자를 위해 검증하는 Upstage Studio 워크플로입니다. 금액을 다시 계산하지 않고, 청구의 효력이 갈리는 네 가지만 봅니다: 서류가 다 있는가, 서명이 있는가, 기한 안에 왔는가, 서류끼리 시각이 맞는가.

An Upstage Studio workflow that checks the evidence behind a tanker demurrage claim for the charterer's claims handler: completeness, signatures, the 90-day time bar (BPVOY4 cl. 20.1) and time consistency. It returns one of four decisions and drafts the next document.

## 워크플로

```
Parse (OCR) → Classify (6종 + Other) → Extract × 6 → Merge → Instruct 판정 → Instruct × 4 후속 문서
```

| 판정 | 조건 | 담당자가 받는 것 |
|---|---|---|
| 검토 필요 | 다른 선박 서류, 판독 불가, 시각 불일치, 무서명 + 항의서 | 어디를 봐야 하는지 적은 메모 |
| 기한 위험 | 접수일이 기한일보다 늦음 | 두 날짜를 적은 메모 |
| 보완 요청 | 필수 서류 누락, 터미널 서명 없음 | 선주에게 보내는 영문 서신 초안 |
| 지급 검토 가능 | 모든 확인 통과 | 확인한 사실을 적은 메모 |

판정은 위 순서대로 확인하며, 워크플로는 "거절"을 내지 않습니다. 출력 키는 `claim_no`, `vessel_name`, `decision`, `reason`, `missing_documents` 다섯 개입니다.

## 결과

- 테스트 데이터: 가상 청구 10건, 서류 51개 (단순 28, 여러 양식 8, 예외 10, 저품질 6). 모든 문서는 가상이며 실제 회사·선박과 무관합니다.
- 2026-11-26 Studio 설정 #4로 10건을 한 번에 실행: `decision`과 `missing_documents`가 10건 모두 정답지와 일치 (`work/runs/run03_v4_full.json`). `reason` 문장은 대조하지 않았습니다.
- 처음 전체 실행에서는 9/10이었습니다. 실패 원인과 수정은 `docs/decisions.md`에 있습니다.

## 폴더

| 경로 | 내용 |
|---|---|
| `submission/` | 제출물: 데이터셋 PDF 10개, 정답지, 유형표, 설계서, 워크플로 설정 JSON, 발표 자료, 데모 영상 |
| `work/gen/` | 테스트 문서·정답지·유형표·설계서·워크플로 설정·데모 영상을 만드는 코드 |
| `tools/` | 제출물 정합성 검사, 실행 결과 채점, PDF 도구 |
| `docs/` | 주제 브리프(출처 URL 포함), 결정 기록, 멘토링 질문, 영어 발표 원고 |
| `.claude/` | 작업에 쓴 Claude Code 서브에이전트와 명령 |

## 다시 만들기

```bash
uv sync
uv run python work/gen/build.py            # 데이터셋 PDF와 정답지
uv run python tools/check_submission.py    # 제출물 정합성 검사
uv run python tools/score.py work/runs/run03_v4_full.json
uv run pytest -q
```

`work/gen/workflow.py`와 `design_doc.py`는 주최 측이 배포한 예시 설정과 템플릿을 입력으로 쓰는데, 그 파일들은 재배포할 수 없어 이 저장소에 없습니다.

## AI 도구를 쓴 방식

- **Upstage Studio**가 문서를 읽고 판정합니다.
- **Claude Code**는 출처 조사, 테스트 문서 생성, 실행 결과 채점을 맡았습니다.
- 정답지는 어느 모델의 출력도 아닌 규칙 코드(`work/gen/cases.py`)에서 나옵니다.
- 판정 기준과 예외 처리 방침은 사람이 정했고, `docs/decisions.md`에 버전별로 남겼습니다.

## 출처

법적·시장 사실의 출처는 `docs/brief.md`에 URL과 함께 있습니다. 확인하지 못한 것(청구가 기한으로 거절되는 빈도, 수작업 검토 시간, Aramco 내부 절차)은 주장하지 않았습니다.
