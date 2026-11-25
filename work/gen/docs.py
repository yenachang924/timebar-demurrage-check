"""체선료 청구 서류의 HTML. 모든 회사·선박·인물은 가상이다.

양식 구성의 근거(docs/reference/forms/의 이미지):
- Statement of Facts: BIMCO/FONASBA Standard Statement of Facts (Oil and Chemical Tank Vessels) Short Form의 칸 번호와 이름
- Cargo Pumping Log: Saudi Aramco Form 39 General & Cargo Log의 열(Date, Time, Shore, Ship, Diff, Hourly Rate, Remarks)
  + BPVOY4 19.7.1조가 요구하는 시간별 매니폴드 압력과 두 서명
- Letter of Protest: Saudi Aramco Form 32 Protest Letter의 구성(Port/Terminal, Berth, Date, 수신, 본문, 서명, 수령 확인)
로고와 발행 기관 명칭은 쓰지 않는다.
"""
from __future__ import annotations

from datetime import datetime, timedelta

FMT = "%Y-%m-%d %H:%M"
ALT_FMT = "%d %b %Y / %H%M hrs"
CSS = """
@page { size: A4; margin: 14mm; }
body { font-family: Arial, 'Malgun Gothic', sans-serif; font-size: 9.5pt; color: #111; }
h1 { font-size: 13.5pt; margin: 0 0 2px; letter-spacing: .4px; }
.sub { color: #333; font-size: 8.5pt; }
.head { border-bottom: 2px solid #111; padding-bottom: 5px; margin-bottom: 8px; display: flex; justify-content: space-between; }
table { border-collapse: collapse; width: 100%; margin: 6px 0; }
th, td { border: 1px solid #444; padding: 3px 6px; text-align: left; vertical-align: top; }
th { background: #eee; font-weight: 600; }
table.kv th { width: 38%; }
table.grid th, table.grid td { text-align: center; }
table.log th, table.log td { text-align: center; font-size: 6.9pt; padding: 0.4px 4px; line-height: 1.12; }
table.top th { width: 13%; } table.top td { width: 37%; }
table.boxes td { height: 34px; width: 25%; font-size: 9.5pt; }
.no { font-size: 7pt; color: #333; display: block; margin-bottom: 2px; }
.sign { display: flex; gap: 22px; margin-top: 16px; }
.sign div { flex: 1; }
.line { border-bottom: 1px solid #111; height: 30px; font-family: 'Segoe Script', 'Brush Script MT', cursive; font-size: 14pt; padding-left: 8px; }
.cap { font-size: 8pt; color: #333; margin-top: 2px; }
.note { font-size: 9pt; margin-top: 8px; line-height: 1.45; }
.fict { position: fixed; bottom: 2mm; left: 0; right: 0; text-align: center; font-size: 7pt; color: #777; }
"""
FICT = "FICTIONAL SAMPLE DOCUMENT - created for a hackathon test dataset. All companies, vessels and persons are fictitious."
SMUDGE = ("<span style='display:inline-block;width:140px;height:14px;background:#111;border-radius:7px;"
          "transform:rotate(-2deg)'></span>")
AGENT = "Hanbada Shipping Agency Co. (fictional)"


def page(title: str, ref: str, issuer: str, body: str, note: str = "") -> str:
    return (
        f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>"
        f"<div class='head'><div><h1>{title}</h1><div class='sub'>{issuer}</div></div>"
        f"<div class='sub'>Ref: {ref}</div></div>{body}<div class='fict'>{note}{FICT}</div></body></html>"
    )


def rows(pairs: list[tuple[str, str]]) -> str:
    return "<table class='kv'>" + "".join(f"<tr><th>{k}</th><td>{v}</td></tr>" for k, v in pairs) + "</table>"


def sign(blocks: list[tuple[str, str, bool]]) -> str:
    cells = "".join(
        f"<div><div class='line'>{name if signed else ''}</div><div class='cap'>{role}</div></div>"
        for role, name, signed in blocks
    )
    return f"<div class='sign'>{cells}</div>"


def at(c: dict, key: str, shift_minutes: int = 0) -> datetime:
    return datetime.strptime(c[key], FMT) + timedelta(minutes=shift_minutes)


def show(c: dict, key: str, shift_minutes: int = 0) -> str:
    """일시 표기. alt 양식은 '14 Aug 2026 / 1840 hrs'처럼 쓴다."""
    return at(c, key, shift_minutes).strftime(ALT_FMT if c["style"] == "alt" else FMT)


def voyage(c: dict) -> list[tuple[str, str]]:
    return [("Vessel", c["vessel"]), ("Voyage No.", c["voyage"]),
            ("Charter Party", f"BPVOY4 dated {c['cp_date']}"), ("Discharge Port / Terminal", c["terminal"])]


