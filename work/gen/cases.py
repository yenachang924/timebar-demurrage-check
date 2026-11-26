"""케이스 데이터와 정답 규칙. 정답은 이 규칙으로만 정한다(워크플로 출력으로 정하지 않는다).

규칙이 보는 것은 묶음에 실제로 들어간 서류의 값뿐이다(doc_views). 묶음에 없는 서류의 날짜·선박명·서명·판독 상태는
케이스 데이터에 남아 있어도 판정과 reason에 쓰지 않는다. '서류가 없음'(누락)과 '서류는 있는데 필요한 값이 비어 있거나
정규화되지 않음'(검토 필요)을 구별한다. 수기 기대값 표: tests/test_domain_rules.py
"""
from __future__ import annotations

import re
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


# 서류 종류별로 판정이 보는 값. 워크플로 Extract 항목 가운데 판정 지시문이 쓰는 것만 적는다.
# (접수 기록에서는 선박·항차를 추출하지 않으므로 청구 번호로만 같은 청구인지 본다.)
IDENTITY = {"nor": ("vessel", "voyage"), "sof": ("vessel", "voyage"), "pumping_log": ("vessel", "voyage"),
            "lop": ("vessel", "voyage")}
JUDGED = {
    "invoice": ("claim_no", "vessel", "voyage", "invoice_completed"),
    "receipt": ("claim_no", "received_date", "time_bar_date"),
    "nor": ("vessel", "voyage"),
    "sof": ("vessel", "voyage", "hoses_disconnected", "smudge"),
    "pumping_log": ("vessel", "voyage", "pump_signed"),
    "lop": ("vessel", "voyage"),
}
BLANK_CHECKED = {"invoice": ("claim_no", "vessel", "voyage"), "receipt": ("claim_no",), **IDENTITY}
LABELS = {"claim_no": "청구 번호", "vessel": "선박명", "voyage": "항차 번호", "invoice_completed": "양하 완료 일시",
          "hoses_disconnected": "Hoses Disconnected 일시", "received_date": "접수일", "time_bar_date": "기한일",
          "smudge": "판독 상태", "pump_signed": "터미널 서명"}
DAY_SHAPE = re.compile(r"\d{4}-\d{2}-\d{2}")
TIME_SHAPE = re.compile(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}")


def _parses(value: object, shape: re.Pattern, fmt: str) -> bool:
    if not isinstance(value, str) or not shape.fullmatch(value):
        return False
    try:
        datetime.strptime(value, fmt)
    except ValueError:
        return False
    return True


def valid_day(value: object) -> bool:
    """YYYY-MM-DD로 정규화된, 달력에 있는 날짜인가. 빈 값·다른 표기는 False."""
    return _parses(value, DAY_SHAPE, DAY)


def valid_time(value: object) -> bool:
    """YYYY-MM-DD HH:MM으로 정규화된 일시인가."""
    return _parses(value, TIME_SHAPE, FMT)


def doc_views(case: dict) -> list[tuple[str, dict]]:
    """묶음에 들어가는 서류를 순서대로, 그 서류에 실제로 적히는 값과 함께 돌려준다.

    doc_overrides는 그 종류의 모든 장에, copy_overrides는 같은 종류의 두 번째 장부터 적용한다.
    PDF를 만드는 쪽(build.py, probes.py)과 정답 규칙이 같은 값을 보게 하려고 여기 한 곳에 둔다.
    """
    docs = list(case["docs"])
    overrides = case.get("doc_overrides", {})
    later = case.get("copy_overrides", {})
    return [
        (kind, {**case, **overrides.get(kind, {}), **(later.get(kind, {}) if kind in docs[:index] else {})})
        for index, kind in enumerate(docs)
    ]


def first_views(views: list[tuple[str, dict]]) -> dict[str, dict]:
    """종류별 첫 장. 여러 장의 값이 다르면 _conflict가 먼저 걸러 내므로 첫 장을 대표로 써도 된다."""
    return {kind: next(view for k, view in views if k == kind) for kind in dict.fromkeys(k for k, _ in views)}


def _conflict(views: list[tuple[str, dict]], names: dict[str, str]) -> str | None:
    """같은 종류 서류가 여러 장이고 판정에 쓰는 값이 서로 다르면 사유를 돌려준다. 어느 장도 고르지 않는다."""
    for kind in dict.fromkeys(k for k, _ in views):
        copies = [view for k, view in views if k == kind]
        fields = [f for f in JUDGED.get(kind, ()) if len({view.get(f) for view in copies}) > 1]
        if fields:
            detail = "; ".join(f"{LABELS[f]} " + " / ".join(str(view.get(f) if view.get(f) is not None else "") or "빈 값" for view in copies) for f in fields)
            return (f"{names[kind]}가 {len(copies)}건 제출되었고 값이 서로 다름({detail}). "
                    "어느 쪽이 맞는지 정할 근거가 없어 담당자 확인이 필요함")
    return None


def _blank_identity(first: dict[str, dict], names: dict[str, str]) -> str | None:
    for kind, view in first.items():
        empty = [LABELS[f] for f in BLANK_CHECKED.get(kind, ()) if not str(view.get(f) or "").strip()]
        if empty:
            return f"{names[kind]}의 {'·'.join(empty)}가 비어 있어 같은 청구 건인지 확인할 수 없음"
    return None


