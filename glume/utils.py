# -*- coding: utf-8 -*-
"""glume utils."""

import os
import fnmatch
from pathlib import Path
from typing import List, Optional, Any, Union
import tomli
from .errors import GlumeValidationError
from .params import (
    TARGET_DIR_TYPE_ERROR,
    TARGET_DIR_EMPTY_ERROR,
    TARGET_DIR_INVALID_ERROR,
    CUSTOM_TEMPLATE_TYPE_ERROR,
    IGNORE_PATTERNS_TYPE_ERROR,
    INCLUDE_PATTERNS_TYPE_ERROR,
    BOOLEAN_ARGUMENT_TYPE_ERROR,
    NON_EMPTY_STRING_ARGUMENT_TYPE_ERROR,
    INVALID_CONFIG_TYPE_ERROR,
    INVALID_CONFIG_FILE_ERROR,
    INVALID_CONFIG_FORMAT_ERROR,
    DEFAULT_AUTO_DISCOVER,
)


def _load_config(
    directory: Union[str, Path],
    config_source: Optional[Union[str, Path, dict]] = None,
    auto_discover: bool = DEFAULT_AUTO_DISCOVER,
) -> dict:
    """Load config."""
    if config_source is None:
        if not auto_discover:
            return {}

        dir_path = Path(directory)
        candidate = dir_path / ".glume"

        if candidate.is_file():
            config_path = candidate
        else:
            return {}
    elif isinstance(config_source, dict):
        return config_source
    elif isinstance(config_source, (str, Path)):
        config_path = Path(config_source)
    else:
        raise GlumeValidationError(INVALID_CONFIG_TYPE_ERROR)

    if not config_path.exists():
        return {}

    try:
        with open(config_path, "rb") as f:
            data = tomli.load(f)

        if not isinstance(data, dict):
            raise GlumeValidationError(INVALID_CONFIG_FORMAT_ERROR)

        return data
    except Exception as e:
        if isinstance(e, GlumeValidationError):
            raise e
        raise GlumeValidationError(INVALID_CONFIG_FILE_ERROR.format(error=e))


def _validate_non_empty_string(value: Any, name: str) -> None:
    """
    Validate non-empty string.

    :param value: value
    :param name: parameter name
    """
    if not isinstance(value, str) or not value.strip():
        raise GlumeValidationError(NON_EMPTY_STRING_ARGUMENT_TYPE_ERROR.format(name=name))


def _validate_target_dir(target_dir: Any) -> None:
    """
    Validate the target directory.
    
    :param target_dir: Root directory containing files to pack.
    """
    if not isinstance(target_dir, (str, Path)):
        raise GlumeValidationError(TARGET_DIR_TYPE_ERROR)

    if isinstance(target_dir, str) and not target_dir.strip():
        raise GlumeValidationError(TARGET_DIR_EMPTY_ERROR)

    target_path = Path(target_dir).resolve()

    if not target_path.is_dir():
        raise GlumeValidationError(TARGET_DIR_INVALID_ERROR.format(path=target_path))


def _validate_custom_template(custom_template: Any) -> None:
    """
    Validate the custom template.
    
    :param custom_template: Optional Jinja2 template string for rendering the output.
    """
    if custom_template is not None:
        if not isinstance(custom_template, str) or not custom_template.strip():
            raise GlumeValidationError(CUSTOM_TEMPLATE_TYPE_ERROR)


def _validate_ignore_patterns(ignore_patterns: Any) -> None:
    """
    Validate the ignore patterns.
    
    :param ignore_patterns: Optional list of glob patterns for files and directories to ignore.
    """
    if ignore_patterns is not None:
        if not isinstance(ignore_patterns, list):
            raise GlumeValidationError(IGNORE_PATTERNS_TYPE_ERROR)

        for index, pattern in enumerate(ignore_patterns):
            _validate_non_empty_string(pattern, "ignore_patterns[{index}]".format(index=index))


def _validate_include_patterns(include_patterns: Any) -> None:
    """
    Validate the include patterns.
    
    :param include_patterns: Optional list of glob patterns for files and directories to include.
    """
    if include_patterns is not None:
        if not isinstance(include_patterns, list):
            raise GlumeValidationError(INCLUDE_PATTERNS_TYPE_ERROR)

        for index, pattern in enumerate(include_patterns):
            _validate_non_empty_string(pattern, "include_patterns[{index}]".format(index=index))


def _validate_use_gitignore(use_gitignore: Any) -> None:
    """
    Validate the use_gitignore argument.
    
    :param use_gitignore: If True, loads ignore patterns from the root directory's .gitignore file.
    """
    if not isinstance(use_gitignore, bool):
        raise GlumeValidationError(BOOLEAN_ARGUMENT_TYPE_ERROR.format(name="use_gitignore"))


def _validate_include_tree(include_tree: Any) -> None:
    """
    Validate the include_tree argument.
    
    :param include_tree: If True, includes the directory tree in the output.
    """
    if not isinstance(include_tree, bool):
        raise GlumeValidationError(BOOLEAN_ARGUMENT_TYPE_ERROR.format(name="include_tree"))


