"""제출 데이터셋에 없는 조합으로 워크플로를 다시 시험하기 위한 문서 묶음을 만든다.

제출물(submission/)은 건드리지 않고 work/probes/ 에만 쓴다.

    uv run python work/gen/probes.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(Path(__file__).parent))

import pdfkit  # noqa: E402
from build import SCAN  # noqa: E402
from cases import FULL, answer, finish  # noqa: E402
from docs import NAMES, RENDERERS  # noqa: E402

OUT = ROOT / "work" / "probes"
YEOSU = {"style": "alt", "terminal": "Yeosu Oil Jetty No. 4, Yeosu (fictional)", "terminal_rep": "Park J. W."}

# (id, 선박, 항차, 도착, 대기 시간, 양하 시간, 접수까지 일수, 차이)
PLAN = [
    ("P1", "MT SOBAEK DAWN", "SD-2701", "2026-08-03 05:10", 50, 52, 40,
     {"docs": ["invoice", "receipt", "nor", "pumping_log"]}),
    ("P2", "MT GAYA LANTERN", "GL-2702", "2026-07-21 14:00", 57, 50, 95,
     {"docs": ["invoice", "receipt", "nor", "sof"]}),
    ("P3", "MT MUDEUNG HARBOR", "MH-2703", "2026-07-24 08:20", 60, 49, 93,
     {"pump_signed": False}),
    ("P4", "MT ODAE MERIDIAN", "OM-2704", "2026-08-11 19:40", 48, 54, 37,
     {"docs": ["invoice", "receipt", "pumping_log"]}),
    ("P5", "MT BUKHAN CURRENT", "BC-2705", "2026-08-18 01:15", 53, 51, 31,
     {"doc_overrides": {"nor": {"voyage": "BC-2699"}}}),
    ("P6", "MT WOLCHUL ANCHOR", "WA-2706", "2026-07-19 10:30", 62, 50, 92,
     {"invoice_shift_hours": 3}),
    ("P7", "MT CHIAK LEDGER", "CL-2707", "2026-08-22 16:45", 46, 53, 29,
     {"degrade": ["nor", "pumping_log"], "scan": "heavy"}),
    ("P8", "MT GYERYONG TIDE", "GT-2708", "2026-08-29 07:05", 59, 52, 33,
     {**YEOSU, "pump_signed": False, "docs": FULL + ["lop"]}),
    # 2차: 지시문이 명시적으로 다루지 않는 입력
    ("Q1", "MT NAEJANG SIGNAL", "NS-2709", "2026-08-06 12:25", 51, 50, 36,
     {"docs": ["invoice", "nor", "sof", "pumping_log"]}),                      # 접수 기록 없음
    ("Q2", "MT DEOGYU COMPASS", "DC-2710", "2026-08-09 21:50", 56, 53, 34,
     {"docs": ["receipt", "nor", "sof", "pumping_log"]}),                      # 청구서 없음
    ("Q3", "MT SONGNI BEACON", "SB-2711", "2026-08-13 03:35", 49, 51, 32,
     {"docs": FULL + ["sof"]}),                                                # 같은 서류 두 장
    ("Q4", "MT JUWANG KEEL", "JK-2712", "2026-08-16 15:10", 58, 52, 30,
     {"docs": ["invoice", "receipt", "nor", "sof", "lop"]}),                   # 항의서만 있고 펌핑 기록 없음
    ("Q5", "MT BYEONSAN RUDDER", "BR-2713", "2026-08-20 09:00", 54, 49, 28,
     {"docs": ["pumping_log", "sof", "nor", "receipt", "invoice"]}),           # 서류 순서가 뒤집힘
]


def build(case: dict) -> dict:
    parts = []
    for kind in case["docs"]:
        view = {**case, **case["doc_overrides"].get(kind, {})}
        html = OUT / "html" / f"{case['case_id']}_{kind}.html"
        html.parent.mkdir(parents=True, exist_ok=True)
        html.write_text(RENDERERS[kind](view), encoding="utf-8")
        pdf = pdfkit.html2pdf(html, OUT / "pdf" / f"{case['case_id']}_{kind}.pdf")
        if kind in case["degrade"]:
            pdf = pdfkit.degrade(pdf, pdf.with_name(pdf.stem + "_scan.pdf"), **SCAN[case["scan"]])
        parts.append(pdf)
    name = f"probe_{case['case_id']}.pdf"
    pdfkit.merge(OUT / name, parts)
    return {"case_id": case["case_id"], "file": name, "documents": [NAMES[k] for k in case["docs"]],
            "answer": answer(case, NAMES)}


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    cases = [build(finish(plan, 20 + index)) for index, plan in enumerate(PLAN)]
    (OUT / "probe_answer.json").write_text(json.dumps(cases, ensure_ascii=False, indent=2), encoding="utf-8")
    for case in cases:
        a = case["answer"]
        print(case["file"], a["claim_no"], a["decision"], a["missing_documents"], "|", a["reason"][:60])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
