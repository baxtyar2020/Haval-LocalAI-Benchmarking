from haval_engine.paths import locate_node, locate_python


def test_python_locator_finds_this_interpreter():
    found = locate_python()
    assert found is not None
    assert found.is_file() or found.name.lower() in {"python", "python.exe", "py"}


def test_node_locator_is_optional_but_stable():
    found = locate_node()
    if found is None:
        return
    assert "node" in found.name.lower() or found.name.lower() == "node.exe"
