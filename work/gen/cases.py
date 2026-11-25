"""케이스 데이터와 정답 규칙. 정답은 이 규칙으로만 정한다(워크플로 출력으로 정하지 않는다)."""
from __future__ import annotations

from datetime import datetime, timedelta

FMT = "%Y-%m-%d %H:%M"
DAY = "%Y-%m-%d"
REQUIRED = ["invoice", "receipt", "nor", "sof", "pumping_log"]
FULL = ["invoice", "receipt", "nor", "sof", "pumping_log"]
TIME_LIMIT_DAYS = 90
NOTICE_HOURS = 6
DECISIONS = ["지급 검토 가능", "보완 요청", "기한 위험", "검토 필요"]

BASE = {
    "cp_date": "2026-07-03", "owner": "Blue Meridian Tankers Ltd. (fictional)",
    "charterer": "Daehan Energy Trading Co. (fictional)",
    "terminal": "Onsan Crude Terminal No. 2, Ulsan (fictional)", "cargo": "Arab Light Crude Oil, 270,000 MT",
    "master": "Capt. R. Alvarez", "chief_officer": "J. Petrov", "terminal_rep": "Kim S. H.", "owner_sign": "M. Hartono",
    "laytime_hours": 72, "rate": 48000, "nor_received": True, "pump_signed": True, "style": "standard",
    "pumping": [(7.2, 5800, ""), (7.1, 5900, ""), (7.0, 5850, ""), (6.4, 4300, "Shore restriction"),
                (7.1, 5900, ""), (7.0, 5700, "Stripping")],
    "docs": FULL, "doc_overrides": {}, "degrade": [], "scan": "heavy", "smudge": False,
    "lop_subject": "Terminal declined to countersign the pumping log",
    "lop_text": "We hereby protest that the terminal representative declined to countersign the vessel's cargo "
                "pumping log on completion of discharge. Owners reserve all rights under the Charter Party.",
}

# (case_id, 선박, 항차, 도착 일시, 접안까지 대기 시간, 양하 시간, 양하 완료 후 접수까지 일수, 케이스별 차이)
PLAN = [
    ("A", "MT HANBIT PIONEER", "HP-2608", "2026-08-10 04:30", 52, 53, 49, {}),
    ("B", "MT SEORAK SPIRIT", "SS-2611", "2026-08-20 22:10", 61, 49, 48, {"pump_signed": False}),
    ("C", "MT JIRISAN GLORY", "JG-2609", "2026-07-26 09:40", 47, 55, 91, {"degrade": ["nor", "sof"], "scan": "mild"}),
    ("D", "MT BAEKDU VENTURE", "BV-2607", "2026-07-29 13:20", 66, 51, 90, {"degrade": ["nor", "pumping_log"], "scan": "mild"}),
    ("E", "MT HALLA CREST", "HC-2610", "2026-08-15 02:50", 58, 50, 40,
     {"docs": ["invoice", "receipt", "sof", "pumping_log"], "style": "alt", "terminal": "Yeosu Oil Jetty No. 4, Yeosu (fictional)", "terminal_rep": "Park J. W."}),
    ("F", "MT DOKDO TRADER", "DT-2612", "2026-08-27 17:00", 70, 54, 35,
     {"pump_signed": False, "docs": FULL + ["lop"]}),
    ("G", "MT GEUMGANG STAR", "GS-2613", "2026-09-02 06:15", 49, 52, 30, {"invoice_shift_hours": 6, "style": "alt", "terminal": "Yeosu Oil Jetty No. 4, Yeosu (fictional)", "terminal_rep": "Park J. W."}),
    ("H", "MT NAKDONG BREEZE", "NB-2614", "2026-09-05 11:45", 55, 48, 33,
     {"doc_overrides": {"pumping_log": {"vessel": "MT SEORAK SPIRIT", "voyage": "SS-2611"}}}),
    ("I", "MT TAEBAEK HORIZON", "TH-2615", "2026-09-09 20:30", 63, 56, 28,
     {"smudge": True, "degrade": ["sof", "pumping_log"]}),
    ("J", "MT ULLEUNG PEARL", "UP-2616", "2026-09-14 03:05", 44, 50, 26,
     {"style": "alt", "terminal": "Yeosu Oil Jetty No. 4, Yeosu (fictional)", "terminal_rep": "Park J. W.",
      "docs": ["invoice", "receipt", "nor", "sof", "pumping_log", "other"]}),
]


