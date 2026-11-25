from __future__ import annotations

from checks import ERROR, WARN, check_answer, count_documents, decision_keys


def errors(findings):
    return [f.message for f in findings if f.level == ERROR]


def warnings(findings):
    return [f.message for f in findings if f.level == WARN]


def test_valid_answer_has_no_errors_or_warnings(answer):
    findings = check_answer(answer)
    assert errors(findings) == []
    assert warnings(findings) == []


def test_documents_counted_per_document_type(answer):
    assert count_documents(answer) == 10


def test_fewer_than_ten_documents_is_error(answer):
    answer["cases"][0]["documents"] = ["작업허가서"]
    assert any("10건 이상" in m for m in errors(check_answer(answer)))


def test_key_with_different_casing_is_error_with_hint(answer):
    case = answer["cases"][0]["answer"]
    case["permitNo"] = case.pop("permit_no")
    messages = errors(check_answer(answer))
    assert any("'permit_no'가 없습니다" in m and "permitNo" in m for m in messages)
    assert any("'permitNo'는 output_keys에 없는 키" in m for m in messages)


def test_missing_top_level_field_is_error(answer):
    del answer["decision_values"]
    assert any("'decision_values' 칸이 없습니다" in m for m in errors(check_answer(answer)))


def test_duplicate_case_id_is_error(answer):
    answer["cases"][1]["case_id"] = "A"
    assert any("겹칩니다" in m for m in errors(check_answer(answer)))


def test_decision_key_is_detected(answer):
    assert decision_keys(answer) == ["decision"]


def test_decision_value_spacing_mismatch_is_error(answer):
    answer["cases"][2]["answer"]["decision"] = "검토필요"
    messages = errors(check_answer(answer))
    assert any("'검토필요'가 decision_values에 없습니다" in m and "'검토 필요'와 표기가 다릅니다" in m for m in messages)


def test_untested_decision_value_is_warning(answer):
    answer["decision_values"].append("조건부 적격")
    assert any("조건부 적격" in m for m in warnings(check_answer(answer)))


def test_mixed_value_types_is_error(answer):
    answer["cases"][0]["answer"]["missing_documents"] = "없음"
    assert any("케이스마다 값 형식이 다릅니다" in m for m in errors(check_answer(answer)))


def test_null_list_is_warning(answer):
    answer["cases"][0]["answer"]["missing_documents"] = None
    assert any("[]로 둡니다" in m for m in warnings(check_answer(answer)))


def test_non_iso_date_is_warning(answer):
    answer["cases"][0]["answer"]["permit_no"] = "2026.11.24"
    assert any("2004-05-12 형식" in m for m in warnings(check_answer(answer)))


def test_trailing_space_is_error(answer):
    answer["cases"][0]["answer"]["decision"] = "적격 "
    assert any("앞뒤에 공백" in m for m in errors(check_answer(answer)))


def test_non_object_answer_is_reported_not_raised():
    assert errors(check_answer([1, 2])) == ["최상위가 { } 객체가 아닙니다."]
