"""정답지와 제출 폴더의 파일·워크플로 JSON·유형표를 서로 맞춰 보는 검사."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Iterator

from checks import ERROR, INFO, WARN, Finding, case_files, decision_keys, normalize

TYPE_MARKS = "①②③④"
MIN_TYPES = 3
IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
COLUMN_HINTS = {
    "file": "파일", "unit": "판정 단위", "kind": "문서 종류",
    "type": "유형", "purpose": "시험 목적", "expected": "기대 결과",
}
FINAL_ONLY = ("발표자료.pdf",)
COMMON = ("설계서.pdf", "answer.json", "유형표.xlsx")


def prefix(team: str, phase: str) -> str:
    return f"{team}_{phase}_"


def check_dataset_files(answer: dict[str, Any], folder: Path, team: str, phase: str) -> list[Finding]:
    findings: list[Finding] = []
    start = prefix(team, phase)
    owners: dict[str, str] = {}
    for case in answer.get("cases") or []:
        if not isinstance(case, dict):
            continue
        case_id = str(case.get("case_id"))
        where = f"케이스 {case_id}"
        files = case_files(case)
        if not files:
            findings.append(Finding(ERROR, where, "file이 비어 있습니다."))
        for name in files:
            if not (folder / name).is_file():
                findings.append(Finding(ERROR, where, f"'{name}' 파일이 {folder.name}/에 없습니다."))
            if not name.startswith(start):
                findings.append(Finding(ERROR, where, f"'{name}'의 이름이 '{start}'로 시작하지 않습니다."))
            if len(files) > 1 and f"_{case_id}_" not in name:
                findings.append(Finding(WARN, where, f"통합 업로드 파일 '{name}'에 case_id가 없습니다 (예: {start}{case_id}_신청서.pdf)."))
            if name in owners:
                findings.append(Finding(WARN, where, f"'{name}'이 케이스 {owners[name]}에도 적혀 있습니다."))
            owners[name] = case_id
    return findings


def _strings(node: Any) -> Iterator[str]:
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for key, value in node.items():
            yield str(key)
            yield from _strings(value)
    elif isinstance(node, list):
        for item in node:
            yield from _strings(item)


def check_workflow_keys(output_keys: list[str], workflows: dict[str, Any]) -> list[Finding]:
    """내보낸 워크플로 JSON 어딘가에 출력 키가 글자 그대로 있는지 본다."""
    if not workflows:
        return [Finding(WARN, "workflow", "워크플로 설정 JSON이 없어 출력 키를 대조하지 못했습니다.")]
    texts = [text for wf in workflows.values() for text in _strings(wf)]
    identifiers = {token for text in texts for token in IDENTIFIER.findall(text)}
    findings: list[Finding] = []
    for key in output_keys:
        if any(key in text for text in texts):
            continue
        twins = sorted(t for t in identifiers if normalize(t) == normalize(key) and t != key)
        hint = f" 비슷한 이름 {twins}가 있습니다 — 표기가 다르면 0점입니다." if twins else ""
        findings.append(Finding(ERROR, "workflow", f"출력 키 '{key}'를 워크플로 JSON에서 찾지 못했습니다.{hint}"))
    if not findings:
        findings.append(Finding(INFO, "workflow", f"출력 키 {len(output_keys)}개가 모두 워크플로 JSON에 있습니다."))
    return findings


def _header(rows: list[tuple]) -> tuple[int, dict[str, int]] | None:
    for index, row in enumerate(rows[:20]):
        cells = [str(c) if c is not None else "" for c in row]
        columns = {
            name: next((i for i, cell in enumerate(cells) if hint in cell.replace("\n", " ")), -1)
            for name, hint in COLUMN_HINTS.items()
        }
        if columns["unit"] >= 0 and columns["type"] >= 0:
            return index, columns
    return None


def read_type_table(path: Path) -> list[dict[str, str]] | None:
    from openpyxl import load_workbook

    book = load_workbook(path, data_only=True)
    sheet = book["유형표"] if "유형표" in book.sheetnames else book.worksheets[0]
    rows = list(sheet.iter_rows(values_only=True))
    found = _header(rows)
    if found is None:
        return None
    start, columns = found
    table = []
    for row in rows[start + 1:]:
        record = {
            name: str(row[i]).strip() if 0 <= i < len(row) and row[i] is not None else ""
            for name, i in columns.items()
        }
        if record["unit"] or record["kind"]:
            table.append(record)
    return table


def check_type_table(table: list[dict[str, str]] | None, answer: dict[str, Any], documents: int) -> list[Finding]:
    if table is None:
        return [Finding(WARN, "유형표", "'판정 단위'·'유형' 머리글 줄을 찾지 못했습니다. 템플릿 시트를 그대로 썼는지 확인하세요.")]
    findings: list[Finding] = []
    cases = {str(c.get("case_id")): c for c in answer.get("cases") or [] if isinstance(c, dict)}
    if len(table) < 10:
        findings.append(Finding(ERROR, "유형표", f"{len(table)}줄입니다. 문서 1건당 1줄, 10줄 이상이어야 합니다."))
    elif len(table) != documents:
        findings.append(Finding(WARN, "유형표", f"{len(table)}줄인데 정답지의 문서는 {documents}건입니다."))
    marks = {m for row in table for m in TYPE_MARKS if m in row["type"]}
    if len(marks) < MIN_TYPES:
        findings.append(Finding(ERROR, "유형표", f"유형이 {len(marks)}가지뿐입니다 ({''.join(sorted(marks)) or '없음'}). ①~④ 중 3가지 이상이어야 합니다."))
    keys = decision_keys(answer)
    seen: set[str] = set()
    for number, row in enumerate(table, start=1):
        where = f"유형표 {number}번 줄"
        if "예시" in row["unit"] or "예시" in row["file"]:
            findings.append(Finding(WARN, where, "예시 줄이 남아 있는 것 같습니다."))
        case_id = next((cid for cid in sorted(cases, key=len, reverse=True) if row["unit"] == cid or row["unit"].startswith(cid + " ")), None)
        if case_id is None:
            findings.append(Finding(ERROR, where, f"판정 단위 '{row['unit']}'가 정답지의 case_id와 맞지 않습니다."))
            continue
        seen.add(case_id)
        expected = [str(cases[case_id]["answer"].get(k)) for k in keys if isinstance(cases[case_id].get("answer"), dict)]
        if expected and not any(value in row["expected"] for value in expected):
            findings.append(Finding(WARN, where, f"기대 결과 '{row['expected']}'에 정답지의 판정 값 {expected}이 없습니다."))
        if row["file"] and not any(name in row["file"] for name in case_files(cases[case_id])):
            findings.append(Finding(WARN, where, f"파일 칸 '{row['file']}'이 정답지의 file과 다릅니다."))
    findings.extend(
        Finding(WARN, "유형표", f"케이스 {case_id}의 문서가 한 줄도 없습니다.")
        for case_id in cases
        if case_id not in seen
    )
    return findings


def _pdf_pages(path: Path) -> int:
    from pypdf import PdfReader

    return len(PdfReader(str(path)).pages)


def check_deliverables(folder: Path, team: str, phase: str) -> list[Finding]:
    start = prefix(team, phase)
    findings = [
        Finding(ERROR, "제출물", f"'{start}{suffix}'가 없습니다.")
        for suffix in (*COMMON, *(FINAL_ONLY if phase == "최종제출" else ()))
        if not (folder / f"{start}{suffix}").is_file()
    ]
    if not list(folder.glob(f"{start}workflow*.json")):
        findings.append(Finding(ERROR, "제출물", f"'{start}workflow.json'이 없습니다."))
    design = folder / f"{start}설계서.pdf"
    if design.is_file() and _pdf_pages(design) != 2:
        findings.append(Finding(WARN, "설계서", f"{_pdf_pages(design)}쪽입니다. 템플릿 분량인 1장(2쪽)으로 맞춥니다."))
    if phase == "최종제출" and not list(folder.glob(f"{start}데모영상*")):
        findings.append(Finding(WARN, "제출물", "데모 영상 파일이 없습니다. URL로 낼 거면 무시하세요 (최대 3분)."))
    return findings


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))
