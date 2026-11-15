# -*- coding: utf-8 -*-
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
import glume.cli


def run_cli(monkeypatch, args):
    monkeypatch.setattr(sys, "argv", ["glume"] + args)
    glume.cli.main()


def test_cli_default_arguments(monkeypatch, tmp_path):
    captured = {}

    def fake_init(self, **kwargs):
        captured.update(kwargs)

    def fake_pack(self):
        return "packed output"

    with patch("glume.cli.Glume.__init__", fake_init), patch("glume.cli.Glume.pack", fake_pack):
        run_cli(monkeypatch, [str(tmp_path)])

    assert captured["target_dir"] == tmp_path.resolve()
    assert captured["custom_template"] is None
    assert captured["ignore_patterns"] is None
    assert captured["use_gitignore"] is False
    assert captured["include_tree"] is True
    assert captured["verbose"] is False


def test_cli_wizard_mode_prints_to_stderr(monkeypatch, tmp_path, capsys):
    monkeypatch.chdir(tmp_path)

    with patch("glume.cli.Glume.pack", return_value="result"):
        run_cli(monkeypatch, [])

    captured = capsys.readouterr()
    assert "[Wizard Mode] Auto-packing current directory:" in captured.err
    assert captured.out == "result"


def test_cli_writes_output_file(monkeypatch, tmp_path, capsys):
    source = tmp_path / "source"
    source.mkdir()
    output = tmp_path / "packed.txt"

    with patch("glume.cli.Glume.pack", return_value="packed content"):
        run_cli(monkeypatch, [str(source), "--output", str(output)])

    assert output.read_text(encoding="utf-8") == "packed content"
    assert "Context packed successfully" in capsys.readouterr().err


def test_cli_custom_template_and_flags(monkeypatch, tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    template = tmp_path / "template.j2"
    template.write_text("{{ files|length }}", encoding="utf-8")
    captured = {}

    def fake_init(self, **kwargs):
        captured.update(kwargs)

    with patch("glume.cli.Glume.__init__", fake_init), patch("glume.cli.Glume.pack", return_value="ok"):
        run_cli(
            monkeypatch,
            [
                str(source), "--template", str(template),
                "--no-tree", "--ignore", "*.log", "--ignore", "cache",
                "--git-ignore", "--verbose",
            ],
        )

    assert captured["custom_template"] == "{{ files|length }}"
    assert captured["include_tree"] is False
    assert captured["ignore_patterns"] == ["*.log", "cache"]
    assert captured["use_gitignore"] is True
    assert captured["verbose"] is True


def test_cli_template_read_error_exits(monkeypatch, tmp_path, capsys):
    missing_template = tmp_path / "missing.j2"

    with pytest.raises(SystemExit) as exc:
        run_cli(monkeypatch, [str(tmp_path), "--template", str(missing_template)])

    assert exc.value.code == 1
    assert "Error reading template file:" in capsys.readouterr().err


def test_cli_pack_error_exits(monkeypatch, tmp_path, capsys):
    with patch("glume.cli.Glume.pack", side_effect=RuntimeError("packing failed")):
        with pytest.raises(SystemExit) as exc:
            run_cli(monkeypatch, [str(tmp_path)])

    assert exc.value.code == 1
    assert "Error during packing: packing failed" in capsys.readouterr().err


def test_cli_reports_statistics(monkeypatch, tmp_path, capsys):
    stats = {
        "included_count": 2,
        "ignored_count": 1,
        "binary_count": 1,
        "failed_count": 1,
        "ignored": ["cache"],
        "binary": ["image.bin"],
        "failed": [{"path": "bad.txt", "error": "denied"}],
    }

    with patch("glume.cli.Glume.pack", return_value="packed"), patch(
        "glume.cli.Glume.get_stats", return_value=stats
    ):
        run_cli(monkeypatch, [str(tmp_path), "--stats"])

    captured = capsys.readouterr()
    assert captured.out == "packed"
    assert "Included Files: 2" in captured.err
    assert "Ignored Paths:  1" in captured.err
    assert "Binary Files:   1" in captured.err
    assert "Failed Files:   1" in captured.err
    assert "- cache" in captured.err
    assert "- image.bin" in captured.err
    assert "- bad.txt (denied)" in captured.err


def test_cli_stats_without_detail_lists(monkeypatch, tmp_path, capsys):
    stats = {
        "included_count": 0,
        "ignored_count": 0,
        "binary_count": 0,
        "failed_count": 0,
        "ignored": [],
        "binary": [],
        "failed": [],
    }

    with patch("glume.cli.Glume.pack", return_value="packed"), patch(
        "glume.cli.Glume.get_stats", return_value=stats
    ):
        run_cli(monkeypatch, [str(tmp_path), "--stats"])

    assert "Glume Execution Statistics" in capsys.readouterr().err


def test_cli_invalid_arguments_show_argparse_error(monkeypatch):
    with pytest.raises(SystemExit) as exc:
        run_cli(monkeypatch, ["--unknown-option"])

    assert exc.value.code == 2


def test_cli_adds_output_file_to_ignore_patterns(monkeypatch, tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    output = source / "context.txt"
    captured = {}

    def fake_init(self, **kwargs):
        captured.update(kwargs)

    with patch("glume.cli.Glume.__init__", fake_init), patch("glume.cli.Glume.pack", return_value="packed"):
        run_cli(monkeypatch, [str(source), "--output", str(output)])

    assert captured["ignore_patterns"] == ["context.txt"]


def test_cli_does_not_add_external_output_to_ignore_patterns(monkeypatch, tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    output = tmp_path / "context.txt"
    captured = {}

    def fake_init(self, **kwargs):
        captured.update(kwargs)

    with patch("glume.cli.Glume.__init__", fake_init), patch("glume.cli.Glume.pack", return_value="packed"):
        run_cli(monkeypatch, [str(source), "--output", str(output)])

    assert captured["ignore_patterns"] is None


def test_cli_optional_directory_argument(monkeypatch, tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    captured = {}

    def fake_init(self, **kwargs):
        captured.update(kwargs)

    with patch("glume.cli.Glume.__init__", fake_init), patch("glume.cli.Glume.pack", return_value="packed"):
        run_cli(monkeypatch, ["--directory", str(source)])

    assert captured["target_dir"] == source.resolve()


def test_cli_optional_directory_overrides_positional(monkeypatch, tmp_path):
    positional_source = tmp_path / "positional"
    optional_source = tmp_path / "optional"
    positional_source.mkdir()
    optional_source.mkdir()

    captured = {}

    def fake_init(self, **kwargs):
        captured.update(kwargs)

    with patch("glume.cli.Glume.__init__", fake_init), patch("glume.cli.Glume.pack", return_value="packed"):
        run_cli(
            monkeypatch,
            [
                str(positional_source),
                "--directory",
                str(optional_source),
            ],
        )

    assert captured["target_dir"] == optional_source.resolve()


def test_cli_positional_directory_still_works(monkeypatch, tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    captured = {}

    def fake_init(self, **kwargs):
        captured.update(kwargs)

    with patch("glume.cli.Glume.__init__", fake_init), patch("glume.cli.Glume.pack", return_value="packed"):
        run_cli(monkeypatch, [str(source)])

    assert captured["target_dir"] == source.resolve()
