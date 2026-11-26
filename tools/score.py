"""Studio 실행 결과를 옮겨 적은 파일을 정답지와 글자 그대로 대조한다.

    uv run python tools/score.py work/runs/run01.json [--answer 경로] [--status 경로]
                                 [--cases A,B] [--keys decision,missing_documents] [--allow-extra]

이 도구가 하는 것과 하지 않는 것
- 하는 것: 엄격 문자열 비교. 고정값(청구 번호·선박명·판정값), 목록(누락 서류), 문장(reason)을 따로 집계한다.
- 하지 않는 것: 운영진의 LLM 채점을 재현하지 않는다. reason의 의미가 맞는지는 판단하지 않는다.
  reason 문자열이 다르다는 것은 오답이라는 뜻이 아니고, 같다는 것이 유일한 정답이라는 뜻도 아니다.

종료 코드: 0 = 비교한 범위의 모든 값이 관측되었고 글자 그대로 같음 / 1 = 다르거나, 없거나, 미관측이거나,
정답지 밖 케이스가 있음 / 2 = 입력 자체가 잘못됨(같은 case_id가 두 번 등).

실행 결과 파일은 아래 셋 중 하나의 모양이면 된다 (Studio 화면의 출력을 옮겨 적는다).
    {"A": {"키": 값, ...}, "B": {...}}
    [{"case_id": "A", "output": {...}}, ...]
    {"cases": [{"case_id": "A", "answer": {...}}, ...]}

값을 어떻게 얻었는지(관측 상태)는 '원문'(판정 노드 출력 원문을 보존), '전사'(화면에서 읽어 옮김, 기본값),
'미관측'(그 실행에서 읽지 않음) 가운데 하나다. 미관측 값은 정답과 같게 적혀 있어도 일치로 세지 않는다.
    실행 파일 안: {"case_id": "A", "output": {...}, "status": {"vessel_name": "미관측"}}  또는 "status": "원문"
    별도 파일(--status): {"default": {"vessel_name": "미관측"}, "cases": {"A": {"reason": "원문"}}}
이미 남긴 실행 기록은 고치지 않고 --status 파일로 정정한다.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))

from checks import normalize  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
MISSING = "<없음>"
FIXED, LIST, SENTENCE = "고정값", "목록", "문장"
RAW, TRANSCRIBED, UNOBSERVED = "원문", "전사", "미관측"
STATUSES = (RAW, TRANSCRIBED, UNOBSERVED)
SENTENCE_KEYS = ("reason",)
ALL_KEYS = "*"
EXIT_OK, EXIT_DIFFERENT, EXIT_BAD_INPUT = 0, 1, 2


class DuplicateCaseError(ValueError):
    """같은 case_id가 실행 결과에 두 번 이상 있다. 어느 쪽을 채점할지 도구가 고르지 않는다."""


def _entries(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, dict) and isinstance(data.get("cases"), list):
        data = data["cases"]
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict) and "case_id" in item]
    if isinstance(data, dict):
        return [{"case_id": key, "output": value} for key, value in data.items() if isinstance(value, dict)]
    return []


def to_case_map(data: Any) -> dict[str, dict[str, Any]]:
    entries = _entries(data)
    repeated = sorted(case_id for case_id, count in Counter(str(e["case_id"]) for e in entries).items() if count > 1)
    if repeated:
        raise DuplicateCaseError(
            f"case_id 중복: 같은 case_id가 두 번 이상 있습니다: {repeated}. 반복 실행은 실행(배치)마다 파일을 나눠 따로 채점하세요.")
    return {str(e["case_id"]): dict(e.get("output") or e.get("answer") or {}) for e in entries}


def _status_map(raw: Any, where: str) -> dict[str, str]:
    if raw is not None and not isinstance(raw, (str, dict)):
        raise ValueError(f"{where}: status는 문자열이나 {{키: 상태}} 객체여야 합니다.")
    mapping = {ALL_KEYS: raw} if isinstance(raw, str) else dict(raw or {})
    unknown = sorted({str(value) for value in mapping.values()} - set(STATUSES))
    if unknown:
        raise ValueError(f"{where}: 관측 상태 {unknown}는 {STATUSES} 가운데 하나가 아닙니다.")
    return mapping


def read_statuses(data: Any, sidecar: Any) -> dict[str, dict[str, str]]:
    """케이스·키별 관측 상태. 우선순위: 별도 파일의 cases > 실행 파일 안의 status > 별도 파일의 default."""
    default = _status_map((sidecar or {}).get("default"), "default")
    per_case = (sidecar or {}).get("cases") or {}
    inside = {str(e["case_id"]): _status_map(e.get("status"), f"케이스 {e['case_id']}") for e in _entries(data)}
    names = set(inside) | {str(key) for key in per_case}
    return {
        name: _layer(default, inside.get(name, {}), _status_map(per_case.get(name), f"케이스 {name}"))
        for name in names
    }


def _layer(*stages: dict[str, str]) -> dict[str, str]:
    """낮은 순위부터 겹친다. 윗단계가 전체('*')를 정하면 아랫단계의 키별 상태는 버린다."""
    merged: dict[str, str] = {}
    for stage in stages:
        merged = {**({} if ALL_KEYS in stage else merged), **stage}
    return merged


def status_problems(statuses: dict[str, dict[str, str]], known_keys: list[str], known_cases: set[str]) -> list[str]:
    """정답지에 없는 키나 어디에도 없는 케이스에 상태를 달았는지 본다(오타가 미관측 표시를 조용히 무효로 만든다)."""
    bad_keys = sorted({key for mapping in statuses.values() for key in mapping} - set(known_keys) - {ALL_KEYS})
    bad_cases = sorted(set(statuses) - known_cases)
    return ([f"관측 상태에 정답지에 없는 키가 있습니다: {bad_keys}"] if bad_keys else []) + (
        [f"관측 상태에 실행 결과에도 정답지에도 없는 케이스가 있습니다: {bad_cases}"] if bad_cases else [])


def status_of(statuses: dict[str, dict[str, str]] | None, case_id: str, key: str) -> str:
    mapping = (statuses or {}).get(case_id, {})
    return mapping.get(key) or mapping.get(ALL_KEYS) or TRANSCRIBED


def kind_of(key: str, expected: Any) -> str:
    if isinstance(expected, list):
        return LIST
    return SENTENCE if key in SENTENCE_KEYS else FIXED


def describe(expected: Any, actual: Any) -> str:
    """왜 다른지 한마디. 같으면 빈 문자열."""
    if expected == actual:
        return ""
    if actual == MISSING:
        return "키 없음"
    if isinstance(expected, list) and isinstance(actual, list) and sorted(map(str, expected)) == sorted(map(str, actual)):
        return "목록 순서만 다름"
    if type(expected) is not type(actual) and str(expected) == str(actual):
        return "형식만 다름 (숫자/문자열)"
    if normalize(str(expected)) == normalize(str(actual)):
        return "공백·기호·대소문자만 다름"
    return "값 다름"


def compare(
    answer: dict[str, Any], results: dict[str, dict[str, Any]], statuses: dict[str, dict[str, str]] | None = None,
    keys: list[str] | None = None, cases: list[str] | None = None,
) -> list[dict[str, Any]]:
    rows = []
    for case in answer.get("cases") or []:
        case_id = str(case.get("case_id"))
        if cases is not None and case_id not in cases:
            continue
        output = results.get(case_id)
        for key in answer.get("output_keys") or []:
            if keys is not None and key not in keys:
                continue
            expected = (case.get("answer") or {}).get(key)
            actual = MISSING if output is None or key not in output else output[key]
            status = status_of(statuses, case_id, key)
            if output is None:
                reason = "실행 결과 없음"
            elif status == UNOBSERVED:
                reason = "미관측"
            else:
                reason = describe(expected, actual)
            rows.append({"case": case_id, "key": key, "kind": kind_of(key, expected), "status": status,
                         "expected": expected, "actual": actual, "reason": reason})
    return rows


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_kind = {
        kind: {"total": sum(r["kind"] == kind for r in rows), "same": sum(r["kind"] == kind and not r["reason"] for r in rows)}
        for kind in (FIXED, LIST, SENTENCE)
    }
    all_cases = {r["case"] for r in rows}
    return {
        **by_kind,
        "unobserved": sum(r["reason"] == "미관측" for r in rows),
        "absent": sum(r["reason"] in ("키 없음", "실행 결과 없음") for r in rows),
        "status": {s: sum(r["status"] == s and r["reason"] != "실행 결과 없음" for r in rows) for s in STATUSES},
        "cases": len(all_cases),
        "cases_same": len(all_cases - {r["case"] for r in rows if r["reason"]}),
    }


def report(answer: dict[str, Any], rows: list[dict[str, Any]], extra: list[str], allow_extra: bool,
           keys: list[str] | None, cases: list[str] | None) -> list[str]:
    summary = summarize(rows)
    all_keys = list(answer.get("output_keys") or [])
    all_cases = [str(c.get("case_id")) for c in answer.get("cases") or []]
    used_keys = [k for k in all_keys if keys is None or k in keys]
    lines = [
        f"✗ 케이스 {r['case']} · {r['key']} [{r['kind']}·{r['status']}]: 정답 {r['expected']!r} / 출력 {r['actual']!r} — {r['reason']}"
        for r in rows if r["reason"]
    ]
    if extra:
        verdict = "무시했습니다(--allow-extra)" if allow_extra else "채점되지 않았으므로 성공으로 보지 않습니다"
        lines.append(f"정답지에 없는 케이스가 결과에 있습니다: {extra} — {verdict}.")
    partial = keys is not None or cases is not None or (extra and allow_extra)
    sentence, same_text = summary[SENTENCE], summary[SENTENCE]["same"]
    lines += [
        "",
        f"비교 범위: 케이스 {summary['cases']}/{len(all_cases)}, 키 {len(used_keys)}/{len(all_keys)} ({', '.join(used_keys)})"
        + (" — 부분 비교입니다. 전체 정확도로 쓰지 않습니다." if partial else ""),
        f"고정값 {summary[FIXED]['same']}/{summary[FIXED]['total']} 일치 · 목록 {summary[LIST]['same']}/{summary[LIST]['total']} 일치 (글자 그대로 비교)",
        f"문장 {same_text}/{sentence['total']} 문자열 동일 — 문장은 의미로 채점되므로 이 숫자는 정답률이 아닙니다. 의미 검토는 이 도구가 하지 않습니다.",
        f"관측 상태: 원문 {summary['status'][RAW]} · 전사 {summary['status'][TRANSCRIBED]} · 미관측 {summary['unobserved']} / 값 없음 {summary['absent']}",
        f"비교한 키가 모두 관측되고 같은 케이스 {summary['cases_same']}/{summary['cases']}",
        "이 결과는 옮겨 적은 값의 엄격 문자열 비교입니다. 운영진의 LLM 채점을 재현하지 않습니다.",
    ]
    return lines


def find_answer(explicit: str | None) -> Path:
    if explicit:
        return Path(explicit)
    team = json.loads((ROOT / "team.json").read_text(encoding="utf-8-sig"))
    return ROOT / "submission" / f"{team['team']}_{team['phase']}_answer.json"


def _split(value: str | None) -> list[str] | None:
    return [part.strip() for part in value.split(",") if part.strip()] if value else None


def _no_repeated_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    repeated = sorted(key for key, count in Counter(key for key, _ in pairs).items() if count > 1)
    if repeated:
        raise DuplicateCaseError(f"중복: JSON의 한 객체 안에 같은 키가 두 번 이상 있습니다: {repeated}. 뒤의 값으로 덮어쓰지 않습니다.")
    return dict(pairs)


def _read(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8-sig"), object_pairs_hook=_no_repeated_keys)


def main(argv: list[str] | None = None) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="실행 결과를 정답지와 글자 그대로 대조 (운영진 채점의 재현이 아님)")
    parser.add_argument("results")
    parser.add_argument("--answer", help="정답지 경로. probe 실행에는 probe 전용 정답을 지정한다")
    parser.add_argument("--status", help="관측 상태(원문·전사·미관측)를 적은 별도 JSON")
    parser.add_argument("--cases", help="이 case_id만 비교 (쉼표 구분). 부분 비교로 표시된다")
    parser.add_argument("--keys", help="이 키만 비교 (쉼표 구분). 부분 비교로 표시된다")
    parser.add_argument("--allow-extra", action="store_true", help="정답지 밖 케이스를 무시한다. 부분 비교로 표시된다")
    args = parser.parse_args(argv)
    try:
        answer, data = _read(find_answer(args.answer)), _read(args.results)
        results = to_case_map(data)
        statuses = read_statuses(data, _read(args.status) if args.status else None)
    except (OSError, ValueError) as error:
        print(f"입력 오류: {error}")
        return EXIT_BAD_INPUT
    keys, cases = _split(args.keys), _split(args.cases)
    known_keys = list(answer.get("output_keys") or [])
    known_cases = [str(c.get("case_id")) for c in answer.get("cases") or []]
    unknown = [k for k in keys or [] if k not in known_keys] + [c for c in cases or [] if c not in known_cases]
    if unknown:
        print(f"입력 오류: 정답지에 없는 키 또는 케이스를 지정했습니다: {unknown}")
        return EXIT_BAD_INPUT
    problems = status_problems(statuses, known_keys, set(known_cases) | set(results))
    if problems:
        print("입력 오류: " + " / ".join(problems))
        return EXIT_BAD_INPUT
    rows = compare(answer, results, statuses, keys, cases)
    extra = sorted(set(results) - set(known_cases))
    print("\n".join(report(answer, rows, extra, args.allow_extra, keys, cases)))
    failed = any(row["reason"] for row in rows) or (extra and not args.allow_extra) or not rows
    return EXIT_DIFFERENT if failed else EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
