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
    assert packer._active_includes is None


def test_initializes_with_include_patterns(tmp_path):
    packer = Glume(
        target_dir=tmp_path,
        include_patterns=["*.py", "*.md"]
    )

    assert packer._active_includes == ["*.py", "*.md"]


def test_collect_files_applies_include_patterns(tmp_path):
    (tmp_path / "main.py").write_text("python", encoding="utf-8")
    (tmp_path / "readme.md").write_text("markdown", encoding="utf-8")
    (tmp_path / "config.json").write_text("json", encoding="utf-8")

    packer = Glume(tmp_path, include_patterns=["*.py", "*.md"])
    files = packer.collect_files()

    assert {item["path"] for item in files} == {"main.py", "readme.md"}


def test_collect_files_ignore_patterns_take_precedence(tmp_path):
    (tmp_path / "main.py").write_text("main", encoding="utf-8")
    (tmp_path / "test_main.py").write_text("test", encoding="utf-8")
    (tmp_path / "readme.md").write_text("readme", encoding="utf-8")

    packer = Glume(
        tmp_path,
        include_patterns=["*.py", "*.md"],
        ignore_patterns=["test_*.py"]
    )

    files = packer.collect_files()

    assert {item["path"] for item in files} == {"main.py", "readme.md"}
    assert packer.get_stats()["ignored"] == ["test_main.py"]


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

    assert set([item["path"] for item in files]) == {"keep.txt", ".gitignore"}
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


def test_save_writes_output_file(tmp_path):
    (tmp_path / "hello.txt").write_text("hello", encoding="utf-8")
    output = tmp_path / "context.txt"

    packer = Glume(tmp_path)
    result = packer.save(output)

    assert result == output.resolve()
    assert output.exists()
    assert "hello" in output.read_text(encoding="utf-8")


def test_save_excludes_output_file_from_packed_content(tmp_path):
    (tmp_path / "hello.txt").write_text("hello", encoding="utf-8")
    output = tmp_path / "context.txt"
    output.write_text("previous output", encoding="utf-8")

    packer = Glume(tmp_path)
    packer.save(output)

    content = output.read_text(encoding="utf-8")

    assert "hello" in content
    assert "previous output" not in content
    assert "context.txt" not in content


def test_save_excludes_output_file_with_config_ignore_patterns(tmp_path):
    (tmp_path / "hello.txt").write_text("hello", encoding="utf-8")
    output = tmp_path / "context.txt"

    packer = Glume.from_config(
        config={"ignore_patterns": ["*.log"]},
        target_dir=tmp_path,
    )
    original_ignores = packer._active_ignores.copy()

    packer.save(output)

    assert packer._active_ignores == original_ignores
    assert "context.txt" not in output.read_text(encoding="utf-8")


def test_save_does_not_ignore_external_output_file(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "hello.txt").write_text("hello", encoding="utf-8")
    output = tmp_path / "context.txt"

    packer = Glume(source)
    packer.save(output)

    assert "hello" in output.read_text(encoding="utf-8")
    assert packer._active_ignores is None


def test_save_restores_ignore_patterns_when_packing_fails(tmp_path):
    packer = Glume(tmp_path, ignore_patterns=["*.log"])
    original_ignores = packer._active_ignores.copy()

    with patch.object(packer, "pack", side_effect=RuntimeError("packing failed")):
        with pytest.raises(RuntimeError, match="packing failed"):
            packer.save(tmp_path / "context.txt")

    assert packer._active_ignores == original_ignores


def test_collect_files_applies_include_patterns_to_directories(tmp_path):
    src = tmp_path / "src"
    docs = tmp_path / "docs"
    src.mkdir()
    docs.mkdir()

    (src / "main.py").write_text("python", encoding="utf-8")
    (docs / "guide.md").write_text("markdown", encoding="utf-8")

    packer = Glume(tmp_path, include_patterns=["*.py"])
    files = packer.collect_files()
    stats = packer.get_stats()

    assert [item["path"] for item in files] == ["src/main.py"]
    assert "docs" in stats["ignored"]
    assert stats["ignored_count"] == 1


def test_pack_tree_respects_include_patterns(tmp_path):
    src = tmp_path / "src"
    src.mkdir()

    (src / "main.py").write_text("python", encoding="utf-8")
    (src / "readme.md").write_text("markdown", encoding="utf-8")

    result = Glume(tmp_path, include_patterns=["*.py"]).pack()

    assert "src" in result
    assert "main.py" in result
    assert "readme.md" not in result


def test_pack_tree_excludes_directories_without_included_files(tmp_path):
    src = tmp_path / "src"
    git = tmp_path / ".git"
    docs = tmp_path / "docs"

    src.mkdir()
    git.mkdir()
    docs.mkdir()

    (src / "main.js").write_text("javascript", encoding="utf-8")
    (git / "config").write_text("git config", encoding="utf-8")
    (docs / "guide.md").write_text("markdown", encoding="utf-8")

    result = Glume(tmp_path, include_patterns=["*.js"]).pack()

    assert "src" in result
    assert "main.js" in result
    assert ".git" not in result
    assert "docs" not in result
    assert "guide.md" not in result


def test_collect_files_tracks_include_excluded_files(tmp_path):
    (tmp_path / "main.py").write_text("python", encoding="utf-8")
    (tmp_path / "readme.md").write_text("markdown", encoding="utf-8")
    (tmp_path / "config.json").write_text("json", encoding="utf-8")

    packer = Glume(tmp_path, include_patterns=["*.py"])
    packer.collect_files()
    stats = packer.get_stats()

    assert stats["included_count"] == 1
    assert stats["ignored_count"] == 2
    assert set(stats["ignored"]) == {"readme.md", "config.json"}


def test_from_config_merges_ignore_patterns(tmp_path):
    packer = Glume.from_config(
        config={
            "ignore_patterns": ["*.log", "__pycache__"],
        },
        target_dir=tmp_path,
        ignore_patterns=["*.tmp"],
    )

    assert packer._active_ignores == [
        "*.log",
        "__pycache__",
        "*.tmp",
    ]


def test_from_config_merges_include_patterns(tmp_path):
    packer = Glume.from_config(
        config={
            "include_patterns": ["*.py", "*.md"],
        },
        target_dir=tmp_path,
        include_patterns=["*.json"],
    )

    assert packer._active_includes == [
        "*.py",
        "*.md",
        "*.json",
    ]


def test_from_config_uses_config_patterns_when_no_overrides(tmp_path):
    packer = Glume.from_config(
        config={
            "ignore_patterns": ["*.log"],
            "include_patterns": ["*.py"],
        },
        target_dir=tmp_path,
    )

    assert packer._active_ignores == ["*.log"]
    assert packer._active_includes == ["*.py"]


def test_from_config_loads_glume_file(tmp_path):
    config_file = tmp_path / ".glume"
    config_file.write_text(
        'ignore_patterns = ["*.log"]\n'
        'include_patterns = ["*.py"]\n',
        encoding="utf-8",
    )

    packer = Glume.from_config(target_dir=tmp_path, auto_discover=True)

    assert packer._active_ignores == ["*.log"]
    assert packer._active_includes == ["*.py"]
