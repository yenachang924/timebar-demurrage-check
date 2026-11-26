"""케이스 데이터로 문서 묶음 PDF와 정답지를 만든다.

    uv run python work/gen/build.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(Path(__file__).parent))

import pdfkit  # noqa: E402
from cases import CASES, DECISIONS, answer, doc_views  # noqa: E402
from docs import NAMES, RENDERERS  # noqa: E402

TASK = "유조선 체선료 청구 서류 검증 (가상 화주사 Daehan Energy Trading, BPVOY4 기준)"
UNIT = "청구 1건 = 파일 1개(서류 묶음 PDF) = 판정 1건"
SCAN = {"heavy": {"dpi": 110, "blur": 0.9, "tilt": 1.2}, "mild": {"dpi": 150, "blur": 0.5, "tilt": -0.8}}
OUTPUT_KEYS = ["claim_no", "vessel_name", "decision", "reason", "missing_documents"]


def build_case(case: dict, prefix: str, number: int) -> dict:
    parts = []
    for kind, view in doc_views(case):
        html = ROOT / "work" / "html" / f"{case['case_id']}_{kind}.html"
        html.parent.mkdir(parents=True, exist_ok=True)
        html.write_text(RENDERERS[kind](view), encoding="utf-8")
        pdf = pdfkit.html2pdf(html, ROOT / "work" / "pdf" / f"{case['case_id']}_{kind}.pdf")
        if kind in case["degrade"]:
            pdf = pdfkit.degrade(pdf, pdf.with_name(pdf.stem + "_scan.pdf"), **SCAN[case["scan"]])
        parts.append(pdf)
    name = f"{prefix}set{number:02d}.pdf"
    pdfkit.merge(ROOT / "submission" / name, parts)
    return {"case_id": case["case_id"], "file": name, "documents": [NAMES[k] for k in case["docs"]],
            "answer": answer(case, NAMES)}


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    team = json.loads((ROOT / "team.json").read_text(encoding="utf-8"))
    prefix = f"{team['team']}_{team['phase']}_"
    cases = [build_case(case, prefix, index) for index, case in enumerate(CASES, 1)]
    sheet = {"task": TASK, "unit": UNIT, "output_keys": OUTPUT_KEYS, "decision_values": DECISIONS, "cases": cases}
    target = ROOT / "submission" / f"{prefix}answer.json"
    target.write_text(json.dumps(sheet, ensure_ascii=False, indent=2), encoding="utf-8")
    for case in cases:
        print(case["case_id"], case["file"], case["answer"]["decision"], "|", case["answer"]["reason"])
    print(f"정답지: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
