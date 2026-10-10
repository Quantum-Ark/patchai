"""Unit tests for safe file patching and backup/rollback mechanism."""

import pytest
from pathlib import Path
from patchpilot.tools.patch import PatchTool


def test_apply_replacement_and_rollback(tmp_path: Path):
    test_file = tmp_path / "service.py"
    original_code = "def process():\n    return 'original'\n"
    test_file.write_text(original_code, encoding="utf-8")

    tool = PatchTool(tmp_path)

    # 1. Apply replacement
    success, diff, err = tool.apply_replacement(
        rel_path="service.py",
        original_snippet="return 'original'",
        patched_snippet="return 'modified'",
    )
    assert success is True
    assert "--- a/service.py" in diff
    assert "+++ b/service.py" in diff
    assert "+    return 'modified'" in diff
    assert "return 'modified'" in test_file.read_text(encoding="utf-8")

    # 2. Roll back file
    rb_success = tool.rollback("service.py")
    assert rb_success is True
    assert test_file.read_text(encoding="utf-8") == original_code


def test_rollback_all(tmp_path: Path):
    f1 = tmp_path / "mod1.py"
    f2 = tmp_path / "mod2.py"
    f1.write_text("x = 1\n", encoding="utf-8")
    f2.write_text("y = 2\n", encoding="utf-8")

    tool = PatchTool(tmp_path)
    tool.apply_replacement("mod1.py", "x = 1", "x = 100")
    tool.apply_replacement("mod2.py", "y = 2", "y = 200")

    assert "x = 100" in f1.read_text(encoding="utf-8")
    assert "y = 200" in f2.read_text(encoding="utf-8")

    tool.rollback_all()
    assert "x = 1" in f1.read_text(encoding="utf-8")
    assert "y = 2" in f2.read_text(encoding="utf-8")


def test_missing_snippet_fails_safely(tmp_path: Path):
    f = tmp_path / "file.py"
    f.write_text("content\n", encoding="utf-8")

    tool = PatchTool(tmp_path)
    success, diff, err = tool.apply_replacement("file.py", "nonexistent", "replacement")
    assert success is False
    assert "Original snippet not found" in err