def invoice(c: dict) -> str:
    used = c["demurrage_hours"] + c["laytime_hours"]
    body = rows(voyage(c) + [
        ("Claim No.", c["claim_no"]), ("Invoice Date", c["invoice_date"]),
        ("Owners", c["owner"]), ("Charterers", c["charterer"]), ("Cargo", c["cargo"]),
    ])
    body += ("<table class='grid'><tr><th colspan='2'>LAYTIME STATEMENT - DISCHARGE PORT</th></tr>" + "".join(
        f"<tr><td style='text-align:left'>{k}</td><td>{v}</td></tr>" for k, v in [
            ("Notice of Readiness Tendered", c["nor_tendered"]),
            ("Laytime Commenced (6 hours after NOR)", show({**c, "style": "standard"}, "nor_tendered", 360)),
            ("Completion of Discharge (hoses disconnected)", c["invoice_completed"]),
            ("Total Time Used", f"{used:.2f} hours"),
            ("Laytime Allowed", f"{c['laytime_hours']}.00 running hours"),
            ("Time on Demurrage", f"{c['demurrage_hours']:.2f} hours"),
            ("Demurrage Rate", f"USD {c['rate']:,}.00 per day pro rata"),
            ("Amount Claimed", f"USD {c['amount']:,.2f}"),
        ]) + "</table>")
    enclosed = "Notice of Readiness, Statement of Facts, Cargo Pumping Log" + (
        ", Letter of Protest" if "lop" in c["docs"] else "")
    body += f"<div class='note'>Supporting documents enclosed: {enclosed}.</div>"
    body += sign([("For and on behalf of Owners", c["owner_sign"], True)])
    return page("DEMURRAGE CLAIM INVOICE", c["claim_no"], c["owner"], body)


def receipt(c: dict) -> str:
    body = rows([
        ("Claim No.", c["claim_no"]), ("Vessel / Voyage", f"{c['vessel']} / {c['voyage']}"),
        ("Counterparty (Owners)", c["owner"]),
        ("Completion of Discharge (hoses disconnected)", c["hoses_disconnected"]),
        ("Claim Time Limit", "90 days after completion of discharge (BPVOY4 cl. 20.1)"),
        ("Time Bar Date", c["time_bar_date"]),
        ("Date Claim Received", c["received_date"]), ("Received via", "E-mail to demurrage desk, with attachments"),
        ("Logged by", "Claims Desk, " + c["charterer"]),
    ])
    body += "<div class='note'>System printout from the Charterers' demurrage claims register. Generated when a claim package is logged.</div>"
    return page("CLAIM RECEIPT RECORD", "REG-" + c["claim_no"], c["charterer"] + " - Demurrage Claims Desk", body)


def nor(c: dict) -> str:
    body = rows(voyage(c) + [
        ("To", c["terminal"] + " / " + c["charterer"] + " / " + AGENT), ("Cargo", c["cargo"]),
        ("Arrived at Pilot Station", show(c, "arrival")),
        ("Notice of Readiness Tendered", show(c, "nor_tendered")),
    ])
    body += ("<div class='note'>Please be advised that the above vessel arrived at the customary anchorage of the "
             "discharge port at the time stated above and is in all respects ready to discharge her cargo in "
             "accordance with the terms and conditions of the governing Charter Party. This Notice of Readiness is "
             "tendered without prejudice to the vessel's rights under the Charter Party.</div>")
    body += sign([("Master (name, signature, ship's stamp)", c["master"], True),
                  (f"Received / accepted on behalf of Receivers - {show(c, 'nor_tendered', 25)}",
                   c["terminal_rep"], c["nor_received"])])
    return page("NOTICE OF READINESS", c["voyage"] + "-NOR", c["owner"], body)


def box(number: int, label: str, value: str = "", span: int = 1) -> str:
    return f"<td colspan='{span}'><span class='no'>{number}. {label}</span>{value}</td>"


def daily_working(c: dict) -> str:
    start, end = at(c, "commenced"), at(c, "completed")
    lines, day = [], start
    while day.date() <= end.date():
        begin = start if day.date() == start.date() else day.replace(hour=0, minute=0)
        finish = end if day.date() == end.date() else day.replace(hour=23, minute=59)
        lines.append(f"<tr><td>{day.strftime('%Y-%m-%d')}</td><td>{day.strftime('%a')}</td>"
                     f"<td>{begin.strftime('%H:%M')}</td><td>{finish.strftime('%H:%M')}</td><td>-</td><td>-</td>"
                     f"<td>Disch.</td><td style='text-align:left'>Discharging through 3 x 16 in. arms</td></tr>")
        day = (day + timedelta(days=1)).replace(hour=0, minute=0)
    head = ("<tr><th rowspan='2'>Date</th><th rowspan='2'>Day</th><th colspan='2'>Hours worked</th>"
            "<th colspan='2'>Hours stopped</th><th rowspan='2'>Quantity load./disch.</th><th rowspan='2'>Remarks</th></tr>"
            "<tr><th>From</th><th>to</th><th>From</th><th>to</th></tr>")
    return f"<div class='sub' style='margin-top:6px'>DETAILS OF DAILY WORKING</div><table class='grid'>{head}{''.join(lines)}</table>"


