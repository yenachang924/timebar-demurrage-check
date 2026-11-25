"""예시팀 워크플로 설정(JSON)의 구조를 그대로 빌려 체선료 검증 워크플로 초안을 만든다.

    uv run python work/gen/workflow.py

결과는 work/workflow_draft.json. Studio에서 '설정 가져오기'로 넣어 실행해 보고,
제출용 파일은 반드시 Studio에서 다시 내보낸다.
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = next((ROOT / "docs" / "reference" / "example").glob("*/*workflow.json"))
AGENT = "유조선 체선료 청구 서류 검증 에이전트"
MERGE = "병합-1"
JUDGE = "청구_판정"
NONE = "문서에 없으면 추측하지 말고 빈 문자열."
TIME = "YYYY-MM-DD HH:MM(24시간)으로 정규화. 예: 14 Aug 2026 18:40 → 2026-08-14 18:40. " + NONE
DATE = "YYYY-MM-DD로 정규화. " + NONE
BOUNDARY = ("[문서 경계] 입력 파일은 청구 1건의 서류 여러 종류가 한 PDF로 이어 붙은 묶음이며 앞 단계에서 문서 단위로 "
            "분리된다. 다른 문서에 속한 값을 이 문서의 값으로 가져오지 않는다. ")
SIGNED = "서명란 선 위에 손글씨 서명이나 이름이 있으면 true, 선만 있고 비어 있으면 false."
READ = ("문서 판독 상태. 번호가 붙은 칸의 날짜·시각을 모두 읽을 수 있으면 'clear'. 칸이 가려졌거나 번져서 읽을 수 없는 "
        "날짜·시각이 하나라도 있으면 'unclear'. 글자가 작거나 표가 길다는 이유만으로 'unclear'라 하지 않는다.")
VESSEL = {"type": "string", "description": "선박명. 'Vessel' 칸의 값 그대로. 예: 'MT HANBIT PIONEER'. " + NONE}
VOYAGE = {"type": "string", "description": "항차 번호. 'Voyage No.' 칸의 값. 예: 'HP-2608'. " + NONE}

CLASSES = [
    ("invoice", "청구서_추출", "Demurrage Claim Invoice(체선료 청구서). 제목에 'DEMURRAGE CLAIM INVOICE'가 있고 Claim No., "
     "Invoice Date 칸과 'LAYTIME STATEMENT' 표(Laytime Allowed, Time on Demurrage, Demurrage Rate, Amount Claimed)가 있다. 선주가 발행한다."),
    ("receipt", "접수기록_추출", "Claim Receipt Record(청구 접수 기록). 제목에 'CLAIM RECEIPT RECORD'가 있고 Time Bar Date와 "
     "Date Claim Received 칸이 있다. 화주 측 청구 대장에서 출력한다."),
    ("nor", "도착통지서_추출", "Notice of Readiness(도착 통지서). 제목에 'NOTICE OF READINESS'가 있고 Arrived at Pilot Station, "
     "Notice of Readiness Tendered 칸과 선장 서명란이 있다."),
    ("sof", "시간기록_추출", "Statement of Facts(항만 시간 기록). 제목에 'STATEMENT OF FACTS'가 있다. 번호가 붙은 칸(1. Agents, 5. Vessel moored, "
     "15. Hoses disconnected (disch.), 24. Notice of readiness tendered)과 'DETAILS OF DAILY WORKING' 표가 있는 양식, "
     "또는 'PORT LOG - STATEMENT OF FACTS' 제목 아래 Operation별 Date / Time 표가 있는 양식이다."),
    ("pumping_log", "펌핑기록_추출", "Cargo Pumping Log(펌핑 기록). 제목에 'CARGO PUMPING LOG'가 있고 한 시간 간격의 Manifold Pressure, Total Discharged"
     "(Shore / Ship), Hourly Rate 표와 Chief Officer, Terminal Representative 서명란이 있다."),
    ("lop", "항의서_추출", "Letter of Protest(항의서). 제목에 'LETTER OF PROTEST'가 있고 Port / Terminal, From, To, Subject 칸과 항의 본문, "
     "선장 서명, 터미널 대표의 수령 확인 서명이 있다."),
]
OTHER = "위 여섯 범주에 해당하지 않거나 판독이 어려운 문서. 예: 급수 영수증, 선하증권, 빈 페이지, 다른 청구서."

FIELDS = {
    "청구서_추출": {
        "claim_no": {"type": "string", "description": "청구 번호. 'Claim No.' 칸의 값. 예: 'DMG-2026-0412'. " + NONE},
        "vessel_name": VESSEL, "voyage_no": VOYAGE,
        "invoice_date": {"type": "string", "description": "'Invoice Date' 칸의 날짜. " + DATE},
        "completion_of_discharge": {"type": "string", "description": "'Completion of Discharge (hoses disconnected)' 칸의 일시. " + TIME},
        "amount_claimed": {"type": "number", "description": "'Amount Claimed'의 금액. 통화 기호와 쉼표를 뺀 숫자. 없으면 0."},
    },
    "접수기록_추출": {
        "claim_no": {"type": "string", "description": "청구 번호. 'Claim No.' 칸의 값. " + NONE},
        "completion_of_discharge": {"type": "string", "description": "'Completion of Discharge (hoses disconnected)' 칸의 일시. " + TIME},
        "time_bar_date": {"type": "string", "description": "'Time Bar Date' 칸의 날짜(청구 기한일). 'Date Claim Received'가 아니다. " + DATE},
        "received_date": {"type": "string", "description": "'Date Claim Received' 칸의 날짜(청구 접수일). 'Time Bar Date'가 아니다. " + DATE},
    },
    "도착통지서_추출": {
        "vessel_name": VESSEL, "voyage_no": VOYAGE,
        "arrival_time": {"type": "string", "description": "'Arrived at Pilot Station' 일시. " + TIME},
        "nor_tendered_time": {"type": "string", "description": "'Notice of Readiness Tendered' 일시. " + TIME},
        "master_signed": {"type": "boolean", "description": "Master 서명란. " + SIGNED},
    },
    "시간기록_추출": {
        "vessel_name": {"type": "string", "description": "선박명. '2. Vessel's name' 칸에서 ' / Voy.' 앞부분(다른 양식에서는 'Vessel' 칸). 예: 'MT HANBIT PIONEER'. " + NONE},
        "voyage_no": {"type": "string", "description": "항차 번호. '2. Vessel's name' 칸에서 'Voy.' 뒤의 값(다른 양식에서는 'Voyage No.' 칸). 예: 'HP-2608'. " + NONE},
        "arrival_time": {"type": "string", "description": "'20. Vessel arrived at anchorage' 칸(다른 양식에서는 'Arrived at Pilot Station' 행)의 일시. " + TIME},
        "hoses_disconnected_time": {"type": "string", "description": "'15. Hoses disconnected (disch.)' 칸(다른 양식에서는 'Hoses Disconnected' 행)의 일시. '14. Discharging completed'나 'Completed Discharge'가 아니다. 칸이 가려졌거나 읽을 수 없으면 옆 칸의 값을 쓰지 말고 빈 문자열. " + TIME},
        "terminal_signed": {"type": "boolean", "description": "'Name and signature (for the Charterers/Shippers/Receivers)' 또는 'Terminal Representative' 서명란. " + SIGNED},
        "readability": {"type": "string", "description": READ},
    },
    "펌핑기록_추출": {
        "vessel_name": {"type": "string", "description": "선박명. 'MV' 칸에서 ' / Voy.' 앞부분만. 뒤에 붙은 숫자나 기호는 넣지 않는다. 예: 'MT HANBIT PIONEER'. " + NONE},
        "voyage_no": {"type": "string", "description": "항차 번호. 'MV' 칸에서 'Voy.' 뒤의 값. 예: 'HP-2608'. " + NONE},
        "chief_officer_signed": {"type": "boolean", "description": "Chief Officer 서명란. " + SIGNED},
        "terminal_signed": {"type": "boolean", "description": "표 아래 오른쪽 'Terminal Representative (countersignature)' 서명란. 왼쪽 Chief Officer 서명과 혼동하지 않는다. " + SIGNED},
    },
    "항의서_추출": {
        "issued_time": {"type": "string", "description": "'Date / Time Issued' 일시. " + TIME},
        "from_vessel": {"type": "string", "description": "'From' 칸에 적힌 선박명. 예: 'MT DOKDO TRADER'. " + NONE},
        "subject": {"type": "string", "description": "'Subject' 칸의 문장 그대로. " + NONE},
    },
}

JUDGE_PROMPT = """당신은 화주사(Charterers) 체선료 정산 담당자의 서류 검증 보조자다. 앞 단계에서 추출된 청구서·접수 기록·도착 통지서·항만 시간 기록·펌핑 기록·항의서 결과만 사용해, 선주가 보낸 체선료 청구 건을 지급 검토로 넘겨도 되는지 1차 판정하라.
문서에 없는 값은 절대 생성하지 마라. 확신이 없으면 단정하지 말고 '검토 필요'로 표기하라. 본 결과는 1차 스크리닝이며 지급·거절의 최종 판단은 정산 담당자가 한다. 청구 금액이 맞는지는 판정하지 않는다.

