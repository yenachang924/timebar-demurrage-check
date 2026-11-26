"""채점·검사 도구가 잘못된 성공을 만들지 않는지 본다 (도구 동작 시험, Studio 정확도 검증이 아님)."""
from __future__ import annotations

import json

import pytest

import score
from checks import ERROR, INFO, WARN
from file_checks import check_workflow_keys

KEYS = ["claim_no", "vessel_name", "decision", "reason", "missing_documents"]
DECISIONS = ["지급 검토 가능", "보완 요청", "기한 위험", "검토 필요"]
GOOD = {"claim_no": "DMG-1", "vessel_name": "MT A", "decision": "보완 요청", "reason": "필수 서류 누락",
        "missing_documents": ["Notice of Readiness"]}


def sheet(*case_ids: str) -> dict:
    return {"output_keys": KEYS, "decision_values": DECISIONS,
            "cases": [{"case_id": case_id, "answer": dict(GOOD)} for case_id in case_ids]}


def entry(case_id: str, **changes) -> dict:
    return {"case_id": case_id, "output": {**GOOD, **changes}}


def run_cli(tmp_path, capsys, answer, results, *extra):
    answer_path, results_path = tmp_path / "answer.json", tmp_path / "results.json"
    answer_path.write_text(json.dumps(answer, ensure_ascii=False), encoding="utf-8")
    results_path.write_text(json.dumps(results, ensure_ascii=False), encoding="utf-8")
    code = score.main([str(results_path), "--answer", str(answer_path), *extra])
    return code, capsys.readouterr().out


# ---- score.py: 중복·추가 케이스 ----

def test_duplicate_case_id_is_an_error_not_an_overwrite():
    with pytest.raises(score.DuplicateCaseError) as error:
        score.to_case_map([entry("A", decision="기한 위험"), entry("A")])
    assert "A" in str(error.value)


def test_duplicate_case_id_fails_the_cli(tmp_path, capsys):
    code, out = run_cli(tmp_path, capsys, sheet("A"), [entry("A", decision="기한 위험"), entry("A")])
    assert code == 2
    assert "중복" in out


def test_extra_case_does_not_succeed(tmp_path, capsys):
    code, out = run_cli(tmp_path, capsys, sheet("A"), [entry("A"), entry("EXTRA")])
    assert code == 1
    assert "EXTRA" in out


def test_extra_case_needs_an_explicit_option_and_is_reported_as_partial(tmp_path, capsys):
    code, out = run_cli(tmp_path, capsys, sheet("A"), [entry("A"), entry("EXTRA")], "--allow-extra")
    assert code == 0
    assert "부분 비교" in out and "EXTRA" in out


def test_case_subset_shows_its_denominator(tmp_path, capsys):
    code, out = run_cli(tmp_path, capsys, sheet("A", "B", "C"), [entry("A")], "--cases", "A")
    assert code == 0
    assert "부분 비교" in out and "케이스 1/3" in out


def test_missing_case_without_subset_fails(tmp_path, capsys):
    code, _ = run_cli(tmp_path, capsys, sheet("A", "B"), [entry("A")])
    assert code == 1


# ---- score.py: 키 종류와 관측 상태 ----

def test_rows_carry_key_kinds():
    rows = score.compare(sheet("A"), {"A": dict(GOOD)})
    assert {row["key"]: row["kind"] for row in rows} == {
        "claim_no": score.FIXED, "vessel_name": score.FIXED, "decision": score.FIXED,
        "reason": score.SENTENCE, "missing_documents": score.LIST}


def test_reason_wording_is_reported_separately_from_fixed_values(tmp_path, capsys):
    code, out = run_cli(tmp_path, capsys, sheet("A"), [entry("A", reason="NOR이 빠져 있음")])
    summary = score.summarize(score.compare(sheet("A"), {"A": {**GOOD, "reason": "NOR이 빠져 있음"}}))
    assert summary[score.FIXED] == {"total": 3, "same": 3}
    assert summary[score.LIST] == {"total": 1, "same": 1}
    assert summary[score.SENTENCE] == {"total": 1, "same": 0}
    assert code == 1
    assert "의미" in out and "운영진" in out


