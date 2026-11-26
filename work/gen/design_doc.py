"""설계서 템플릿(docx)을 채워 work/에 저장한다. PDF 변환은 Word로 따로 한다.

    uv run python work/gen/design_doc.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Pt

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = next((ROOT / "docs" / "reference" / "templates").glob("*/*설계서*.docx"))
CELL_FONT_PT = 8
TOPIC = "유조선 체선료 청구 서류 검증 (가상 화주사 · 용선계약 BPVOY4)"

CARD_CHANGE = (
    "화물을 컨테이너에서 원유 유조선으로, 판정을 '금액 검산'에서 '증빙 완결성 · 터미널 서명 · 청구 기한 · 일시 일치'로 바꿈. "
    "유조선 청구는 금액보다 증빙과 기한에서 효력이 갈리기 때문(BPVOY4 20.1조, The Adventure [2015] EWHC 318). 카드의 문서 3종을 6종으로 늘리고, "
    "카드 예외 3개 대신 무서명, 무서명 + 항의서, 기한 경계값, 다른 선박 서류 혼입, 가려진 스캔, 다른 터미널 양식을 더함."
)
SECTION1 = {
    "업무:": "업무: 화주사 체선료 정산 담당자가 선주가 보낸 청구 서류 묶음을 보고 지급 검토 가능 · 보완 요청 · 기한 위험 · 검토 필요로 1차 판정",
    "문서:": "문서: 6종 — 청구서, 접수 기록, 도착 통지서(NOR), 항만 시간 기록(SOF), 펌핑 기록, 항의서(무서명일 때만) (청구 1건 = PDF 1개)",
    "선정 이유:": "선정 이유: 서류 한 장의 누락 · 무서명 · 기한 초과로 청구 전체의 효력이 갈리는데, 서류 5~6종을 서로 대조해야 판단할 수 있어 놓치기 쉬움",
    "판정 기준:": "판정 기준: 접수일이 기한일(양하 완료 후 90일) 이내 / 필수 5종 제출 / 펌핑 기록에 터미널 서명(없고 항의서도 없으면 보완 요청, 항의서가 있으면 검토 필요) / 청구서와 SOF의 양하 완료 일시 일치 / 선박명 · 항차 일치",
}
KEYS = [
    ("claim_no", "문자열", "청구서의 청구 번호. 예: \"DMG-2026-0410\""),
    ("vessel_name", "문자열", "청구서의 선박명. 예: \"MT HANBIT PIONEER\""),
    ("decision", "지급 검토 가능 | 보완 요청 | 기한 위험 | 검토 필요", "네 값 중 하나만"),
    ("reason", "문자열 (1~2문장)", "판정 근거. 어떤 기준이 충족 · 미달인지 실제 값(접수일 · 기한일 · 일시 · 서류 이름)과 함께"),
    ("missing_documents", "문자열 배열", "빠진 필수 서류의 영문 이름. 없으면 []"),
]
NODES = [
    ("1", "Parse", "스캔본까지 읽어야 해서 OCR을 켬"),
    ("2", "Classify", "한 PDF에 섞인 서류를 6종 + Other로 분할 후 분류. 대상 밖 문서는 Other로 뺌"),
    ("3", "Extract ×6", "서류별로 필요한 값만 뽑음(일시는 YYYY-MM-DD HH:MM로 정규화, 서명 유무는 참/거짓, 판독 상태)"),
    ("4", "Merge", "청구 1건의 추출 결과를 하나로 합쳐 서류끼리 비교할 수 있게 함"),
    ("5", "Instruct (청구_판정)", "판정 순서(검토 필요 → 기한 위험 → 보완 요청 → 지급 검토 가능)대로 출력 키 5개 작성. 기한일은 계산하지 않고 접수 기록의 값과 비교"),
    ("6", "Instruct ×4 + 1", "판정값별 후속 문서 4종(지급 검토 메모, 선주용 보완 요청 서신(영문), 기한 위험 메모, 검토 필요 메모)과 Other 문서의 미분류 안내"),
]
EXCEPTIONS = [
    ("필수 서류 누락", "빠진 서류 이름을 기록하고 선주에게 보완을 요청", "보완 요청"),
    ("펌핑 기록에 터미널 서명 없음", "항의서가 없으면 보완 요청. 있으면 대체 여부를 추측하지 않고 넘김", "보완 요청 / 검토 필요"),
    ("접수일이 기한일과 같은 날", "'기한일 이내'에 포함해 통과로 봄", "지급 검토 가능"),
    ("접수일이 기한일보다 늦음", "거절을 단정하지 않고 두 날짜를 남겨 담당자에게 넘김", "기한 위험"),
    ("일시 불일치 · 다른 선박 서류 · 판독 불가", "추측하지 않고 어느 서류의 어느 값인지 남김", "검토 필요"),
    ("대상 밖 문서(예: 급수 영수증)", "Other로 분류해 안내만 남기고 판정에 쓰지 않음", "영향 없음"),
]


def set_text(paragraph, text: str) -> None:
    for run in paragraph.runs[1:]:
        run._element.getparent().remove(run._element)
    if paragraph.runs:
        paragraph.runs[0].text = text
        paragraph.runs[0].font.color.rgb = None
    else:
        paragraph.add_run(text)


def fill_table(table, lines: list[tuple], header_rows: int = 1) -> None:
    while len(table.rows) < header_rows + len(lines):
        table.add_row()
    for row, line in zip(table.rows[header_rows:], lines):
        for cell, value in zip(row.cells, line):
            set_text(cell.paragraphs[0], value)
    for row in table.rows[header_rows + len(lines):]:
        row._element.getparent().remove(row._element)


def compact(document) -> None:
    """2쪽에 맞추려고 표 안의 글자 크기와 줄 간격을 줄인다."""
    for table in document.tables:
        for row in table.rows:
            for height in row._tr.iter(qn("w:trHeight")):
                height.getparent().remove(height)
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    paragraph.paragraph_format.space_before = Pt(1)
                    paragraph.paragraph_format.space_after = Pt(1)
                    paragraph.paragraph_format.line_spacing = 1.0
                    for run in paragraph.runs:
                        run.font.size = Pt(CELL_FONT_PT)


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    team = json.loads((ROOT / "team.json").read_text(encoding="utf-8"))
    prefix = f"{team['team']}_{team['phase']}_"
    document = Document(TEMPLATE)
    info, keys, nodes, exceptions = document.tables
    values = [team["team"], TOPIC, prefix + "유조선 체선료 청구 서류 검증",
              "U038 (컨테이너 지체료 무료기간 검산)", CARD_CHANGE]
    for row, value in zip(info.rows, values):
        set_text(row.cells[1].paragraphs[0], value)
    for paragraph in document.paragraphs:
        text = paragraph.text
        if text.startswith("- 우리 팀"):
            set_text(paragraph, "- 우리 팀 워크플로우 최종 설계서 -")
        elif text.startswith("1장 분량으로") or text.startswith("누가 어떤 문서를") or text.startswith(
                "정답 값을 내는 노드가") or text.startswith("노드를 순서대로") or text.startswith("서류 누락 · 값 불일치"):
            paragraph._element.getparent().remove(paragraph._element)
        else:
            for start, value in SECTION1.items():
                if text.startswith(start):
                    set_text(paragraph, value)
    fill_table(keys, KEYS)
    fill_table(nodes, NODES)
    for row in nodes.rows[1:]:
        row.cells[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    fill_table(exceptions, EXCEPTIONS)
    compact(document)
    target = ROOT / "work" / f"{prefix}설계서.docx"
    document.save(target)
    print(f"만들었습니다: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