[입력 형태] 입력은 청구 1건의 서류 여러 종류가 하나의 PDF로 이어 붙은 묶음이다. 특정 문서 종류의 추출 결과가 비어 있다면 그 문서가 제출되지 않았거나 분류·분할이 실패한 것이다. 어느 쪽인지 단정하지 말고 해당 서류를 '누락'으로 기록하라.

[기준 정보] 청구 건의 식별 키는 청구서의 청구 번호(claim_no)와 선박명(vessel_name)이다. 같은 청구 건의 서류인지는 선박명과 항차 번호(voyage_no)로 확인한다.

[판정 기준 — 용선계약 BPVOY4]
1) 청구 기한: 접수 기록의 접수일(received_date)이 기한일(time_bar_date)과 같거나 그보다 앞서야 한다. 기한일은 양하 완료(호스 분리) 후 90일이며 접수 기록에 적힌 값을 그대로 쓴다. 날짜를 직접 계산하지 않는다. 접수일이 기한일과 같은 날이면 충족이다.
2) 필수 서류 5종: Demurrage Claim Invoice, Claim Receipt Record, Notice of Readiness, Statement of Facts, Cargo Pumping Log가 모두 있어야 한다.
3) 터미널 서명: Cargo Pumping Log의 terminal_signed가 true여야 한다. false인데 Letter of Protest가 첨부된 경우, 항의서가 서명을 대신하는지는 용선계약에 명시되어 있지 않으므로 통과로 보지 않고 담당자에게 넘긴다.
4) 시각 일치: 청구서의 completion_of_discharge가 Statement of Facts의 hoses_disconnected_time과 같아야 한다.
5) 동일 청구 건: 서류들의 선박명과 항차 번호가 청구서와 같아야 한다.