def sof_standard(c: dict) -> str:
    last = SMUDGE if c["smudge"] else c["hoses_disconnected"]
    grid = "<table class='boxes'>" + "".join(f"<tr>{line}</tr>" for line in [
        box(1, "Agents", AGENT, 2) + box(3, "Port or Place", c["terminal"], 2),
        box(2, "Vessel's name", c["vessel"] + " / Voy. " + c["voyage"], 2) + box(5, "Vessel moored", c["berthed"], 2),
        box(4, "Owners/Disponent Owners", c["owner"], 2) + box(11, "Hoses connected (disch.)", c["hoses_connected"])
        + box(12, "Discharging commenced", c["commenced"]),
        box(8, "Cargo (also indicate possible details as to slops)", c["cargo"], 2)
        + box(14, "Discharging completed", c["completed"]) + box(15, "Hoses disconnected (disch.)", last),
        box(13, "Charter Party", f"BPVOY4 dated {c['cp_date']}", 2)
        + box(18, "Cargo documents on board", show(c, "hoses_disconnected", 95))
        + box(19, "Vessel sailed", show(c, "hoses_disconnected", 190)),
        box(20, "Vessel arrived at anchorage", c["arrival"]) + box(21, "Pilot on board", show(c, "berthed", -140))
        + box(24, "Notice of readiness tendered", c["nor_tendered"], 2),
        box(30, "Free Pratique given", show(c, "arrival", 75), 2) + box(16, "Bill of Lading quantity", "270,000 MT")
        + box(17, "Outturn quantity", "269,640 MT"),
    ]) + "</table>"
    remarks = ("<table><tr><td style='height:44px'><span class='no'>General remarks (state reasons and duration of "
               "delays, such as slow pumping, excess back pressure, etc.)</span>Vessel waited at anchorage for berth. "
               "Shore restriction on discharge rate recorded in the pumping log.</td></tr></table>")
    signs = sign([("Name and signature (Master)", c["master"], True), ("Name and signature (Agents)", "Lee D. H.", True),
                  ("Name and signature (for the Charterers/Shippers/Receivers)", c["terminal_rep"], True)])
    place = f"<div class='sub'>Place and date: Ulsan, {c['hoses_disconnected'][:10]}</div>"
    note = "Box numbering follows the BIMCO/FONASBA standard short form for oil and chemical tank vessels. "
    return page("STATEMENT OF FACTS (OIL AND CHEMICAL TANK VESSELS)", c["voyage"] + "-SOF", AGENT,
                grid + daily_working(c) + remarks + place + signs, note)


def sof_alt(c: dict) -> str:
    last = SMUDGE if c["smudge"] else show(c, "hoses_disconnected")
    events = [("Arrived at Pilot Station", show(c, "arrival")), ("Notice of Readiness Tendered", show(c, "nor_tendered")),
              ("All Fast at Berth", show(c, "berthed")), ("Hoses Connected", show(c, "hoses_connected")),
              ("Commenced Discharge", show(c, "commenced")), ("Completed Discharge", show(c, "completed")),
              ("Hoses Disconnected", last)]
    head = "<tr><th>No.</th><th>Operation</th><th>Date / Time (local)</th><th>Remarks</th></tr>"
    lines = "".join(f"<tr><td>{i}</td><td style='text-align:left'>{k}</td><td>{v}</td><td></td></tr>"
                    for i, (k, v) in enumerate(events, 1))
    body = rows(voyage(c)) + f"<table class='grid'>{head}{lines}</table>" + sign(
        [("Master", c["master"], True), ("Terminal Representative", c["terminal_rep"], True)])
    return page("PORT LOG - STATEMENT OF FACTS", c["voyage"] + "-SOF", c["terminal"], body)


def sof(c: dict) -> str:
    return sof_alt(c) if c["style"] == "alt" else sof_standard(c)


