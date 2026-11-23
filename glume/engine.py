# -*- coding: utf-8 -*-
"""glume engine."""

import os
import sys
from pathlib import Path
from typing import List, Optional, Union, Dict
from memor import Prompt, PromptTemplate, TemplateEngine
from .params import DEFAULT_TEMPLATE
from .utils import _load_gitignore_patterns, _matches_patterns, _is_binary_file, _load_config
from .utils import _build_tree_structure, _validate_inputs, _filter_ignored_directories


class Glume:
    """Pack directory files into a formatted text representation."""

    def __init__(
        self,
        target_dir: Union[str, Path] = ".",
        custom_template: Optional[str] = None,
        ignore_patterns: Optional[List[str]] = None,
        include_patterns: Optional[List[str]] = None,
        use_gitignore: bool = False,
        include_tree: bool = True,
        verbose: bool = False
    ):
        """
        Initialize the Glume packer.

        :param target_dir: Root directory containing files to pack.
        :param custom_template: Optional Jinja2 template string for rendering the output.
        :param ignore_patterns: Optional list of glob patterns for files and directories to ignore.
        :param include_patterns: Optional list of glob patterns for files and directories to include.
        :param use_gitignore: If True, loads ignore patterns from the root directory's .gitignore file.
        :param include_tree: If True, includes the directory tree in the output.
        :param verbose: If True, prints warnings when files cannot be read.
        """
        _validate_inputs(
            target_dir=target_dir,
            custom_template=custom_template,
            ignore_patterns=ignore_patterns,
            include_patterns=include_patterns,
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
        self._active_includes = list(include_patterns) if include_patterns else None

        self._included_files: List[str] = []
        self._ignored_paths: List[str] = []
        self._binary_files: List[str] = []
        self._failed_files: List[Dict[str, str]] = []

    def collect_files(self) -> List[dict]:
        """Collect readable, non-binary files from the target directory."""
        self._included_files = []
        self._ignored_paths = []
        self._binary_files = []
        self._failed_files = []

        collected_files = []
        for root, dirs, files in os.walk(self._target_dir):
            root = Path(root)
            filtered_dirs, ignored_dirs = _filter_ignored_directories(
                root,
                dirs,
                self._target_dir,
                self._active_ignores,
                self._active_includes,
            )
            self._ignored_paths.extend(ignored_dirs)
            dirs[:] = filtered_dirs
            for file in files:
                full_path = Path(root) / file
                rel_path = full_path.relative_to(self._target_dir)
                rel_path_str = str(rel_path).replace("\\", "/")

                if _matches_patterns(rel_path_str, self._active_ignores):
                    self._ignored_paths.append(rel_path_str)
                    continue

                if self._active_includes and not _matches_patterns(rel_path_str, self._active_includes):
                    self._ignored_paths.append(rel_path_str)
                    continue

                try:
                    if _is_binary_file(full_path):
                        self._binary_files.append(rel_path_str)
                        continue
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
            "ignored_count": len(self._ignored_paths),
            "binary_count": len(self._binary_files),
            "failed_count": len(self._failed_files),
            "included": self._included_files,
            "ignored": self._ignored_paths,
            "binary": self._binary_files,
            "failed": self._failed_files,
        }

    def pack(self) -> str:
        """Pack directory contents into a formatted text."""
        files = self.collect_files()
        tree_str = _build_tree_structure(
            self._target_dir,
            self._active_ignores,
            self._active_includes) if self._include_tree else ""

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
    
    def save(self, output_path: Union[str, Path]) -> Path:
        """
        Pack directory contents and save them to a file.
        
        :param output_path: Output path.
        """
        output_path = Path(output_path).resolve()
        original_ignores = self._active_ignores

        try:
            try:
                relative_output = output_path.relative_to(self._target_dir)
                self._active_ignores = list(original_ignores or [])
                if relative_output.as_posix() not in self._active_ignores:
                    self._active_ignores.append(relative_output.as_posix())
            except ValueError:
                pass

            result = self.pack()

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(result)

        finally:
            self._active_ignores = original_ignores

        return output_path

    @classmethod
    def from_config(
        cls,
        config: Optional[Union[str, Path, dict]] = None,
        target_dir: Optional[Union[str, Path]] = None,
        custom_template: Optional[str] = None,
        ignore_patterns: Optional[List[str]] = None,
        include_patterns: Optional[List[str]] = None,
        use_gitignore: Optional[bool] = None,
        include_tree: Optional[bool] = None,
        verbose: Optional[bool] = None,
        auto_discover: bool = False,
    ):
        """
        Create a Glume instance from a config file or dictionary.
        
        :param config: Glume config.
        :param target_dir: Root directory containing files to pack.
        :param custom_template: Optional Jinja2 template string for rendering the output.
        :param ignore_patterns: Optional list of glob patterns for files and directories to ignore.
        :param include_patterns: Optional list of glob patterns for files and directories to include.
        :param use_gitignore: If True, loads ignore patterns from the root directory's .gitignore file.
        :param include_tree: If True, includes the directory tree in the output.
        :param verbose: If True, prints warnings when files cannot be read.
        """
        init_directory = target_dir if target_dir is not None else "."
        loaded_config = _load_config(init_directory, config, auto_discover=auto_discover)

        resolved_ignore_patterns = list(loaded_config.get("ignore_patterns", []))
        resolved_ignore_patterns.extend(ignore_patterns or [])

        resolved_include_patterns = list(loaded_config.get("include_patterns", []))
        resolved_include_patterns.extend(include_patterns or [])

        resolved_target_dir = target_dir if target_dir is not None else loaded_config.get("target_dir", ".")
        resolved_custom_template = custom_template if custom_template is not None else loaded_config.get("custom_template")
        resolved_use_gitignore = use_gitignore if use_gitignore is not None else loaded_config.get("use_gitignore", False)
        resolved_include_tree = include_tree if include_tree is not None else loaded_config.get("include_tree", True)
        resolved_verbose = verbose if verbose is not None else loaded_config.get("verbose", False)

        return cls(
            target_dir=resolved_target_dir,
            custom_template=resolved_custom_template,
            ignore_patterns=resolved_ignore_patterns or None,
            include_patterns=resolved_include_patterns or None,
            use_gitignore=resolved_use_gitignore,
            include_tree=resolved_include_tree,
            verbose=resolved_verbose,
        )
