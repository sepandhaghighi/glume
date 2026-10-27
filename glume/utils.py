# -*- coding: utf-8 -*-
"""glume utils."""

import os
import fnmatch
from pathlib import Path
from typing import List, Optional

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
