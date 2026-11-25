from __future__ import annotations

import copy

import pytest

TEAM, PHASE = "에너지팀", "최종제출"


def make_answer() -> dict:
    cases = [
        {
            "case_id": case_id,
            "file": f"{TEAM}_{PHASE}_set0{index}.pdf",
            "documents": ["작업허가서", "가스측정기록", "교육이수증", "작업계획서"][:count],
            "answer": {"decision": decision, "permit_no": f"PTW-00{index}", "missing_documents": missing},
        }
        for index, (case_id, count, decision, missing) in enumerate(
            [("A", 4, "적격", []), ("B", 4, "부적격", []), ("C", 2, "검토 필요", ["교육이수증"])], start=1
        )
    ]
    return {
        "task": "안전작업허가서 적격 심사",
        "unit": "허가 신청 1건 = 케이스 1건",
        "output_keys": ["decision", "permit_no", "missing_documents"],
        "decision_values": ["적격", "부적격", "검토 필요"],
        "cases": cases,
    }


@pytest.fixture
def answer() -> dict:
    return copy.deepcopy(make_answer())