def _validate_verbose(verbose: Any) -> None:
    """
    Validate the verbose argument.
    
    :param verbose: If True, prints warnings when files cannot be read.
    """
    if not isinstance(verbose, bool):
        raise GlumeValidationError(BOOLEAN_ARGUMENT_TYPE_ERROR.format(name="verbose"))


def _load_gitignore_patterns(root_path: Path) -> List[str]:
    """
    Load ignore patterns from the root directory's .gitignore file.

    :param root_path: Root directory containing the .gitignore file.
    """
    patterns = []
    gitignore_file = root_path / ".gitignore"
    if gitignore_file.is_file():
        try:
            with open(gitignore_file, "r", encoding="utf-8") as f:
                for line in f:
                    cleaned = line.strip()
                    if cleaned and not cleaned.startswith("#"):
                        patterns.append(cleaned.lstrip("/"))
        except Exception:
            pass
    return patterns


def _matches_patterns(rel_path_str: str, patterns: Optional[List[str]]) -> bool:
    """
    Determine whether a relative path matches any glob pattern.

    :param rel_path_str: File or directory path relative to the target directory.
    :param patterns: Optional list of glob patterns.
    """
    if not patterns:
        return False

    path_obj = Path(rel_path_str)
    for pattern in patterns:
        if fnmatch.fnmatch(rel_path_str, pattern) or fnmatch.fnmatch(path_obj.name, pattern):
            return True
        if any(fnmatch.fnmatch(part, pattern.rstrip("/")) for part in path_obj.parts):
            return True
    return False


def _filter_ignored_directories(
    root: Path,
    directories: List[str],
    target_dir: Path,
    ignore_patterns: Optional[List[str]],
    include_patterns: Optional[List[str]],
) -> tuple:
    """
    Filter ignored directories and return their names.

    :param root: Current directory being traversed.
    :param directories: List of directory names to filter.
    :param target_dir: Root directory containing files to pack.
    :param ignore_patterns: Optional list of glob patterns for files and directories to ignore.
    :param include_patterns: Optional list of glob patterns for files and directories to include.
    """
    ignored = []
    filtered = []

    for directory in directories:
        dir_path = root / directory
        rel_path = dir_path.relative_to(target_dir).as_posix()

        if _matches_patterns(rel_path, ignore_patterns):
            ignored.append(rel_path)
            continue

        if include_patterns:
            has_included_files = any(
                _matches_patterns(
                    (Path(current_root) / file).relative_to(target_dir).as_posix(),
                    include_patterns
                )
                for current_root, _, files in os.walk(dir_path)
                for file in files
            )

            if not has_included_files:
                ignored.append(rel_path)
                continue

        filtered.append(directory)

    return filtered, ignored


def _is_binary_file(file_path: Path) -> bool:
    """
    Determine whether a file contains binary data.

    :param file_path: Path to the file being checked.
    """
    try:
        with open(file_path, "rb") as check_file:
            chunk = check_file.read(1024)
            return b"\0" in chunk
    except OSError:
        return False


def _build_tree_structure(root_path: Path,
                          ignore_patterns: Optional[List[str]],
                          include_patterns: Optional[List[str]]) -> str:
    """
    Build a formatted directory tree while excluding ignored paths.

    :param root_path: Root directory from which to build the tree.
    :param ignore_patterns: Optional list of glob patterns for files and directories to ignore.
    :param include_patterns: Optional list of glob patterns for files and directories to include.
    """
    tree_lines = [f"{root_path.name}/"]

    def _build(dir_path: Path, prefix: str = ""):
        """
        Recursively append directory entries to the tree representation.

        :param dir_path: Directory whose entries should be processed.
        :param prefix: Prefix used to align entries in the directory tree.
        """
        try:
            entries = sorted(dir_path.iterdir(), key=lambda e: (not e.is_dir(), e.name.lower()))
        except PermissionError:
            return

        valid_entries = []
        for entry in entries:
            rel_path = entry.relative_to(root_path)
            rel_path_str = str(rel_path).replace("\\", "/") + ("/" if entry.is_dir() else "")
            if _matches_patterns(rel_path_str.rstrip("/"), ignore_patterns):
                continue

            if include_patterns:
                if entry.is_file() and not _matches_patterns(rel_path_str.rstrip("/"), include_patterns):
                    continue

                if entry.is_dir():
                    has_included_files = any(
                        _matches_patterns(
                            (Path(current_root) / file).relative_to(root_path).as_posix(),
                            include_patterns
                        )
                        for current_root, _, files in os.walk(entry)
                        for file in files
                    )

                    if not has_included_files:
                        continue

            valid_entries.append(entry)

        count = len(valid_entries)
        for i, entry in enumerate(valid_entries):
            is_last = (i == count - 1)
            connector = "└── " if is_last else "├── "
            tree_lines.append(f"{prefix}{connector}{entry.name}")

            if entry.is_dir():
                extension = "    " if is_last else "│   "
                _build(entry, prefix + extension)

    _build(root_path)
    return "\n".join(tree_lines)
