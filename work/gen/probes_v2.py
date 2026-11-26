"""경계값 시험용 문서 묶음(R1~R8)을 만든다. Studio 담당자가 지시문 수정안을 시험할 때 쓴다.

제출물(submission/)과 1차 시험 문서(work/probes/)는 건드리지 않고 work/probes_v2/ 에만 쓴다.
기대값은 아래 HAND 표에 손으로 적었고, 정답 규칙(cases.answer)의 결과가 이 표와 다르면 파일을 만들지 않고 멈춘다.
이 기대값은 '지시문 수정안'을 전제로 한다. 제출된 설정 #4의 지시문에는 없는 규약이 섞여 있으므로
설정 #4의 실행 결과를 이 기대값으로 채점해 정확도로 쓰지 않는다.

    uv run python work/gen/probes_v2.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(Path(__file__).parent))

import pdfkit  # noqa: E402
from build import OUTPUT_KEYS, SCAN  # noqa: E402
from cases import DECISIONS, FULL, answer, doc_views, finish  # noqa: E402
from docs import NAMES, RENDERERS  # noqa: E402

OUT = ROOT / "work" / "probes_v2"
FIRST_NUMBER = 40  # 청구 번호가 제출 10건(0~9)·1차 시험(20~32)과 겹치지 않게 한다

# (id, 선박, 항차, 도착, 대기 시간, 양하 시간, 접수까지 일수, 차이)
PLAN = [
    ("R1", "MT GARIWANG LOG", "GL-2801", "2026-08-04 06:20", 52, 51, 38,
     {"doc_overrides": {"receipt": {"received_date": ""}}}),                       # 접수일 칸이 빈 접수 기록
    ("R2", "MT MINJUJI SPAN", "MS-2802", "2026-08-07 13:40", 55, 50, 36,
     {"doc_overrides": {"receipt": {"time_bar_date": ""}}}),                       # 기한일 칸이 빈 접수 기록
    ("R3", "MT DUTA HELM", "DH-2803", "2026-08-12 09:15", 49, 53, 33,
     {"doc_overrides": {"receipt": {"claim_no": "DMG-2026-0998"}}}),               # 다른 청구 번호의 접수 기록
    ("R4", "MT BANGTAE YARD", "BY-2804", "2026-08-15 18:05", 57, 52, 31,
     {"docs": FULL + ["sof"], "copy_overrides": {"sof": {"hoses_disconnected": "2026-08-20 09:15"}}}),  # 완료 시각이 다른 SOF 두 장
    ("R5", "MT HWAAK BOW", "HB-2805", "2026-07-30 04:50", 60, 50, 90,
     {"invoice_shift_hours": 4}),                                                  # 기한 당일 접수 + 일시 불일치
    ("R6", "MT GAJI STERN", "GS-2806", "2026-07-22 11:30", 54, 52, 93,
     {"pump_signed": False, "docs": FULL + ["lop"]}),                              # 기한 초과 + 무서명 + 항의서
    ("R7", "MT CHEONGTAE MAST", "CM-2807", "2026-08-19 20:25", 51, 54, 30,
     {"doc_overrides": {"invoice": {"invoice_completed": ""}}}),                   # 완료 일시 칸이 빈 청구서
    ("R8", "MT UNMUN DECK", "UD-2808", "2026-08-23 02:10", 58, 49, 28,
     {"doc_overrides": {"receipt": {"claim_no": ""}}}),                            # 청구 번호 칸이 빈 접수 기록
]

# 손으로 적은 기대값: (판정, 누락 목록). 지시문 수정안 기준.
HAND = {
    "R1": ("검토 필요", []), "R2": ("검토 필요", []), "R3": ("검토 필요", []), "R4": ("검토 필요", []),
    "R5": ("검토 필요", []), "R6": ("검토 필요", []), "R7": ("검토 필요", []), "R8": ("검토 필요", []),
}


def build(case: dict) -> dict:
    parts = []
    for index, (kind, view) in enumerate(doc_views(case), start=1):
        stem = f"{case['case_id']}_{index}_{kind}"  # 같은 종류가 두 장이어도 파일이 겹치지 않게 순번을 붙인다
        html = OUT / "html" / f"{stem}.html"
        html.parent.mkdir(parents=True, exist_ok=True)
        html.write_text(RENDERERS[kind](view), encoding="utf-8")
        pdf = pdfkit.html2pdf(html, OUT / "pdf" / f"{stem}.pdf")
        if kind in case["degrade"]:
            pdf = pdfkit.degrade(pdf, pdf.with_name(pdf.stem + "_scan.pdf"), **SCAN[case["scan"]])
        parts.append(pdf)
    name = f"probe2_{case['case_id']}.pdf"
    pdfkit.merge(OUT / name, parts)
    return {"case_id": case["case_id"], "file": name, "documents": [NAMES[k] for k in case["docs"]],
            "answer": answer(case, NAMES)}


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    planned = [finish(plan, FIRST_NUMBER + index) for index, plan in enumerate(PLAN)]
    computed = {case["case_id"]: answer(case, NAMES) for case in planned}
    wrong = {key: (computed[key]["decision"], computed[key]["missing_documents"]) for key, hand in HAND.items()
             if (computed[key]["decision"], computed[key]["missing_documents"]) != hand}
    if wrong or set(HAND) != set(computed):
        print(f"규칙의 결과가 손으로 적은 기대값과 다릅니다: {wrong}")
        return 1
    built = [build(case) for case in planned]
    sheet = {"task": "지시문 수정안 경계값 시험(제출 데이터셋 아님)", "unit": "청구 1건 = 파일 1개",
             "output_keys": OUTPUT_KEYS, "decision_values": DECISIONS, "cases": built}
    (OUT / "probe2_answer.json").write_text(json.dumps(sheet, ensure_ascii=False, indent=2), encoding="utf-8")
    for case in built:
        a = case["answer"]
        print(case["file"], a["claim_no"], a["decision"], a["missing_documents"], "|", a["reason"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
