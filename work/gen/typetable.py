"""유형표 템플릿에 문서 1건당 1줄을 채워 submission/에 저장한다.

    uv run python work/gen/typetable.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).parent))

from cases import CASES, answer  # noqa: E402
from docs import NAMES  # noqa: E402

TEMPLATE = next((ROOT / "docs" / "reference" / "templates").glob("*/*유형표*.xlsx"))
SIMPLE, FORMS, EDGE, POOR = "① 단순", "② 여러 양식", "③ 예외", "④ 저품질"
FIRST_ROW = 2
DEFAULT = {
    "invoice": "청구 번호 · 선박명 · 양하 완료 일시 추출",
    "receipt": "접수일과 기한일을 서로 바꾸지 않고 추출",
    "nor": "도착 · 통지 일시와 선장 서명 추출",
    "sof": "시간 기록 표에서 Hoses Disconnected 일시 추출 (Completed Discharge와 구분)",
    "pumping_log": "터미널 서명란의 서명 유무 판독",
    "lop": "항의서 분류와 주제 추출",
    "other": "대상 밖 문서를 Other로 분류",
}
ALT = "다른 터미널 양식 · 날짜 표기(14 Sep 2026 / 0505 hrs)를 같은 형식으로 정규화"
SPECIAL = {
    ("A", "invoice"): (SIMPLE, "기본 추출, 한 PDF에 든 서류 5종 분류"),
    ("B", "pumping_log"): (EDGE, "터미널 서명 없음 + 항의서 없음 → 보완 요청"),
    ("C", "receipt"): (EDGE, "접수일이 기한일 하루 뒤 → 기한 위험"),
    ("C", "nor"): (POOR, "살짝 기운 스캔본에서 도착 · 통지 일시 읽기"),
    ("C", "sof"): (POOR, "살짝 기운 스캔본의 번호 칸에서 15번 일시를 읽고, 읽히는데도 검토 필요로 넘기지 않는지"),
    ("D", "receipt"): (EDGE, "접수일 = 기한일(경계값)을 기한 내로 보는지"),
    ("D", "nor"): (POOR, "살짝 기운 스캔본에서 선장 서명과 일시 읽기"),
    ("D", "pumping_log"): (POOR, "스캔본의 촘촘한 표 아래에서 터미널 서명이 있음을 읽는지"),
    ("E", "invoice"): (EDGE, "도착 통지서 미제출 → 누락 서류 이름을 기록하고 보완 요청"),
    ("E", "sof"): (FORMS, ALT + ", 표 구성이 다른 Port Log 양식"),
    ("E", "pumping_log"): (FORMS, ALT),
    ("F", "pumping_log"): (EDGE, "터미널 서명 없음 + 항의서 첨부 → 통과로 단정하지 않고 검토 필요"),
    ("F", "lop"): (EDGE, "항의서를 서명의 대체로 추측하지 않는지 (계약에 명시 없음)"),
    ("G", "invoice"): (EDGE, "청구서의 양하 완료 일시가 시간 기록보다 6시간 늦음 → 검토 필요"),
    ("G", "nor"): (FORMS, ALT),
    ("G", "sof"): (FORMS + " · " + EDGE, "다른 양식의 날짜 표기를 정규화한 뒤 청구서 일시와 다름을 잡는지"),
    ("G", "pumping_log"): (FORMS, ALT),
    ("H", "pumping_log"): (EDGE, "다른 선박 · 항차의 서류 혼입 → 추측하지 않고 검토 필요"),
    ("I", "sof"): (POOR, "기울고 흐린 스캔, 일시 한 칸이 가려짐 → 추측하지 않고 검토 필요"),
    ("I", "pumping_log"): (POOR, "기울고 흐린 스캔에서 서명 유무 판독"),
    ("J", "nor"): (FORMS, ALT),
    ("J", "sof"): (FORMS, ALT + ", 표 구성이 다른 Port Log 양식"),
    ("J", "pumping_log"): (FORMS, ALT),
    ("J", "other"): (EDGE, "대상 밖 문서(급수 영수증) → Other로 분류, 판정에 영향 없음"),
}


def rows(prefix: str) -> list[list]:
    result = []
    for number, case in enumerate(CASES, 1):
        decision = answer(case, NAMES)["decision"]
        for page, kind in enumerate(case["docs"], 1):
            kind_type, purpose = SPECIAL.get((case["case_id"], kind), (SIMPLE, DEFAULT[kind]))
            result.append([len(result) + 1, f"{prefix}set{number:02d}.pdf", str(page),
                           f"{case['case_id']} {case['claim_no']}", NAMES[kind], kind_type, purpose, decision])
    return result


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    team = json.loads((ROOT / "team.json").read_text(encoding="utf-8"))
    prefix = f"{team['team']}_{team['phase']}_"
    book = load_workbook(TEMPLATE)
    sheet = book["유형표"]
    sheet.delete_rows(FIRST_ROW, sheet.max_row)
    lines = rows(prefix)
    for line in lines:
        sheet.append(line)
    target = ROOT / "submission" / f"{prefix}유형표.xlsx"
    book.save(target)
    counts = {kind: sum(1 for line in lines if kind in line[5]) for kind in (SIMPLE, FORMS, EDGE, POOR)}
    print(f"만들었습니다: {target} ({len(lines)}줄, {counts})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
