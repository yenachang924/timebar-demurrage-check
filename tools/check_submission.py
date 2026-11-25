"""제출 폴더 전체를 검사한다. 오류가 있으면 종료 코드 1.

    uv run python tools/check_submission.py [--dir submission] [--team 이름] [--phase 최종제출]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from checks import ERROR, WARN, Finding, check_answer, count_documents  # noqa: E402
from file_checks import (  # noqa: E402
    check_dataset_files, check_deliverables, check_type_table,
    check_workflow_keys, load_json, prefix, read_type_table,
)

ROOT = Path(__file__).resolve().parent.parent
PLACEHOLDER_TEAM = "팀명"
PHASES = ("미션", "최종제출")


def load_team(args: argparse.Namespace) -> tuple[str, str]:
    config_path = ROOT / "team.json"
    config = load_json(config_path) if config_path.is_file() else {}
    return args.team or config.get("team", PLACEHOLDER_TEAM), args.phase or config.get("phase", "최종제출")


def run_checks(folder: Path, team: str, phase: str) -> list[Finding]:
    if team == PLACEHOLDER_TEAM:
        return [Finding(ERROR, "team.json", "팀명이 아직 '팀명'입니다. team.json에 실제 팀 이름을 넣으세요.")]
    if phase not in PHASES:
        return [Finding(ERROR, "team.json", f"phase는 {PHASES} 중 하나여야 합니다.")]
    findings = check_deliverables(folder, team, phase)
    answer_path = folder / f"{prefix(team, phase)}answer.json"
    if not answer_path.is_file():
        return findings
    try:
        answer = load_json(answer_path)
    except json.JSONDecodeError as error:
        return [*findings, Finding(ERROR, answer_path.name, f"JSON 문법 오류: {error}")]
    findings = [*findings, *check_answer(answer)]
    if not isinstance(answer, dict):
        return findings
    findings.extend(check_dataset_files(answer, folder, team, phase))
    workflows = {}
    for path in sorted(folder.glob(f"{prefix(team, phase)}workflow*.json")):
        try:
            workflows[path.name] = load_json(path)
        except json.JSONDecodeError as error:
            findings.append(Finding(ERROR, path.name, f"JSON 문법 오류: {error}"))
    findings.extend(check_workflow_keys(list(answer.get("output_keys") or []), workflows))
    table_path = folder / f"{prefix(team, phase)}유형표.xlsx"
    if table_path.is_file():
        findings.extend(check_type_table(read_type_table(table_path), answer, count_documents(answer)))
    return findings


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="제출물 정합성 검사")
    parser.add_argument("--dir", default=str(ROOT / "submission"))
    parser.add_argument("--team")
    parser.add_argument("--phase", choices=PHASES)
    args = parser.parse_args()
    team, phase = load_team(args)
    findings = run_checks(Path(args.dir), team, phase)
    for level in (ERROR, WARN, "정보"):
        for finding in findings:
            if finding.level == level:
                print(finding)
    errors = sum(f.level == ERROR for f in findings)
    warnings = sum(f.level == WARN for f in findings)
    print(f"\n{team} / {phase}: 오류 {errors}건, 주의 {warnings}건")
    print("제출을 막는 오류가 있습니다." if errors else "도구가 볼 수 있는 범위에서는 오류가 없습니다. Studio 실행 결과는 score.py로 따로 확인하세요.")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
