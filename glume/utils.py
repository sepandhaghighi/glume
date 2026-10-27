# -*- coding: utf-8 -*-
"""glume utils."""

import os
import fnmatch
from pathlib import Path
from typing import List, Optional
from .error import GlumeValidationError
from .params import (
    TARGET_DIR_TYPE_ERROR,
    TARGET_DIR_EMPTY_ERROR,
    TARGET_DIR_INVALID_ERROR,
    CUSTOM_TEMPLATE_TYPE_ERROR,
    IGNORE_PATTERNS_TYPE_ERROR,
    IGNORE_PATTERN_TYPE_ERROR,
    BOOLEAN_ARGUMENT_TYPE_ERROR,
)


def _validate_inputs(
    target_dir,
    custom_template,
    ignore_patterns,
    use_gitignore,
    include_tree,
    verbose,
) -> None:
    """Validate all inputs."""

    if not isinstance(target_dir, (str, Path)):
        raise GlumeValidationError(TARGET_DIR_TYPE_ERROR)

    if isinstance(target_dir, str) and not target_dir.strip():
        raise GlumeValidationError(TARGET_DIR_EMPTY_ERROR)

    target_path = Path(target_dir).resolve()

    if not target_path.is_dir():
        raise GlumeValidationError(TARGET_DIR_INVALID_ERROR.format(path=target_path))

    if custom_template is not None:
        if not isinstance(custom_template, str) or not custom_template.strip():
            raise GlumeValidationError(CUSTOM_TEMPLATE_TYPE_ERROR)

    if ignore_patterns is not None:
        if not isinstance(ignore_patterns, list):
            raise GlumeValidationError(IGNORE_PATTERNS_TYPE_ERROR)

        for index, pattern in enumerate(ignore_patterns):
            if not isinstance(pattern, str) or not pattern.strip():
                raise GlumeValidationError(IGNORE_PATTERN_TYPE_ERROR.format(index=index))

    boolean_arguments = {
        "use_gitignore": use_gitignore,
        "include_tree": include_tree,
        "verbose": verbose,
    }

    for name, value in boolean_arguments.items():
        if not isinstance(value, bool):
            raise GlumeValidationError(BOOLEAN_ARGUMENT_TYPE_ERROR.format(name=name))


def load_gitignore_patterns(root_path: Path) -> List[str]:
    """Reads and parses .gitignore patterns using standard library."""
    patterns = []
    gitignore_file = root_path / ".gitignore"
    if gitignore_file.is_file():
        try:
            with open(gitignore_file, "r", encoding="utf-8") as f:
                for line in f:
                    cleaned = line.strip()
                    if cleaned and not cleaned.startswith("#"):
                        # Normalize leading/trailing slashes for glob matching
                        patterns.append(cleaned.lstrip("/"))
        except Exception:
            pass
    return patterns


def should_ignore(rel_path_str: str, ignore_patterns: Optional[List[str]]) -> bool:
    """Checks if a relative path matches any ignore patterns."""
    if not ignore_patterns:
        return False
    
    path_obj = Path(rel_path_str)
    for pattern in ignore_patterns:
        # Match against full relative path, file name, or directory components
        if fnmatch.fnmatch(rel_path_str, pattern) or fnmatch.fnmatch(path_obj.name, pattern):
            return True
        if any(fnmatch.fnmatch(part, pattern.rstrip("/")) for part in path_obj.parts):
            return True
    return False


def is_binary_file(file_path: Path) -> bool:
    try:
        with open(file_path, "tr", encoding="utf-8") as check_file:
            check_file.read(1024)
            return False
    except UnicodeDecodeError:
        return True


def build_tree_structure(root_path: Path, ignore_patterns: Optional[List[str]]) -> str:
    tree_lines = [f"{root_path.name}/"]

    def _build(dir_path: Path, prefix: str = ""):
        try:
            entries = sorted(list(dir_path.iterdir()), key=lambda e: (not e.is_dir(), e.name.lower()))
        except PermissionError:
            return

        valid_entries = []
        for entry in entries:
            rel_path = entry.relative_to(root_path)
            rel_path_str = str(rel_path).replace("\\", "/") + ("/" if entry.is_dir() else "")
            if not should_ignore(rel_path_str.rstrip("/"), ignore_patterns):
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
