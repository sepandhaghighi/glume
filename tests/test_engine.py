# -*- coding: utf-8 -*-
from pathlib import Path
from unittest.mock import mock_open, patch
import pytest
from glume import Glume


def test_initializes_with_defaults(tmp_path):
    packer = Glume(target_dir=tmp_path)

    assert packer._target_dir == tmp_path.resolve()
    assert packer._include_tree is True
    assert packer._verbose is False
    assert packer._active_ignores is None


def test_initializes_with_custom_options(tmp_path):
    packer = Glume(
        target_dir=str(tmp_path),
        custom_template="CUSTOM",
        ignore_patterns=["*.log"],
        include_tree=False,
        verbose=True,
    )

    assert packer._custom_template == "CUSTOM"
    assert packer._active_ignores == ["*.log"]
    assert packer._include_tree is False
    assert packer._verbose is True


def test_collect_files_reads_nested_text_files(tmp_path):
    (tmp_path / "hello.py").write_text("print('hello')", encoding="utf-8")
    nested = tmp_path / "src"
    nested.mkdir()
    (nested / "module").write_text("module content", encoding="utf-8")

    files = Glume(tmp_path).collect_files()

    assert {"path": "hello.py", "extension": "py", "content": "print('hello')"} in files
    assert {"path": "src/module", "extension": "text", "content": "module content"} in files


def test_collect_files_skips_binary_and_tracks_statistics(tmp_path):
    (tmp_path / "readme.txt").write_text("read me", encoding="utf-8")
    (tmp_path / "image.bin").write_bytes(b"header\x00binary")

    packer = Glume(tmp_path)
    files = packer.collect_files()
    stats = packer.get_stats()

    assert [item["path"] for item in files] == ["readme.txt"]
    assert stats["included_count"] == 1
    assert stats["binary_count"] == 1
    assert stats["included"] == ["readme.txt"]
    assert stats["binary"] == ["image.bin"]


def test_collect_files_applies_file_and_directory_ignore_patterns(tmp_path):
    (tmp_path / "keep.txt").write_text("keep", encoding="utf-8")
    (tmp_path / "skip.log").write_text("skip", encoding="utf-8")
    ignored_dir = tmp_path / "cache"
    ignored_dir.mkdir()
    (ignored_dir / "data.txt").write_text("hidden", encoding="utf-8")

    packer = Glume(tmp_path, ignore_patterns=["*.log", "cache"])
    files = packer.collect_files()
    stats = packer.get_stats()

    assert [item["path"] for item in files] == ["keep.txt"]
    assert set(stats["ignored"]) == {"skip.log", "cache"}
    assert stats["ignored_count"] == 2


def test_gitignore_patterns_are_loaded_and_applied(tmp_path):
    (tmp_path / ".gitignore").write_text("# comment\n\n*.tmp\n/build/\n", encoding="utf-8")
    (tmp_path / "keep.txt").write_text("keep", encoding="utf-8")
    (tmp_path / "drop.tmp").write_text("drop", encoding="utf-8")
    build = tmp_path / "build"
    build.mkdir()
    (build / "artifact.txt").write_text("artifact", encoding="utf-8")

    packer = Glume(tmp_path, use_gitignore=True)
    files = packer.collect_files()

    assert [item["path"] for item in files] == ["keep.txt", ".gitignore"]
    assert set(packer.get_stats()["ignored"]) == {"drop.tmp", "build"}


def test_collect_files_records_read_errors_and_verbose_warning(tmp_path, capsys):
    file_path = tmp_path / "unreadable.txt"
    file_path.write_text("content", encoding="utf-8")
    packer = Glume(tmp_path, verbose=True)

    with patch("builtins.open", side_effect=PermissionError("permission denied")):
        files = packer.collect_files()

    assert files == []
    assert packer.get_stats()["failed_count"] == 1
    assert packer.get_stats()["failed"][0]["path"] == "unreadable.txt"
    assert "Warning: Failed to read unreadable.txt" in capsys.readouterr().err


def test_collect_files_silences_read_errors_when_not_verbose(tmp_path, capsys):
    (tmp_path / "unreadable.txt").write_text("content", encoding="utf-8")

    with patch("builtins.open", side_effect=PermissionError("permission denied")):
        files = Glume(tmp_path).collect_files()

    assert files == []
    assert capsys.readouterr().err == ""


def test_collect_files_resets_previous_statistics(tmp_path):
    (tmp_path / "first.txt").write_text("first", encoding="utf-8")
    packer = Glume(tmp_path)
    packer.collect_files()

    (tmp_path / "second.txt").write_text("second", encoding="utf-8")
    packer.collect_files()

    assert set(packer.get_stats()["included"]) == {"first.txt", "second.txt"}


def test_pack_uses_default_template_and_includes_tree(tmp_path):
    (tmp_path / "hello.py").write_text("print('hello')", encoding="utf-8")

    result = Glume(tmp_path).pack()

    assert "<folder_structure>" in result
    assert f"{tmp_path.name}/" in result
    assert '<file path="hello.py" extension="py">' in result
    assert "print('hello')" in result


def test_pack_can_disable_tree(tmp_path):
    (tmp_path / "hello.txt").write_text("hello", encoding="utf-8")

    result = Glume(tmp_path, include_tree=False).pack()

    assert "<folder_structure>" not in result
    assert '<file path="hello.txt" extension="txt">' in result
    assert "hello" in result


def test_pack_renders_custom_template(tmp_path):
    (tmp_path / "a.txt").write_text("alpha", encoding="utf-8")
    template = "{{ files|length }}:{{ files[0].path }}={{ files[0].content }}"

    result = Glume(tmp_path, custom_template=template).pack()

    assert result == "1:a.txt=alpha"


def test_pack_passes_empty_files_to_template(tmp_path):
    result = Glume(tmp_path, custom_template="count={{ files|length }}").pack()

    assert result == "count=0"