def pumping_log(c: dict) -> str:
    """시간별 기록. 열 구성은 터미널 General & Cargo Log(Shore/Ship/Diff/Hourly Rate)에 매니폴드 압력을 더한 것."""
    start, end = at(c, "commenced"), at(c, "completed")
    hours = int((end - start).total_seconds() // 3600)
    total = 313000
    lines, ship = [], 0
    for hour in range(1, hours + 1):
        restricted = hours // 2 <= hour < hours // 2 + 3
        stripping = hour > hours - 2
        rate = 4300 if restricted else (round(total / hours * 0.55) if stripping else round((total - 3 * 4300) / (hours - 5) / 10) * 10)
        ship = min(ship + rate, total)
        pressure = 6.4 if restricted else (5.1 if stripping else round(7.0 + (hour % 3) * 0.1, 1))
        remark = "Shore restriction, max rate" if restricted else ("Stripping" if stripping else "")
        stamp = (start + timedelta(hours=hour)).strftime(ALT_FMT if c["style"] == "alt" else FMT)
        lines.append(f"<tr><td>{stamp}</td><td>{pressure}</td><td>{ship - (hour * 7) % 90:,}</td><td>{ship:,}</td>"
                     f"<td>{(hour * 7) % 90}</td><td>{rate:,}</td><td style='text-align:left'>{remark}</td></tr>")
    head = ("<tr><th rowspan='2'>Date / Time</th><th rowspan='2'>Manifold Pressure (kg/cm2)</th>"
            "<th colspan='2'>Total Discharged (m3)</th><th rowspan='2'>Diff</th><th rowspan='2'>Hourly Rate (m3/h)</th>"
            "<th rowspan='2'>Remarks</th></tr><tr><th>Shore</th><th>Ship</th></tr>")
    top = (f"<table class='top'><tr><th>MV</th><td>{c['vessel']} / Voy. {c['voyage']}</td><th>Port / Terminal</th>"
           f"<td>{c['terminal']}</td></tr><tr><th>Cargo</th><td>{c['cargo']}</td><th>Pumps in use</th><td>3 x COP</td></tr></table>")
    body = top + f"<table class='log'>{head}{''.join(lines)}</table>"
    body += sign([("Chief Officer (senior officer of the Vessel)", c["chief_officer"], True),
                  ("Terminal Representative (countersignature)", c["terminal_rep"], c["pump_signed"])])
    return page("CARGO PUMPING LOG", c["voyage"] + "-PL", c["owner"], body)


def lop(c: dict) -> str:
    """수신·본문·서명·수령 확인의 구성은 터미널 Protest Letter 양식을 본선 발행용으로 뒤집은 것."""
    top = (f"<table class='kv'><tr><th>Port / Terminal</th><td>{c['terminal']}</td></tr><tr><th>Berth</th><td>No. 2</td></tr>"
           f"<tr><th>Date / Time Issued</th><td>{show(c, 'lop_issued')}</td></tr>"
           f"<tr><th>From</th><td>Master, {c['vessel']} (Voy. {c['voyage']})</td></tr>"
           f"<tr><th>To</th><td>Terminal Representative, {c['terminal']}</td></tr>"
           f"<tr><th>Subject</th><td>{c['lop_subject']}</td></tr></table>")
    body = top + (f"<div class='note'>During the vessel's call at this terminal the matter noted below occurred and is "
                  f"brought to your attention.<br><br>{c['lop_text']}<br><br>On behalf of Owners I hereby lodge this "
                  f"protest and hold you and/or whom it may concern responsible for all consequences, loss of time and "
                  f"costs arising. Copies of this letter will be forwarded to Charterers and Owners.</div>")
    body += sign([("Signature (Master)", c["master"], True)])
    body += "<div class='note'>I hereby acknowledge receipt of a copy of this notice on the date shown above (for receipt only).</div>"
    body += sign([("Signature (Terminal Representative)", c["terminal_rep"], True)])
    return page("LETTER OF PROTEST", c["voyage"] + "-LOP", c["owner"], body)


def other(c: dict) -> str:
    body = rows([("Vessel", c["vessel"]), ("Port", c["terminal"]), ("Item", "Fresh water supply 120 MT"),
                 ("Unit Price", "USD 12.00 per MT"), ("Amount", "USD 1,440.00")])
    return page("PORT SUPPLY RECEIPT", c["voyage"] + "-FW", "Harbour Supply Co. (fictional)", body)


RENDERERS = {"invoice": invoice, "receipt": receipt, "nor": nor, "sof": sof,
             "pumping_log": pumping_log, "lop": lop, "other": other}
NAMES = {"invoice": "Demurrage Claim Invoice", "receipt": "Claim Receipt Record", "nor": "Notice of Readiness",
         "sof": "Statement of Facts", "pumping_log": "Cargo Pumping Log", "lop": "Letter of Protest",
         "other": "Port Supply Receipt"}
