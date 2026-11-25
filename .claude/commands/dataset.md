---
description: 케이스를 구성하고 문서 PDF·정답지·유형표 초안을 만든다
argument-hint: "[추가하거나 바꿀 케이스]"
---

`docs/brief.md`, `docs/design.md`, `team.json`을 읽고 데이터셋을 만든다. 추가 조건: $ARGUMENTS

데이터 영역이 온라인 평가 100점 중 40점이다 (문서 생성 15, 케이스 구성 15, 정답지 품질 10).

**1. 케이스 표를 먼저 보여주고 승인받는다.** 문서를 만들기 전에 표로: case_id / 들어가는 문서 종류 / 유형(①~④) / 시험 목적 / 기대 판정.

- 문서 건수는 케이스 안의 문서 종류를 각각 1건으로 세어 10건 이상
- 유형 ①~④ 중 3가지 이상. 유형 이름은 `docs/reference/`의 유형표 템플릿에서 확인한다. 템플릿이 없으면 사용자에게 LMS에서 받아 달라고 하고, `② 여러 양식`·`④ 저품질` 외의 이름은 지어내지 않는다.
- 판정 값마다 케이스가 적어도 하나, `검토 필요`가 나오는 케이스 포함
- `docs/design.md`의 예외 경로마다 그것을 시험하는 케이스가 하나씩
- 대상 밖 문서(Classify의 Other)가 섞인 케이스 하나

**2. 문서를 만든다.** `work/html/`에 문서마다 HTML 파일을 쓴다.

- 실제 업무 양식처럼 만든다: 문서 번호, 발행처, 작성·승인란, 표, 단위, 날짜, 도장·서명 자리. energy-researcher가 찾은 공개 양식의 칸 구성을 따른다.
- 같은 종류의 문서도 케이스마다 양식을 다르게 한다 (발행처가 다르면 레이아웃·용어·날짜 표기·단위가 다르다). "여러 양식" 유형의 점수가 여기서 나온다.
- 회사·사람·번호는 모두 가상으로 만든다. 실제 회사 로고와 실존 인물 이름은 쓰지 않는다.
- 문서 안의 값과 정답이 어긋나지 않게, 케이스 표의 기대 판정에서 거꾸로 값을 정한다.

**3. PDF로 만든다.**
```bash
uv run python tools/pdfkit.py html2pdf work/html/<문서>.html work/pdf/<문서>.pdf
uv run python tools/pdfkit.py degrade work/pdf/<문서>.pdf work/pdf/<문서>_scan.pdf   # 저품질 유형
uv run python tools/pdfkit.py merge submission/<팀명>_<단계>_set01.pdf work/pdf/a.pdf work/pdf/b.pdf
```
파일명은 `team.json`의 팀명·단계로 가이드 규칙 그대로 붙인다. 만든 PDF 중 두세 개를 직접 열어 깨진 글자나 잘린 표가 없는지 확인한다.

**4. 정답지와 유형표 초안.** `submission/<팀명>_<단계>_answer.json`을 쓰고, 유형표는 템플릿 xlsx가 있으면 그 시트에 채우고 없으면 `work/유형표_초안.csv`로 만든다.

**5. 검증.** `uv run python tools/check_submission.py`를 돌리고, answer-auditor 에이전트로 정답을 독립적으로 다시 도출해 대조한다. 결과를 그대로 보여준다.

문서가 진짜 업무 양식처럼 보이는지는 사용자가 최종 판단한다. 판단할 수 있게 PDF 경로를 알려준다.
