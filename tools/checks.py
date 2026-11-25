"""정답지 JSON 자체의 정합성 검사 (파일 시스템을 건드리지 않는 순수 함수)."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

ERROR, WARN, INFO = "오류", "주의", "정보"
REQUIRED_TOP = ("task", "unit", "output_keys", "decision_values", "cases")
REQUIRED_CASE = ("case_id", "file", "documents", "answer")
MIN_DOCUMENTS = 10
NON_ISO_DATE = re.compile(r"^\d{4}\s*[./년]\s*\d{1,2}\s*[./월]\s*\d{1,2}\s*일?$")


@dataclass(frozen=True)
class Finding:
    level: str
    where: str
    message: str

    def __str__(self) -> str:
        return f"[{self.level}] {self.where}: {self.message}"


def normalize(text: str) -> str:
    """대소문자·밑줄·공백 차이를 지운 비교용 문자열."""
    return re.sub(r"[\W_]+", "", str(text).lower())


def case_files(case: dict[str, Any]) -> list[str]:
    files = case.get("file")
    if isinstance(files, str):
        return [files]
    if isinstance(files, list):
        return [f for f in files if isinstance(f, str)]
    return []


def check_structure(answer: Any) -> list[Finding]:
    if not isinstance(answer, dict):
        return [Finding(ERROR, "정답지", "최상위가 { } 객체가 아닙니다.")]
    findings = [
        Finding(ERROR, "정답지", f"'{key}' 칸이 없습니다.")
        for key in REQUIRED_TOP
        if key not in answer
    ]
    cases = answer.get("cases")
    if not isinstance(cases, list) or not cases:
        return [*findings, Finding(ERROR, "cases", "케이스가 한 건도 없습니다.")]
    seen: set[str] = set()
    for index, case in enumerate(cases, start=1):
        where = f"cases[{index}]"
        if not isinstance(case, dict):
            findings.append(Finding(ERROR, where, "케이스가 { } 객체가 아닙니다."))
            continue
        findings.extend(
            Finding(ERROR, where, f"'{key}' 칸이 없습니다.")
            for key in REQUIRED_CASE
            if key not in case
        )
        case_id = str(case.get("case_id", ""))
        if case_id in seen:
            findings.append(Finding(ERROR, where, f"case_id '{case_id}'가 겹칩니다."))
        seen.add(case_id)
        if not case.get("documents"):
            findings.append(Finding(ERROR, where, "documents가 비어 있습니다."))
    return findings


def _valid_cases(answer: dict[str, Any]) -> list[dict[str, Any]]:
    cases = answer.get("cases")
    if not isinstance(cases, list):
        return []
    return [c for c in cases if isinstance(c, dict) and isinstance(c.get("answer"), dict)]


def check_answer_keys(answer: dict[str, Any]) -> list[Finding]:
    """answer의 키가 output_keys와 글자 단위로 같은지 본다. 틀린 키는 0점이다."""
    output_keys = list(answer.get("output_keys") or [])
    findings: list[Finding] = []
    if len(set(output_keys)) != len(output_keys):
        findings.append(Finding(ERROR, "output_keys", "같은 키가 두 번 적혀 있습니다."))
    for case in _valid_cases(answer):
        where = f"케이스 {case.get('case_id')}"
        actual = set(case["answer"])
        missing = [k for k in output_keys if k not in actual]
        extra = sorted(actual - set(output_keys))
        for key in missing:
            twin = next((e for e in extra if normalize(e) == normalize(key)), None)
            hint = f" ('{twin}'로 적혀 있습니다 — 표기가 다르면 다른 키입니다)" if twin else ""
            findings.append(Finding(ERROR, where, f"answer에 '{key}'가 없습니다.{hint}"))
        for key in extra:
            findings.append(Finding(ERROR, where, f"answer의 '{key}'는 output_keys에 없는 키입니다."))
    return findings


def decision_keys(answer: dict[str, Any]) -> list[str]:
    """값이 decision_values에서 나오는 키(판정 키)를 찾는다."""
    allowed = set(answer.get("decision_values") or [])
    found = []
    for key in answer.get("output_keys") or []:
        values = [c["answer"].get(key) for c in _valid_cases(answer) if key in c["answer"]]
        if values and all(isinstance(v, str) for v in values) and any(v in allowed for v in values):
            found.append(key)
    return found


def check_decision_values(answer: dict[str, Any]) -> list[Finding]:
    allowed = list(answer.get("decision_values") or [])
    keys = decision_keys(answer)
    if allowed and not keys:
        return [Finding(WARN, "decision_values", "이 값들을 쓰는 키를 answer에서 찾지 못했습니다.")]
    findings: list[Finding] = []
    used: set[str] = set()
    for case in _valid_cases(answer):
        for key in keys:
            value = case["answer"].get(key)
            used.add(value)
            if value not in allowed:
                twin = next((a for a in allowed if normalize(a) == normalize(value)), None)
                hint = f" ('{twin}'와 표기가 다릅니다)" if twin else ""
                findings.append(Finding(
                    ERROR, f"케이스 {case.get('case_id')}",
                    f"'{key}' 값 '{value}'가 decision_values에 없습니다.{hint}",
                ))
    findings.extend(
        Finding(WARN, "decision_values", f"'{value}'가 나오는 케이스가 없습니다. 이 판정을 시험하지 않습니다.")
        for value in allowed
        if value not in used
    )
    return findings


def _type_name(value: Any) -> str:
    if isinstance(value, bool):
        return "참/거짓"
    if isinstance(value, (int, float)):
        return "숫자"
    return {str: "문자열", list: "목록", dict: "객체", type(None): "null"}.get(type(value), "기타")


def check_value_formats(answer: dict[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    types_by_key: dict[str, set[str]] = {}
    for case in _valid_cases(answer):
        where = f"케이스 {case.get('case_id')}"
        for key, value in case["answer"].items():
            types_by_key.setdefault(key, set()).add(_type_name(value))
            if value is None:
                findings.append(Finding(WARN, where, f"'{key}'가 null입니다. 값이 없는 목록은 []로 둡니다."))
            if not isinstance(value, str):
                continue
            if value != value.strip():
                findings.append(Finding(ERROR, where, f"'{key}' 값 앞뒤에 공백이 있습니다."))
            if NON_ISO_DATE.match(value.strip()):
                findings.append(Finding(WARN, where, f"'{key}' 값 '{value}'는 날짜로 보입니다. 2004-05-12 형식으로 씁니다."))
    findings.extend(
        Finding(ERROR, f"키 '{key}'", f"케이스마다 값 형식이 다릅니다: {', '.join(sorted(kinds))}")
        for key, kinds in types_by_key.items()
        if len(kinds - {"null"}) > 1
    )
    return findings


def count_documents(answer: dict[str, Any]) -> int:
    cases = answer.get("cases") if isinstance(answer, dict) else None
    if not isinstance(cases, list):
        return 0
    return sum(len(c.get("documents") or []) for c in cases if isinstance(c, dict))


def check_document_count(answer: dict[str, Any]) -> list[Finding]:
    total = count_documents(answer)
    if total < MIN_DOCUMENTS:
        return [Finding(ERROR, "데이터셋", f"문서가 {total}건입니다. {MIN_DOCUMENTS}건 이상이어야 합니다.")]
    return [Finding(INFO, "데이터셋", f"문서 {total}건, 케이스 {len(answer.get('cases') or [])}건.")]


def check_answer(answer: Any) -> list[Finding]:
    structure = check_structure(answer)
    if any(f.level == ERROR and f.where == "정답지" for f in structure) or not isinstance(answer, dict):
        return structure
    return [
        *structure,
        *check_answer_keys(answer),
        *check_decision_values(answer),
        *check_value_formats(answer),
        *check_document_count(answer),
    ]
