"""정답지와 제출 폴더의 파일·워크플로 JSON·유형표를 서로 맞춰 보는 검사.

파일과 구조가 서로 맞는지만 본다. 판정 규칙이 옳은지, Studio 실행 결과가 정답과 같은지는 보지 않는다.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Iterator

from checks import ERROR, INFO, WARN, Finding, case_files, decision_keys, normalize

TYPE_MARKS = "①②③④"
MIN_TYPES = 3
IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
LINE_LABEL = re.compile(r"^[ 	]*([A-Za-z_][A-Za-z0-9_]*)[ 	]*:", re.MULTILINE)
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


def _judge_nodes(node: Any) -> Iterator[dict[str, Any]]:
    """판정 Instruct 노드: 지시문(prompt)이 있고 판정값 enum이 켜진 노드."""
    if isinstance(node, dict):
        if isinstance(node.get("prompt"), str) and (node.get("enumEnabled") or node.get("enumValues")):
            yield node
        for value in node.values():
            yield from _judge_nodes(value)
    elif isinstance(node, list):
        for item in node:
            yield from _judge_nodes(item)


def _line_labels(prompt: str) -> list[str]:
    """지시문에서 '키: <값>'처럼 행의 맨 앞에 놓인 라벨만 순서대로 모은다. 문장 속에 언급된 이름은 세지 않는다."""
    return [match.group(1) for match in LINE_LABEL.finditer(prompt)]


def _check_judge_node(name: str, node: dict[str, Any], output_keys: list[str], decision_values: list[str] | None) -> list[Finding]:
    where = f"{name} · 판정 노드 '{node.get('name', '?')}'"
    labels = _line_labels(node["prompt"])
    identifiers = set(IDENTIFIER.findall(node["prompt"]))
    findings: list[Finding] = []
    for key in output_keys:
        if key in labels:
            continue
        twins = sorted(t for t in identifiers if t != key and (normalize(t) == normalize(key) or key in t))
        hint = f" 비슷한 이름 {twins}가 있습니다 — 표기가 다르면 0점입니다." if twins else ""
        findings.append(Finding(ERROR, where, f"출력 키 '{key}'가 출력 지시의 행 시작 라벨('{key}: ...')로 없습니다.{hint}"))
    found = [label for label in labels if label in output_keys]
    if not findings and found != output_keys:
        findings.append(Finding(WARN, where, f"출력 지시의 키 순서 {found}가 정답지의 output_keys 순서 {output_keys}와 다릅니다."))
    enum = list(node.get("enumValues") or [])
    if decision_values is not None and enum != list(decision_values):
        level = ERROR if sorted(enum) != sorted(decision_values) else WARN
        findings.append(Finding(level, where, f"판정값 enum {enum}이 정답지의 decision_values {list(decision_values)}와 다릅니다."))
    if decision_values is not None and not node.get("enumEnabled"):
        findings.append(Finding(WARN, where, "판정값 enum이 꺼져 있습니다(enumEnabled)."))
    return findings


def check_workflow_keys(output_keys: list[str], workflows: dict[str, Any], decision_values: list[str] | None = None) -> list[Finding]:
    """내보낸 워크플로 JSON의 판정 Instruct 노드가 출력 키를 행 시작 라벨로 지시하고, enum이 판정값과 같은지 본다.

    구조 검사다. 다른 노드나 설명 문장에 키와 비슷한 글자가 있는 것만으로는 통과시키지 않는다.
    워크플로가 실제로 그 키와 값을 출력하는지(Studio 실행 정확도)는 이 검사로 알 수 없다.
    """
    if not workflows:
        return [Finding(WARN, "workflow", "워크플로 설정 JSON이 없어 출력 키를 대조하지 못했습니다.")]
    findings: list[Finding] = []
    for name, workflow in workflows.items():
        nodes = list(_judge_nodes(workflow))
        if len(nodes) != 1:
            texts = list(_strings(workflow))
            seen = [key for key in output_keys if any(key in text for text in texts)]
            twins = sorted({t for text in texts for t in IDENTIFIER.findall(text) for key in output_keys
                            if t != key and normalize(t) == normalize(key)})
            hint = f" 비슷한 이름 {twins}가 있습니다 — 표기가 다르면 0점입니다." if twins else ""
            findings.append(Finding(ERROR, name, (
                f"판정값 enum이 켜진 Instruct 노드가 {len(nodes)}개라 출력 키를 대조하지 못했습니다. "
                f"JSON 어딘가에 글자가 있는 키 {seen}는 참고일 뿐 통과가 아닙니다.{hint}")))
            continue
        checked = _check_judge_node(name, nodes[0], output_keys, decision_values)
        findings.extend(checked or [Finding(INFO, name, (
            f"판정 노드 '{nodes[0].get('name', '?')}'의 출력 지시에 키 {len(output_keys)}개가 행 시작 라벨로 있고"
            + (f" enum {len(decision_values)}개가 decision_values와 같습니다." if decision_values is not None else " (enum은 대조하지 않음).")
            + " 구조 검사이며 Studio 실행 정확도 검증이 아닙니다."))])
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
