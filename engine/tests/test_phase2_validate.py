from haval_engine.phase2.runner import pack_item_count
from haval_engine.phase2.validate import validate_instruction_following, validate_structured_output
from haval_engine.phase2.coding import grade_coding_js, weighted_coding_pct


def test_if_numbered_list():
    q = {"validation": "numberedList", "params": {"expectedCount": 3}}
    assert validate_instruction_following("1. a\n2. b\n3. c", q)
    assert not validate_instruction_following("1. a\n2. b", q)


def test_structured_json_keys():
    q = {
        "validation": "jsonKeys",
        "params": {"keys": ["name", "age"], "types": {"name": "string", "age": "number"}},
    }
    assert validate_structured_output('{"name":"Ada","age":36}', q)
    assert not validate_structured_output('{"name":"Ada","age":"36"}', q)
    assert validate_structured_output('```json\n{"name":"Ada","age":36}\n```', q)
    assert not validate_structured_output('Here you go:\n{"name":"Ada","age":36}', q)
    assert not validate_structured_output('```json\n{"name":"Ada","age":36}\n```\nand thanks', q)


def test_structured_api_response_requires_explicit_null_data():
    q = {"validation": "jsonApiResponse", "params": {"status": 200}}
    assert validate_structured_output('{"status":200,"message":"ok","data":null}', q)
    assert not validate_structured_output('{"status":200,"message":"ok"}', q)


def test_pack_has_five_categories():
    assert pack_item_count() >= 5


def test_coding_score_is_difficulty_weighted():
    easy = {"difficulty": "easy"}
    hard = {"difficulty": "hard"}
    details = [{"correct": True}, {"correct": False}]
    assert abs(weighted_coding_pct([easy, hard], details) - 25.0) < 1e-9
    assert abs(weighted_coding_pct([hard, easy], [{"correct": True}, {"correct": True}]) - 100.0) < 1e-9


def test_coding_vm_matches_hidden_tests():
    import shutil

    if not shutil.which("node"):
        return
    add = {
        "functionName": "add",
        "tests": [{"input": [1, 2], "expected": 3}],
    }
    fenced = "```javascript\nfunction add(a, b) { return a + b; }\n```"
    assert grade_coding_js(fenced, add)
    keys = {
        "functionName": "pair",
        "tests": [{"input": [], "expected": {"b": 1, "a": 2}}],
    }
    assert grade_coding_js("function pair() { return { a: 2, b: 1 }; }", keys)
    assert not grade_coding_js("function add(a, b) { return a - b; }", add)
