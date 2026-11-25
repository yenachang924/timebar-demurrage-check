"""Studio 실행 결과를 정답지와 대조한다. 한 값이라도 다르면 종료 코드 1.

    uv run python tools/score.py work/runs/run01.json [--answer 경로]

실행 결과 파일은 아래 셋 중 하나의 모양이면 된다 (Studio 화면의 출력을 옮겨 적는다).
    {"A": {"키": 값, ...}, "B": {...}}
    [{"case_id": "A", "output": {...}}, ...]
    {"cases": [{"case_id": "A", "answer": {...}}, ...]}
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))

from checks import normalize  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
MISSING = "<없음>"


def to_case_map(data: Any) -> dict[str, dict[str, Any]]:
    if isinstance(data, dict) and isinstance(data.get("cases"), list):
        data = data["cases"]
    if isinstance(data, list):
        return {
            str(item["case_id"]): dict(item.get("output") or item.get("answer") or {})
            for item in data
            if isinstance(item, dict) and "case_id" in item
        }
    if isinstance(data, dict):
        return {str(key): dict(value) for key, value in data.items() if isinstance(value, dict)}
    return {}


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


def compare(answer: dict[str, Any], results: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for case in answer.get("cases") or []:
        case_id = str(case.get("case_id"))
        output = results.get(case_id)
        for key in answer.get("output_keys") or []:
            expected = (case.get("answer") or {}).get(key)
            actual = MISSING if output is None or key not in output else output[key]
            reason = "실행 결과 없음" if output is None else describe(expected, actual)
            rows.append({"case": case_id, "key": key, "expected": expected, "actual": actual, "reason": reason})
    return rows


def find_answer(explicit: str | None) -> Path:
    if explicit:
        return Path(explicit)
    team = json.loads((ROOT / "team.json").read_text(encoding="utf-8-sig"))
    return ROOT / "submission" / f"{team['team']}_{team['phase']}_answer.json"


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="실행 결과 채점")
    parser.add_argument("results")
    parser.add_argument("--answer")
    args = parser.parse_args()
    answer = json.loads(find_answer(args.answer).read_text(encoding="utf-8-sig"))
    results = to_case_map(json.loads(Path(args.results).read_text(encoding="utf-8-sig")))
    rows = compare(answer, results)
    wrong = [row for row in rows if row["reason"]]
    for row in wrong:
        print(f"✗ 케이스 {row['case']} · {row['key']}: 정답 {row['expected']!r} / 출력 {row['actual']!r} — {row['reason']}")
    extra = sorted(set(results) - {str(c.get("case_id")) for c in answer.get("cases") or []})
    if extra:
        print(f"정답지에 없는 케이스가 결과에 있습니다: {extra}")
    correct = len(rows) - len(wrong)
    cases_ok = len({r["case"] for r in rows}) - len({r["case"] for r in wrong})
    print(f"\n값 {correct}/{len(rows)} 일치, 케이스 {cases_ok}/{len({r['case'] for r in rows})} 완전 일치")
    return 1 if wrong else 0


if __name__ == "__main__":
    raise SystemExit(main())
