# -*- coding: utf-8 -*-
"""glume engine."""

import os
import sys
from pathlib import Path
from typing import List, Optional, Union, Dict
from memor import Prompt, PromptTemplate, TemplateEngine
from .params import DEFAULT_TEMPLATE
from .utils import _load_gitignore_patterns, _should_ignore, _is_binary_file, _build_tree_structure, _validate_inputs



class Glume:
    """Pack directory files into a formatted text representation."""

    def __init__(
        self,
        target_dir: Union[str, Path] = ".",
        custom_template: Optional[str] = None,
        ignore_patterns: Optional[List[str]] = None,
        use_gitignore: bool = False,
        include_tree: bool = True,
        verbose: bool = False
    ):
        """
        Initialize the Glume packer.

        :param target_dir: Root directory containing files to pack.
        :param custom_template: Optional Jinja2 template string for rendering the output.
        :param ignore_patterns: Optional list of glob patterns for files and directories to ignore.
        :param use_gitignore: If True, loads ignore patterns from the root directory's .gitignore file.
        :param include_tree: If True, includes the directory tree in the output.
        :param verbose: If True, prints warnings when files cannot be read.
        """
        _validate_inputs(
            target_dir=target_dir,
            custom_template=custom_template,
            ignore_patterns=ignore_patterns,
            use_gitignore=use_gitignore,
            include_tree=include_tree,
            verbose=verbose,
        )

        self._target_dir = Path(target_dir).resolve()
        self._custom_template = custom_template or DEFAULT_TEMPLATE
        self._include_tree = include_tree
        self._verbose = verbose

        active_ignores = list(ignore_patterns) if ignore_patterns else []

        if use_gitignore:
            git_ignores = _load_gitignore_patterns(self._target_dir)
            active_ignores.extend(git_ignores)

        self._active_ignores = active_ignores if active_ignores else None

        self._included_files: List[str] = []
        self._ignored_files: List[str] = []
        self._binary_files: List[str] = []
        self._failed_files: List[Dict[str, str]] = []

    def collect_files(self) -> List[dict]:
        """Collect readable, non-binary files from the target directory."""
        self._included_files = []
        self._ignored_files = []
        self._binary_files = []
        self._failed_files = []

        collected_files = []
        for root, _, files in os.walk(self._target_dir):
            for file in files:
                full_path = Path(root) / file
                rel_path = full_path.relative_to(self._target_dir)
                rel_path_str = str(rel_path).replace("\\", "/")

                if _should_ignore(rel_path_str, self._active_ignores):
                    self._ignored_files.append(rel_path_str)
                    continue

                if _is_binary_file(full_path):
                    self._binary_files.append(rel_path_str)
                    continue

                try:
                    with open(full_path, "r", encoding="utf-8", errors="replace") as f:
                        content = f.read()

                    ext = full_path.suffix.lstrip(".") or "text"
                    collected_files.append({
                        "path": rel_path_str,
                        "extension": ext,
                        "content": content
                    })
                    self._included_files.append(rel_path_str)
                except Exception as e:
                    self._failed_files.append({"path": rel_path_str, "error": str(e)})
                    if self._verbose:
                        print(f"Warning: Failed to read {rel_path_str}: {e}", file=sys.stderr)

        return collected_files

    def get_stats(self) -> dict:
        """Retrieve statistics about processed files."""
        return {
            "included_count": len(self._included_files),
            "ignored_count": len(self._ignored_files),
            "binary_count": len(self._binary_files),
            "failed_count": len(self._failed_files),
            "included": self._included_files,
            "ignored": self._ignored_files,
            "binary": self._binary_files,
            "failed": self._failed_files,
        }

    def pack(self) -> str:
        """Pack directory contents into a formatted text."""
        files = self.collect_files()
        tree_str = _build_tree_structure(self._target_dir, self._active_ignores) if self._include_tree else ""

        prompt_template = PromptTemplate(
            engine=TemplateEngine.JINJA,
            content=self._custom_template,
            custom_map={
                "files": files,
                "tree": tree_str,
                "include_tree": self._include_tree
            }
        )

        prompt = Prompt(template=prompt_template)
        return prompt.render()
