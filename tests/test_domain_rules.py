"""정답 생성 규칙(work/gen/cases.py)의 도메인 회귀 시험.

기대값은 생성 규칙을 호출해 얻은 값이 아니라 사람이 판정 지시문을 읽고 손으로 적은 표다.
기준 케이스의 값도 finish()로 만들지 않고 set01(A) PDF에서 읽은 값을 그대로 적었다.
이 시험은 생성 규칙의 논리만 본다. Studio 워크플로의 실제 출력 정확도는 검증하지 않는다.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "work" / "gen"))

import cases as rules  # noqa: E402

NAMES = {
    "invoice": "Demurrage Claim Invoice", "receipt": "Claim Receipt Record", "nor": "Notice of Readiness",
    "sof": "Statement of Facts", "pumping_log": "Cargo Pumping Log", "lop": "Letter of Protest",
    "other": "Port Supply Receipt",
}
FULL = ["invoice", "receipt", "nor", "sof", "pumping_log"]
REVIEW, RISK, REQUEST, CLEAR = "검토 필요", "기한 위험", "보완 요청", "지급 검토 가능"

# set01(A)의 PDF 5쪽에서 읽은 값. 다른 문제 없이 기한 안에 접수된 완비 청구.
BASE = {
    "case_id": "T", "claim_no": "DMG-2026-0410", "vessel": "MT HANBIT PIONEER", "voyage": "HP-2608",
    "invoice_completed": "2026-08-14 17:30", "hoses_disconnected": "2026-08-14 17:30",
    "received_date": "2026-10-02", "time_bar_date": "2026-11-12",
    "pump_signed": True, "smudge": False, "docs": FULL, "doc_overrides": {},
}
OTHER_SHIP = {"vessel": "MT SEORAK SPIRIT", "voyage": "SS-2611"}
SAME_SHIP = {"vessel": "MT HANBIT PIONEER", "voyage": "HP-2608"}
ID = ("DMG-2026-0410", "MT HANBIT PIONEER")
NO_ID = ("", "")


def without(*kinds: str) -> list[str]:
    return [kind for kind in FULL if kind not in kinds]


# (이름, 기준 케이스와 다른 점, 기대 판정, 기대 누락 목록, 기대 (claim_no, vessel_name),
#  reason에 있어야 하는 말, reason에 있으면 안 되는 말)
TABLE = [
    ("기준: 완비·기한 내", {}, CLEAR, [], ID, ["2026-10-02", "2026-11-12"], []),
    # 빈 값: 서류는 있는데 필요한 값이 비어 있으면 누락이 아니라 검토 필요
    ("빈 접수일", {"received_date": ""}, REVIEW, [], ID, ["접수일"], ["기한 내 접수"]),
    ("빈 기한일", {"time_bar_date": ""}, REVIEW, [], ID, ["기한일"], ["늦음"]),
    ("접수일·기한일 모두 빈 값", {"received_date": "", "time_bar_date": ""}, REVIEW, [], ID, [], ["기한 내 접수"]),
    ("빈 청구서 완료 일시", {"invoice_completed": ""}, REVIEW, [], ID, [], []),
    # 정규화 실패: 문자열 대소 비교로 넘어가면 안 된다
    ("일·월 순서가 애매한 접수일", {"received_date": "02/10/2026"}, REVIEW, [], ID, [], ["기한 내 접수"]),
    ("자릿수가 다른 접수일(문자열 비교 함정)", {"received_date": "2026-9-30"}, REVIEW, [], ID, [], ["늦음"]),
    ("달력에 없는 기한일", {"time_bar_date": "2026-11-31"}, REVIEW, [], ID, [], []),
    ("정규화되지 않은 완료 일시", {"invoice_completed": "14 Aug 2026 / 1730 hrs"}, REVIEW, [], ID, [], []),
    # 식별자
    ("실제로 다른 선박의 펌핑 기록", {"doc_overrides": {"pumping_log": OTHER_SHIP}}, REVIEW, [], ID,
     ["MT SEORAK SPIRIT"], []),
    ("항차 번호만 다른 NOR", {"doc_overrides": {"nor": {"voyage": "HP-2599"}}}, REVIEW, [], ID, ["HP-2599"], []),
    ("원래 값과 같은 override", {"doc_overrides": {"nor": SAME_SHIP}}, CLEAR, [], ID, [], ["다름"]),
    ("청구 번호가 다른 접수 기록", {"doc_overrides": {"receipt": {"claim_no": "DMG-2026-0999"}}}, REVIEW, [], ID,
     ["DMG-2026-0999"], []),
    ("청구 번호가 빈 접수 기록", {"doc_overrides": {"receipt": {"claim_no": ""}}}, REVIEW, [], ID, [], []),
    # 누락: 없는 서류의 값은 쓰지 않는다
    ("접수 기록 없음", {"docs": without("receipt")}, REQUEST, ["Claim Receipt Record"], ID, [],
     ["기한 내 접수", "2026-10-02", "2026-11-12"]),
    ("접수 기록 없음(숨은 날짜는 기한 초과)", {"docs": without("receipt"), "received_date": "2026-12-01"}, REQUEST,
     ["Claim Receipt Record"], ID, [], ["2026-12-01", "늦음"]),
    ("청구서 없음", {"docs": without("invoice")}, REQUEST, ["Demurrage Claim Invoice"], NO_ID, [],
     ["DMG-2026-0410", "MT HANBIT PIONEER"]),
    ("청구서 없음(숨은 완료 일시는 다름)", {"docs": without("invoice"), "invoice_completed": "2026-08-14 23:30"},
     REQUEST, ["Demurrage Claim Invoice"], NO_ID, [], ["23:30"]),
    ("SOF 없음", {"docs": without("sof")}, REQUEST, ["Statement of Facts"], ID, [], ["일치"]),
    ("SOF 없음(숨은 smudge·다른 시각)", {"docs": without("sof"), "smudge": True,
                                  "hoses_disconnected": "2026-08-14 11:30"}, REQUEST, ["Statement of Facts"], ID, [],
     ["판독", "11:30"]),
    ("펌핑 기록 없음 + 항의서", {"docs": without("pumping_log") + ["lop"], "pump_signed": False}, REQUEST,
     ["Cargo Pumping Log"], ID, [], ["서명"]),
    ("서류 2종 누락", {"docs": without("nor", "sof")}, REQUEST, ["Notice of Readiness", "Statement of Facts"], ID, [], []),
    # 서명
    ("펌핑 기록 무서명, 항의서 없음", {"pump_signed": False}, REQUEST, [], ID, ["서명"], []),
    ("펌핑 기록 무서명 + 항의서", {"pump_signed": False, "docs": FULL + ["lop"]}, REVIEW, [], ID, ["Letter of Protest"], []),
    # 기한 경계
    ("기한 하루 전", {"received_date": "2026-11-11"}, CLEAR, [], ID, [], []),
    ("기한 당일", {"received_date": "2026-11-12"}, CLEAR, [], ID, [], []),
    ("기한 하루 뒤", {"received_date": "2026-11-13"}, RISK, [], ID, ["2026-11-13", "2026-11-12"], []),
    # 복합: 검토 필요 → 기한 위험 → 보완 요청 순서. 누락 목록은 상위 판정에서도 전부 적는다
    ("기한 초과 + NOR 누락", {"received_date": "2026-11-13", "docs": without("nor")}, RISK,
     ["Notice of Readiness"], ID, [], []),
    ("기한 초과 + 일시 불일치", {"received_date": "2026-11-13", "invoice_completed": "2026-08-14 23:30"}, REVIEW, [],
     ID, ["23:30"], []),
    ("기한 초과 + 무서명 + 항의서", {"received_date": "2026-11-13", "pump_signed": False, "docs": FULL + ["lop"]},
     REVIEW, [], ID, [], []),
    ("기한 당일 + 일시 불일치", {"received_date": "2026-11-12", "invoice_completed": "2026-08-14 23:30"}, REVIEW, [],
     ID, ["23:30"], []),
    ("일시 불일치 + NOR 누락", {"invoice_completed": "2026-08-14 23:30", "docs": without("nor")}, REVIEW,
     ["Notice of Readiness"], ID, [], []),
    # 중복: 같은 값이면 허용, 다르면 어느 쪽도 고르지 않고 검토 필요
    ("같은 SOF 두 장", {"docs": FULL + ["sof"]}, CLEAR, [], ID, [], []),
    ("완료 시각이 다른 SOF 두 장(뒤쪽이 다름)", {"docs": FULL + ["sof"],
                                     "copy_overrides": {"sof": {"hoses_disconnected": "2026-08-14 11:30"}}},
     REVIEW, [], ID, ["Statement of Facts"], []),
    ("완료 시각이 다른 SOF 두 장(뒤쪽이 청구서와 같음)", {"docs": FULL + ["sof"], "hoses_disconnected": "2026-08-14 11:30",
                                          "invoice_completed": "2026-08-14 17:30",
                                          "copy_overrides": {"sof": {"hoses_disconnected": "2026-08-14 17:30"}}},
     REVIEW, [], ID, [], []),
    ("기한일이 다른 접수 기록 두 장", {"docs": FULL + ["receipt"],
                            "copy_overrides": {"receipt": {"time_bar_date": "2026-09-01"}}}, REVIEW, [], ID, [], []),
    ("무관한 영수증 추가", {"docs": FULL + ["other"]}, CLEAR, [], ID, [], []),
]


def build(changes: dict) -> dict:
    return {**BASE, **changes}


@pytest.mark.parametrize("name,changes,decision,missing,identity,must,must_not", TABLE, ids=[row[0] for row in TABLE])
def test_hand_written_expectations(name, changes, decision, missing, identity, must, must_not):
    result = rules.answer(build(changes), NAMES)
    assert result["decision"] == decision
    assert result["missing_documents"] == missing
    assert (result["claim_no"], result["vessel_name"]) == identity
    for phrase in must:
        assert phrase in result["reason"], result["reason"]
    for phrase in must_not:
        assert phrase not in result["reason"], result["reason"]


def test_answer_has_exactly_five_keys():
    assert list(rules.answer(build({}), NAMES)) == ["claim_no", "vessel_name", "decision", "reason", "missing_documents"]


def test_answer_does_not_change_the_case():
    case = build({"docs": FULL + ["sof"], "doc_overrides": {"nor": SAME_SHIP}})
    before = json.dumps(case, ensure_ascii=False, sort_keys=True)
    rules.answer(case, NAMES)
    assert json.dumps(case, ensure_ascii=False, sort_keys=True) == before


# 제출 A~J: PDF 51쪽을 읽은 검토 기록(docs/review/01)의 판정·식별자·누락 목록을 손으로 옮긴 표
SUBMITTED = {
    "A": ("DMG-2026-0410", "MT HANBIT PIONEER", CLEAR, []),
    "B": ("DMG-2026-0417", "MT SEORAK SPIRIT", REQUEST, []),
    "C": ("DMG-2026-0424", "MT JIRISAN GLORY", RISK, []),
    "D": ("DMG-2026-0431", "MT BAEKDU VENTURE", CLEAR, []),
    "E": ("DMG-2026-0438", "MT HALLA CREST", REQUEST, ["Notice of Readiness"]),
    "F": ("DMG-2026-0445", "MT DOKDO TRADER", REVIEW, []),
    "G": ("DMG-2026-0452", "MT GEUMGANG STAR", REVIEW, []),
    "H": ("DMG-2026-0459", "MT NAKDONG BREEZE", REVIEW, []),
    "I": ("DMG-2026-0466", "MT TAEBAEK HORIZON", REVIEW, []),
    "J": ("DMG-2026-0473", "MT ULLEUNG PEARL", CLEAR, []),
}


def test_submitted_cases_keep_hand_checked_decisions():
    got = {case["case_id"]: rules.answer(case, NAMES) for case in rules.CASES}
    assert {key: (a["claim_no"], a["vessel_name"], a["decision"], a["missing_documents"]) for key, a in got.items()} == SUBMITTED


def test_submitted_answer_file_is_unchanged_by_the_rules():
    """규칙을 고쳐도 제출한 정답지 A~J의 다섯 키(reason 문장 포함)가 글자 그대로 같아야 한다."""
    path = ROOT / "submission" / "TimeBar_최종제출_answer.json"
    if not path.is_file():
        pytest.skip("제출 정답지가 없다")
    sheet = json.loads(path.read_text(encoding="utf-8"))
    frozen = {case["case_id"]: case["answer"] for case in sheet["cases"]}
    assert {case["case_id"]: rules.answer(case, NAMES) for case in rules.CASES} == frozen


def test_documents_render_from_the_same_views():
    """PDF를 만드는 쪽과 정답을 정하는 쪽이 같은 서류별 값을 본다."""
    case = build({"docs": FULL + ["sof"], "doc_overrides": {"nor": {"voyage": "HP-2599"}},
                  "copy_overrides": {"sof": {"hoses_disconnected": "2026-08-14 11:30"}}})
    views = rules.doc_views(case)
    assert [kind for kind, _ in views] == FULL + ["sof"]
    by_kind = [(kind, view["voyage"], view["hoses_disconnected"]) for kind, view in views]
    assert by_kind[2] == ("nor", "HP-2599", "2026-08-14 17:30")
    assert by_kind[3] == ("sof", "HP-2608", "2026-08-14 17:30")
    assert by_kind[5] == ("sof", "HP-2608", "2026-08-14 11:30")


def test_conflict_reason_never_prints_none():
    case = build({"docs": FULL + ["sof"], "copy_overrides": {"sof": {"vessel": None}}})
    result = rules.answer(case, NAMES)
    assert result["decision"] == REVIEW and "None" not in result["reason"] and "빈 값" in result["reason"]