def timeline(arrival: str, wait_hours: int, discharge_hours: int) -> dict:
    start = datetime.strptime(arrival, FMT)
    berthed = start + timedelta(hours=wait_hours)
    commenced = berthed + timedelta(hours=2, minutes=50)
    completed = commenced + timedelta(hours=discharge_hours)
    marks = {"arrival": start, "nor_tendered": start + timedelta(minutes=30), "berthed": berthed,
             "hoses_connected": berthed + timedelta(hours=2, minutes=10), "commenced": commenced,
             "completed": completed, "hoses_disconnected": completed + timedelta(hours=1, minutes=10)}
    return {key: value.strftime(FMT) for key, value in marks.items()}


def finish(plan: tuple, number: int) -> dict:
    """계획 한 줄을 서류에 들어갈 값이 모두 채워진 케이스 dict로 만든다."""
    case_id, vessel, voyage, arrival, wait, discharge, received_after, extra = plan
    times = timeline(arrival, wait, discharge)
    done = datetime.strptime(times["hoses_disconnected"], FMT)
    used = (done - datetime.strptime(times["nor_tendered"], FMT)).total_seconds() / 3600 - NOTICE_HOURS
    hours = round(max(used - BASE["laytime_hours"], 0), 2)
    received = done + timedelta(days=received_after)
    claimed = done + timedelta(hours=extra.get("invoice_shift_hours", 0))
    return {
        **BASE, **times, **extra, "case_id": case_id, "vessel": vessel, "voyage": voyage,
        "claim_no": f"DMG-2026-{410 + number * 7:04d}",
        "time_bar_date": (done + timedelta(days=TIME_LIMIT_DAYS)).strftime(DAY),
        "received_date": received.strftime(DAY), "invoice_date": (received - timedelta(days=4)).strftime(DAY),
        "invoice_completed": claimed.strftime(FMT), "lop_issued": (done + timedelta(minutes=50)).strftime(FMT),
        "demurrage_hours": hours, "amount": round(hours * BASE["rate"] / 24, 2),
    }


def review_reason(case: dict, names: dict[str, str]) -> str | None:
    """사람이 봐야 하는 사유. 없으면 None."""
    for kind, changed in case["doc_overrides"].items():
        if kind in case["docs"] and (changed.get("vessel") or changed.get("voyage")):
            return (f"{names[kind]}의 선박명·항차({changed.get('vessel', case['vessel'])} / "
                    f"{changed.get('voyage', case['voyage'])})가 청구서({case['vessel']} / {case['voyage']})와 다름")
    if case["smudge"]:
        return "Statement of Facts 스캔본에서 Hoses Disconnected 일시를 판독할 수 없어 양하 완료 일시를 확인할 수 없음"
    if "sof" in case["docs"] and case["invoice_completed"] != case["hoses_disconnected"]:
        return (f"청구서의 양하 완료 일시 {case['invoice_completed']}와 Statement of Facts의 "
                f"Hoses Disconnected {case['hoses_disconnected']}가 다름")
    if "pumping_log" in case["docs"] and not case["pump_signed"] and "lop" in case["docs"]:
        return ("Cargo Pumping Log에 터미널 서명이 없고 Letter of Protest가 첨부됨. 항의서가 서명을 대신하는지는 "
                "용선계약(BPVOY4)에 명시되어 있지 않아 담당자 판단이 필요함")
    return None


def answer(case: dict, names: dict[str, str]) -> dict:
    """판정 순서: 검토 필요 → 기한 위험 → 보완 요청 → 지급 검토 가능."""
    docs = case["docs"]
    missing = [names[d] for d in REQUIRED if d not in docs]
    unsigned = "pumping_log" in docs and not case["pump_signed"] and "lop" not in docs
    review = review_reason(case, names)
    late = "receipt" in docs and case["received_date"] > case["time_bar_date"]
    window = f"접수일 {case['received_date']}, 기한일 {case['time_bar_date']}"
    if review:
        decision, reason = "검토 필요", review
    elif late:
        decision, reason = "기한 위험", f"접수일이 기한일(양하 완료 후 90일)보다 늦음. {window}"
    elif missing or unsigned:
        parts = (["필수 서류 누락: " + ", ".join(missing)] if missing else []) + (
            ["Cargo Pumping Log에 터미널 서명이 없고 Letter of Protest도 없음"] if unsigned else [])
        decision, reason = "보완 요청", "; ".join(parts) + f". 기한 내 접수({window})"
    else:
        decision = "지급 검토 가능"
        reason = (f"필수 서류 5종 완비, 터미널 서명 확인. 기한 내 접수({window}), "
                  f"양하 완료 일시 {case['hoses_disconnected']} 일치")
    return {"claim_no": case["claim_no"], "vessel_name": case["vessel"], "decision": decision,
            "reason": reason, "missing_documents": missing}


CASES = [finish(plan, index) for index, plan in enumerate(PLAN)]