def test_key_subset_is_labelled_partial(tmp_path, capsys):
    results = [{"case_id": "A", "output": {"decision": "보완 요청", "missing_documents": ["Notice of Readiness"]}}]
    code, out = run_cli(tmp_path, capsys, sheet("A"), results, "--keys", "decision,missing_documents")
    assert code == 0
    assert "부분 비교" in out and "키 2/5" in out


def test_unobserved_value_is_not_counted_as_a_match():
    statuses = {"A": {"vessel_name": score.UNOBSERVED}}
    rows = score.compare(sheet("A"), {"A": dict(GOOD)}, statuses=statuses)
    row = next(r for r in rows if r["key"] == "vessel_name")
    assert row["status"] == score.UNOBSERVED and row["reason"] == "미관측"
    summary = score.summarize(rows)
    assert summary[score.FIXED] == {"total": 3, "same": 2}
    assert summary["unobserved"] == 1


def test_status_sidecar_marks_values_unobserved(tmp_path, capsys):
    side = tmp_path / "status.json"
    side.write_text(json.dumps({"default": {"vessel_name": "미관측"}}, ensure_ascii=False), encoding="utf-8")
    code, out = run_cli(tmp_path, capsys, sheet("A"), [entry("A")], "--status", str(side))
    assert code == 1
    assert "미관측 1" in out


def test_status_inside_the_run_file_is_read():
    data = [{**entry("A"), "status": {"vessel_name": "미관측"}}, {**entry("B"), "status": "원문"}]
    statuses = score.read_statuses(data, None)
    assert statuses["A"]["vessel_name"] == score.UNOBSERVED
    assert statuses["B"]["*"] == score.RAW


def test_unknown_status_is_rejected():
    with pytest.raises(ValueError):
        score.read_statuses([{**entry("A"), "status": {"vessel_name": "대충 봄"}}], None)


def test_summary_counts_raw_and_transcribed_separately():
    rows = score.compare(sheet("A", "B"), {"A": dict(GOOD), "B": dict(GOOD)}, statuses={"A": {"*": score.RAW}})
    assert score.summarize(rows)["status"] == {score.RAW: 5, score.TRANSCRIBED: 5, score.UNOBSERVED: 0}


# ---- file_checks.py: 판정 노드의 출력 지시와 enum ----

def workflow(prompt: str, enum=None, extra_nodes=()) -> dict:
    judge = {"name": "판정", "prompt": prompt, "enumEnabled": True, "enumValues": list(enum or DECISIONS)}
    return {"workflowConfig": {"instructConfiguration": {"nodes": [judge, *extra_nodes]}}}


PROMPT = "[출력] 아래 키를 한 줄에 하나씩.\n" + "\n".join(f"{key}: <값>" for key in KEYS) + "\n마지막 줄에 decision 값만."


def levels(findings, level):
    return [f.message for f in findings if f.level == level]


def test_judge_node_with_all_keys_and_enum_passes():
    findings = check_workflow_keys(KEYS, {"wf.json": workflow(PROMPT)}, DECISIONS)
    assert levels(findings, ERROR) == [] and levels(findings, WARN) == []
    assert any("구조" in m for m in levels(findings, INFO))


def test_key_text_outside_the_judge_node_does_not_pass():
    prompt = PROMPT.replace("claim_no: <값>\n", "")
    other = {"name": "메모", "prompt": "claim_no: 청구 번호를 적는다"}
    findings = check_workflow_keys(KEYS, {"wf.json": workflow(prompt, extra_nodes=[other])}, DECISIONS)
    assert any("claim_no" in m for m in levels(findings, ERROR))


def test_similar_key_name_does_not_pass():
    prompt = PROMPT.replace("claim_no: <값>", "claim_no_backup: <값>")
    findings = check_workflow_keys(KEYS, {"wf.json": workflow(prompt)}, DECISIONS)
    assert any("'claim_no'" in m for m in levels(findings, ERROR))


def test_key_mentioned_only_inside_a_sentence_does_not_pass():
    prompt = PROMPT.replace("vessel_name: <값>", "선박명은 vessel_name 항목을 참고한다")
    findings = check_workflow_keys(KEYS, {"wf.json": workflow(prompt)}, DECISIONS)
    assert any("vessel_name" in m for m in levels(findings, ERROR))


