"""Tests for stone blocking policy"""

import tempfile
from pathlib import Path

import pytest
from maa_arknights_mcp.cli import strip_forbidden_args, check_task_file_for_stone


class TestStripForbiddenArgs:
    """Test that --stone and --stone=N are stripped from CLI args"""

    def test_stone_flag_and_value_stripped(self):
        args = ["fight", "AP-5", "-m", "1", "--stone", "1"]
        result = strip_forbidden_args(args)
        assert "--stone" not in result
        assert result == ["fight", "AP-5", "-m", "1"]

    def test_stone_equals_stripped(self):
        args = ["fight", "AP-5", "-m", "1", "--stone=1"]
        result = strip_forbidden_args(args)
        assert "--stone=1" not in result

    def test_normal_args_pass_through(self):
        args = ["fight", "AP-5", "-m", "1", "--expiring-medicine", "2"]
        result = strip_forbidden_args(args)
        assert result == args

    def test_multiple_stone_refs_stripped(self):
        args = ["fight", "AP-5", "--stone", "1", "-m", "1", "--stone", "2"]
        result = strip_forbidden_args(args)
        assert "--stone" not in result
        assert result == ["fight", "AP-5", "-m", "1"]


class TestCheckTaskFileForStone:
    """Test that task files with stone > 0 are blocked"""

    def test_task_file_with_stone_gt_zero_blocked(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write('[[tasks]]\ntype = "Fight"\nparams = { stage = "AP-5", stone = 1 }\n')
            f.flush()
            result = check_task_file_for_stone(Path(f.name))
            assert result is not None
            assert "stone" in result.lower()

    def test_task_file_with_stone_zero_passes(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write('[[tasks]]\ntype = "Fight"\nparams = { stage = "AP-5", stone = 0 }\n')
            f.flush()
            result = check_task_file_for_stone(Path(f.name))
            assert result is None

    def test_task_file_without_stone_passes(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write('[[tasks]]\ntype = "Fight"\nparams = { stage = "AP-5" }\n')
            f.flush()
            result = check_task_file_for_stone(Path(f.name))
            assert result is None

    def test_nonexistent_file_passes(self):
        result = check_task_file_for_stone(Path("/nonexistent/file.toml"))
        assert result is None
