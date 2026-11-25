from __future__ import annotations

import json

import pytest
from openpyxl import Workbook
from pypdf import PdfWriter

import check_submission
from checks import ERROR, WARN
from conftest import PHASE, TEAM
from file_checks import check_type_table, check_workflow_keys, read_type_table
from score import compare, describe, to_case_map

PREFIX = f"{TEAM}_{PHASE}_"
TYPES = ["① 정상", "② 여러 양식", "④ 저품질"]


def write_pdf(path, pages=1):
    writer = PdfWriter()
    for _ in range(pages):
        writer.add_blank_page(width=595, height=842)
    with path.open("wb") as handle:
        writer.write(handle)


def write_table(path, answer, types=TYPES, header_offset=2):
    book = Workbook()
    sheet = book.active
    sheet.title = "유형표"
    for _ in range(header_offset):
        sheet.append(["안내 문구"])
    sheet.append(["번호", "파일 · 페이지", "판정 단위", "문서 종류", "유형", "시험 목적", "기대 결과(정답)"])
    number = 0
    for case in answer["cases"]:
        for kind in case["documents"]:
            number += 1
            sheet.append([number, f"{case['file']} p.1", f"{case['case_id']} 신청", kind,
                          types[number % len(types)], "판정 확인", case["answer"]["decision"]])
    book.save(path)


@pytest.fixture
def submission(tmp_path, answer):
    (tmp_path / f"{PREFIX}answer.json").write_text(json.dumps(answer, ensure_ascii=False), encoding="utf-8")
    workflow = {"nodes": [{"type": "Instruct", "schema": '{"decision": "", "permit_no": "", "missing_documents": []}'}]}
    (tmp_path / f"{PREFIX}workflow.json").write_text(json.dumps(workflow), encoding="utf-8")
    write_pdf(tmp_path / f"{PREFIX}설계서.pdf", pages=2)
    write_pdf(tmp_path / f"{PREFIX}발표자료.pdf")
    (tmp_path / f"{PREFIX}데모영상.mp4").write_bytes(b"0")
    for case in answer["cases"]:
        write_pdf(tmp_path / case["file"])
    write_table(tmp_path / f"{PREFIX}유형표.xlsx", answer)
    return tmp_path


def levels(findings, level):
    return [f.message for f in findings if f.level == level]


def test_complete_submission_passes(submission):
    findings = check_submission.run_checks(submission, TEAM, PHASE)
    assert levels(findings, ERROR) == []
    assert levels(findings, WARN) == []


def test_placeholder_team_name_blocks(submission):
    assert "팀명" in levels(check_submission.run_checks(submission, "팀명", PHASE), ERROR)[0]


def test_missing_dataset_file_is_error(submission, answer):
    (submission / answer["cases"][0]["file"]).unlink()
    assert any("파일이 " in m and "없습니다" in m for m in levels(check_submission.run_checks(submission, TEAM, PHASE), ERROR))


def test_wrong_file_prefix_is_error(submission, answer):
    answer["cases"][0]["file"] = "set01.pdf"
    write_pdf(submission / "set01.pdf")
    (submission / f"{PREFIX}answer.json").write_text(json.dumps(answer, ensure_ascii=False), encoding="utf-8")
    assert any("로 시작하지 않습니다" in m for m in levels(check_submission.run_checks(submission, TEAM, PHASE), ERROR))


def test_design_doc_page_count_is_warning(submission):
    write_pdf(submission / f"{PREFIX}설계서.pdf", pages=3)
    assert any("3쪽" in m for m in levels(check_submission.run_checks(submission, TEAM, PHASE), WARN))


def test_broken_answer_json_is_reported(submission):
    (submission / f"{PREFIX}answer.json").write_text('{"task": "x",}', encoding="utf-8")
    assert any("JSON 문법 오류" in m for m in levels(check_submission.run_checks(submission, TEAM, PHASE), ERROR))


def test_workflow_key_casing_mismatch_is_error():
    findings = check_workflow_keys(["permit_no"], {"wf.json": {"schema": {"permitNo": "string"}}})
    assert any("permitNo" in m and "0점" in m for m in levels(findings, ERROR))


def test_workflow_missing_is_warning():
    assert levels(check_workflow_keys(["decision"], {}), WARN)


def test_type_table_needs_three_types(tmp_path, answer):
    path = tmp_path / "t.xlsx"
    write_table(path, answer, types=["① 정상", "② 여러 양식"])
    findings = check_type_table(read_type_table(path), answer, 10)
    assert any("2가지뿐" in m for m in levels(findings, ERROR))


def test_type_table_unknown_case_id_is_error(tmp_path, answer):
    path = tmp_path / "t.xlsx"
    write_table(path, answer)
    answer["cases"][0]["case_id"] = "Z"
    findings = check_type_table(read_type_table(path), answer, 10)
    assert any("'A 신청'가 정답지의 case_id와 맞지 않습니다" in m for m in levels(findings, ERROR))


def test_type_table_without_header_is_warning(tmp_path, answer):
    book = Workbook()
    book.active.append(["아무 표"])
    path = tmp_path / "t.xlsx"
    book.save(path)
    assert levels(check_type_table(read_type_table(path), answer, 10), WARN)


def test_score_all_correct(answer):
    results = {c["case_id"]: c["answer"] for c in answer["cases"]}
    assert all(row["reason"] == "" for row in compare(answer, results))


def test_score_reports_each_kind_of_mismatch(answer):
    results = to_case_map([
        {"case_id": "A", "output": {"decision": "적격", "permit_no": "PTW001", "missing_documents": []}},
        {"case_id": "B", "output": {"decision": "적격", "permit_no": "PTW-002"}},
    ])
    reasons = {(r["case"], r["key"]): r["reason"] for r in compare(answer, results)}
    assert reasons[("A", "decision")] == ""
    assert reasons[("A", "permit_no")] == "공백·기호·대소문자만 다름"
    assert reasons[("B", "decision")] == "값 다름"
    assert reasons[("B", "missing_documents")] == "키 없음"
    assert reasons[("C", "decision")] == "실행 결과 없음"


def test_describe_list_order_and_type():
    assert describe(["a", "b"], ["b", "a"]) == "목록 순서만 다름"
    assert describe(3, "3") == "형식만 다름 (숫자/문자열)"