def test_enum_must_equal_decision_values():
    findings = check_workflow_keys(KEYS, {"wf.json": workflow(PROMPT, enum=DECISIONS[:3] + ["검토필요"])}, DECISIONS)
    assert any("enum" in m and "검토필요" in m for m in levels(findings, ERROR))


def test_workflow_without_a_judge_node_is_not_a_pass():
    findings = check_workflow_keys(["claim_no"], {"wf.json": {"note": "claim_no_backup"}}, DECISIONS)
    assert levels(findings, INFO) == []
    assert levels(findings, ERROR)


def test_key_order_difference_is_a_warning():
    lines = [f"{key}: <값>" for key in ["vessel_name", "claim_no", *KEYS[2:]]]
    findings = check_workflow_keys(KEYS, {"wf.json": workflow("\n".join(lines))}, DECISIONS)
    assert levels(findings, ERROR) == [] and any("순서" in m for m in levels(findings, WARN))


def test_real_submission_judge_node_passes():
    from pathlib import Path
    root = Path(__file__).resolve().parent.parent / "submission"
    wf, answer = root / "TimeBar_최종제출_workflow.json", root / "TimeBar_최종제출_answer.json"
    if not (wf.is_file() and answer.is_file()):
        pytest.skip("제출 파일이 없다")
    sheet_ = json.loads(answer.read_text(encoding="utf-8"))
    findings = check_workflow_keys(sheet_["output_keys"], {wf.name: json.loads(wf.read_text(encoding="utf-8"))},
                                   sheet_["decision_values"])
    assert levels(findings, ERROR) == [] and levels(findings, WARN) == []


# ---- 독립 리뷰에서 재현된 잘못된 성공 경로 (2026-11-26) ----

def test_duplicate_key_in_mapping_shaped_file_fails(tmp_path, capsys):
    answer_path, results_path = tmp_path / "answer.json", tmp_path / "results.json"
    answer_path.write_text(json.dumps(sheet("A"), ensure_ascii=False), encoding="utf-8")
    wrong, right = json.dumps({**GOOD, "decision": "기한 위험"}, ensure_ascii=False), json.dumps(GOOD, ensure_ascii=False)
    results_path.write_text('{"A": ' + wrong + ', "A": ' + right + "}", encoding="utf-8")
    code = score.main([str(results_path), "--answer", str(answer_path)])
    assert code == 2 and "중복" in capsys.readouterr().out


def test_misspelled_status_key_is_rejected(tmp_path, capsys):
    code, out = run_cli(tmp_path, capsys, sheet("A"), [{**entry("A"), "status": {"vesel_name": "미관측"}}])
    assert code == 2 and "vesel_name" in out


def test_status_for_unknown_case_is_rejected(tmp_path, capsys):
    side = tmp_path / "status.json"
    side.write_text(json.dumps({"cases": {"Z": {"vessel_name": "미관측"}}}, ensure_ascii=False), encoding="utf-8")
    code, out = run_cli(tmp_path, capsys, sheet("A"), [entry("A")], "--status", str(side))
    assert code == 2 and "Z" in out


def test_whole_entry_status_beats_a_lower_priority_key_status(tmp_path, capsys):
    side = tmp_path / "status.json"
    side.write_text(json.dumps({"default": {"vessel_name": "전사"}}, ensure_ascii=False), encoding="utf-8")
    code, out = run_cli(tmp_path, capsys, sheet("A"), [{**entry("A"), "status": "미관측"}],
                        "--status", str(side), "--keys", "vessel_name")
    assert code == 1 and "미관측 1" in out


def test_status_of_wrong_type_is_an_input_error(tmp_path, capsys):
    code, _ = run_cli(tmp_path, capsys, sheet("A"), [{**entry("A"), "status": 5}])
    assert code == 2


def test_unverifiable_workflow_is_an_error_not_a_warning():
    off = {"workflowConfig": {"instructConfiguration": {"nodes": [{"name": "판정", "prompt": PROMPT}]}}}
    two = workflow(PROMPT, extra_nodes=[{"name": "판정2", "prompt": PROMPT, "enumEnabled": True, "enumValues": DECISIONS}])
    for wf in (off, two, {"note": "claim_no_backup"}):
        assert levels(check_workflow_keys(KEYS, {"wf.json": wf}, DECISIONS), ERROR)