def _other_claim(first: dict[str, dict], names: dict[str, str]) -> str | None:
    """청구서와 다른 청구 건의 서류. 청구서가 없으면 기준이 없으므로 비교하지 않는다."""
    invoice = first.get("invoice")
    if invoice is None:
        return None
    for kind, view in first.items():
        if kind in IDENTITY and (view["vessel"], view["voyage"]) != (invoice["vessel"], invoice["voyage"]):
            return (f"{names[kind]}의 선박명·항차({view['vessel']} / {view['voyage']})가 "
                    f"청구서({invoice['vessel']} / {invoice['voyage']})와 다름")
    receipt = first.get("receipt")
    if receipt is not None and receipt["claim_no"] != invoice["claim_no"]:
        return f"{names['receipt']}의 청구 번호({receipt['claim_no']})가 청구서({invoice['claim_no']})와 다름"
    return None


def _unusable_dates(first: dict[str, dict], names: dict[str, str]) -> str | None:
    checks = [("receipt", "received_date", valid_day), ("receipt", "time_bar_date", valid_day),
              ("invoice", "invoice_completed", valid_time), ("sof", "hoses_disconnected", valid_time)]
    bad = [(kind, field) for kind, field, ok in checks if kind in first and not ok(first[kind].get(field))]
    if not bad:
        return None
    parts = [f"{names[kind]}의 {LABELS[field]}({first[kind].get(field) or '빈 값'})" for kind, field in bad]
    return ", ".join(parts) + ": 비어 있거나 정해진 형식의 날짜가 아니어서 비교할 수 없음"


def review_reason(case: dict, names: dict[str, str]) -> str | None:
    """사람이 봐야 하는 사유. 없으면 None. 묶음에 있는 서류의 값만 본다."""
    views = doc_views(case)
    first = first_views(views)
    early = _conflict(views, names) or _blank_identity(first, names) or _other_claim(first, names)
    if early:
        return early
    if "sof" in first and first["sof"]["smudge"]:
        return "Statement of Facts 스캔본에서 Hoses Disconnected 일시를 판독할 수 없어 양하 완료 일시를 확인할 수 없음"
    unusable = _unusable_dates(first, names)
    if unusable:
        return unusable
    if "invoice" in first and "sof" in first and first["invoice"]["invoice_completed"] != first["sof"]["hoses_disconnected"]:
        return (f"청구서의 양하 완료 일시 {first['invoice']['invoice_completed']}와 Statement of Facts의 "
                f"Hoses Disconnected {first['sof']['hoses_disconnected']}가 다름")
    if "pumping_log" in first and not first["pumping_log"]["pump_signed"] and "lop" in first:
        return ("Cargo Pumping Log에 터미널 서명이 없고 Letter of Protest가 첨부됨. 항의서가 서명을 대신하는지는 "
                "용선계약(BPVOY4)에 명시되어 있지 않아 담당자 판단이 필요함")
    return None


def answer(case: dict, names: dict[str, str]) -> dict:
    """판정 순서: 검토 필요 → 기한 위험 → 보완 요청 → 지급 검토 가능. 누락 목록은 어느 판정에서도 전부 적는다."""
    first = first_views(doc_views(case))
    missing = [names[d] for d in REQUIRED if d not in first]
    invoice, receipt, sof, pumping = (first.get(k) for k in ("invoice", "receipt", "sof", "pumping_log"))
    unsigned = pumping is not None and not pumping["pump_signed"] and "lop" not in first
    review = review_reason(case, names)
    # review가 없으면 접수 기록의 두 날짜는 유효하다(_unusable_dates). 접수 기록이 없으면 기한을 판단하지 않는다.
    late = review is None and receipt is not None and receipt["received_date"] > receipt["time_bar_date"]
    window = f"접수일 {receipt['received_date']}, 기한일 {receipt['time_bar_date']}" if receipt is not None else ""
    if review:
        decision, reason = "검토 필요", review
    elif late:
        decision, reason = "기한 위험", f"접수일이 기한일(양하 완료 후 90일)보다 늦음. {window}"
    elif missing or unsigned:
        parts = (["필수 서류 누락: " + ", ".join(missing)] if missing else []) + (
            ["Cargo Pumping Log에 터미널 서명이 없고 Letter of Protest도 없음"] if unsigned else [])
        timing = f"기한 내 접수({window})" if receipt is not None else "Claim Receipt Record가 없어 접수일과 기한일은 확인하지 못함"
        decision, reason = "보완 요청", "; ".join(parts) + f". {timing}"
    else:
        decision = "지급 검토 가능"
        reason = (f"필수 서류 5종 완비, 터미널 서명 확인. 기한 내 접수({window}), "
                  f"양하 완료 일시 {sof['hoses_disconnected']} 일치")
    # 청구서가 없으면 식별자를 다른 서류나 케이스 데이터에서 가져오지 않고 빈 문자열로 둔다(제안 규약, 담당자 확인 전).
    return {"claim_no": invoice["claim_no"] if invoice else "", "vessel_name": invoice["vessel"] if invoice else "",
            "decision": decision, "reason": reason, "missing_documents": missing}


CASES = [finish(plan, index) for index, plan in enumerate(PLAN)]