[판정 순서 — 반드시 이 순서로]
- 1단계 '검토 필요': 선박명 또는 항차 번호가 청구서와 다른 서류가 있음 / 기준 4)의 두 일시가 다름 / Statement of Facts의 readability가 'unclear'임 / 있는 서류인데 판정에 필요한 날짜·일시가 빈 문자열임 / 펌핑 기록의 terminal_signed가 false인데 Letter of Protest가 첨부되어 있음. 하나라도 해당하면 '검토 필요'로 판정하고 더 진행하지 않는다.
- 2단계 '기한 위험': 접수일이 기한일보다 늦음.
- 3단계 '보완 요청': 필수 서류 5종 중 하나라도 누락 / 펌핑 기록에 터미널 서명이 없고 항의서도 없음.
- 4단계 '지급 검토 가능': 기준 1)~5)를 모두 충족.
거절 사유를 추측으로 만들지 마라.

[출력] 아래 키 다섯 개를 이 순서로, 한 줄에 하나씩 작성하라. 값은 추출 결과에서 가져온다.
claim_no: <청구서의 청구 번호>
vessel_name: <청구서의 선박명>
decision: <지급 검토 가능 | 보완 요청 | 기한 위험 | 검토 필요 중 하나>
reason: <판정 근거 1~2문장, 한국어. 판정을 정한 기준과 실제 값(접수일·기한일·일시·서류 이름)만 적는다. reason 줄은 한 번만 쓰고 줄을 나누지 않는다. terminal_signed 같은 내부 항목 이름은 쓰지 않고 "터미널 서명 없음"처럼 풀어 쓴다>
missing_documents: <누락된 필수 서류의 영문 이름을 JSON 배열로. 이름은 Demurrage Claim Invoice / Claim Receipt Record / Notice of Readiness / Statement of Facts / Cargo Pumping Log 중에서 글자 그대로 쓰고 큰따옴표로 감싼다. 예: ["Notice of Readiness"]. 누락이 없으면 [] 만 쓴다. 서명 없음은 누락이 아니므로 여기에 적지 않는다>
마지막 줄에 decision 값만 한 번 더 적어라."""

FOLLOW_UPS = [
    ("지급검토_메모", "지급 검토 가능", "앞선 판정 [[청구_판정]] 결과가 '지급 검토 가능'인 건이다. 정산 담당자용 지급 검토 메모 초안을 작성하라. 문서에 없는 값은 절대 생성하지 마라.\n구성: 청구 번호·선박명·항차 / 확인된 사항(필수 서류 5종, 터미널 서명, 접수일과 기한일, 양하 완료 일시) / 담당자가 이어서 할 일(체선 시간과 금액 검산). 300자 이내, 한국어."),
    ("보완요청_초안", "보완 요청", "앞선 판정 [[청구_판정]] 결과가 '보완 요청'인 건이다. 선주에게 보낼 보완 요청 서신 초안을 영어로 작성하라. 문서에 없는 값은 절대 생성하지 마라.\n구성: Subject(Claim No., Vessel) / 빠졌거나 서명이 없는 서류 목록(missing_documents와 reason의 내용을 영어로 옮겨 적는다. 한국어 문장이나 terminal_signed 같은 내부 항목 이름을 그대로 넣지 않는다) / 근거(BPVOY4에 따라 증빙 일체가 기한일까지 접수되어야 함)와 기한일 / Charterers' rights reserved 문구. 150 words 이내."),
    ("기한위험_메모", "기한 위험", "앞선 판정 [[청구_판정]] 결과가 '기한 위험'인 건이다. 정산 담당자용 메모 초안을 작성하라. 문서에 없는 값은 절대 생성하지 마라.\n구성: 청구 번호·선박명 / 접수일과 기한일, 며칠 늦었는지는 계산하지 말고 두 날짜만 적는다 / 담당자가 확인할 것(접수일 기록이 맞는지, 기한 연장 합의가 있었는지). 지급 거절을 단정하지 않는다. 300자 이내, 한국어."),
    ("검토필요_메모", "검토 필요", "앞선 판정 [[청구_판정]] 결과가 '검토 필요'인 건이다. 정산 담당자용 확인 메모 초안을 작성하라. 문서에 없는 값은 절대 생성하지 마라.\n구성: 청구 번호·선박명 / 검토 필요 사유(다른 선박 서류, 일시 불일치, 판독 불가 중 해당 항목과 실제 값) / 담당자가 원문에서 확인할 위치. 300자 이내, 한국어."),
]
OTHER_NODE = ("미분류_안내", "이 문서는 체선료 청구 검증용 6종(청구서·접수 기록·도착 통지서·항만 시간 기록·펌핑 기록·항의서)에 해당하지 않아 분류되지 않았다. 문서에 없는 값은 절대 생성하지 마라.\n한 줄로 작성하라: likely_document_type=<문서가 무엇으로 보이는지>, review_reason=<왜 분류되지 않았는지>, operator_action=<담당자가 할 일: 무시 / 선주에게 올바른 서류 요청 / 수동 확인>.")


def edge(index: int, source: dict, target: dict, condition: str | None = None) -> dict:
    item = {"id": f"e{index}", "source": source, "target": target}
    return {**item, "condition": {"conditionName": condition}} if condition else item


def build(example: dict, decisions: list[str]) -> dict:
    config = copy.deepcopy(example["agentConfig"])
    classify_name = "청구서류-분류"
    config["agent_name"] = AGENT
    config["documentParseConfiguration"]["customName"] = "청구서류-파싱"
    classify = config["documentClassifyConfiguration"]
    classify["customName"] = classify_name
    classify["schema"]["json_schema"]["schema"]["oneOf"] = (
        [{"const": key, "description": text} for key, _, text in CLASSES] + [{"const": "Other", "description": OTHER}])
    template = config["informationExtractConfiguration"]["schemas"][0]
    config["informationExtractConfiguration"]["schemas"] = [
        {**copy.deepcopy(template),
         "json_schema": {"name": name, "schema": {"type": "object", "properties": FIELDS[name]}},
         "userSystemPrompt": BOUNDARY + "영문 문서이며 값은 영문 표기 그대로 읽는다."}
        for _, name, _ in CLASSES]
    config["informationExtractConfiguration"]["categorySchemaMapping"] = {key: name for key, name, _ in CLASSES}
    judge = {"name": JUDGE, "modelName": "", "prompt": JUDGE_PROMPT, "enumEnabled": True, "enumValues": decisions}
    follow = [{"name": name, "modelName": "", "prompt": prompt} for name, _, prompt in FOLLOW_UPS]
    config["instructConfiguration"] = {
        "nodes": [judge, *follow, {"name": OTHER_NODE[0], "modelName": "", "prompt": OTHER_NODE[1]}],
        "connectionMapping": {
            **{name: {"targetType": "instruct", "instructNodeName": JUDGE} for name, _, _ in FOLLOW_UPS},
            OTHER_NODE[0]: {"targetType": "classify", "classifyClassName": "Other"}},
    }
    cls = {"nodeType": "classify", "name": classify_name}
    edges = [({"nodeType": "parse"}, cls, None)]
    edges += [(cls, {"nodeType": "extract", "name": name}, key) for key, name, _ in CLASSES]
    edges += [(cls, {"nodeType": "instruct", "name": OTHER_NODE[0]}, "Other")]
    edges += [({"nodeType": "extract", "name": name}, {"nodeType": "merge", "name": MERGE}, None) for _, name, _ in CLASSES]
    edges += [({"nodeType": "merge", "name": MERGE}, {"nodeType": "instruct", "name": JUDGE}, None)]
    edges += [({"nodeType": "instruct", "name": JUDGE}, {"nodeType": "instruct", "name": name}, value)
              for name, value, _ in FOLLOW_UPS]
    config["pipelineEdges"] = [edge(i, s, t, c) for i, (s, t, c) in enumerate(edges)]
    return {**example, "exportedFrom": {**example["exportedFrom"], "agentName": AGENT}, "agentConfig": config}


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.path.insert(0, str(Path(__file__).parent))
    from cases import DECISIONS

    example = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    target = ROOT / "work" / "workflow_draft.json"
    target.write_text(json.dumps(build(example, DECISIONS), ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"만들었습니다: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
