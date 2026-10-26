# -*- coding: utf-8 -*-
"""glume engine."""

import os
import sys
from pathlib import Path
from typing import List, Optional, Union, Dict
from memor import Prompt, PromptTemplate, TemplateEngine
from glume.utils import load_gitignore_patterns, should_ignore, is_binary_file, build_tree_structure

DEFAULT_TEMPLATE = """
{% if include_tree %}
<folder_structure>
{{ tree }}
</folder_structure>
{% endif %}

<source_files>
{% for file in files %}
<file path="{{ file.path }}" extension="{{ file.extension }}">
{{ file.content }}
</file>
{% endfor %}
</source_files>"""

class Glume:
    """Glume: Nano File-to-Text Packer utilizing Memor natively as engine handler."""

    def __init__(
        self,
        target_dir: Union[str, Path] = ".",
        custom_template: Optional[str] = None,
        ignore_patterns: Optional[List[str]] = None,
        use_gitignore: bool = False,
        include_tree: bool = True,
        verbose: bool = False
    ):
        self.target_dir = Path(target_dir).resolve()
        self.custom_template = custom_template or DEFAULT_TEMPLATE
        self.include_tree = include_tree
        self.verbose = verbose

        # Compile total active ignore patterns
        active_ignores = list(ignore_patterns) if ignore_patterns else []
        if use_gitignore:
            git_ignores = load_gitignore_patterns(self.target_dir)
            active_ignores.extend(git_ignores)
        
        self.active_ignores = active_ignores if active_ignores else None

        # Categorized tracking lists
        self.included_files: List[str] = []
        self.ignored_files: List[str] = []
        self.binary_files: List[str] = []
        self.failed_files: List[Dict[str, str]] = []

    def collect_files(self) -> List[dict]:
        self.included_files = []
        self.ignored_files = []
        self.binary_files = []
        self.failed_files = []

        collected_files = []
        for root, _, files in os.walk(self.target_dir):
            for file in files:
                full_path = Path(root) / file
                rel_path = full_path.relative_to(self.target_dir)
                rel_path_str = str(rel_path).replace("\\", "/")

                if should_ignore(rel_path_str, self.active_ignores):
                    self.ignored_files.append(rel_path_str)
                    continue

                if is_binary_file(full_path):
                    self.binary_files.append(rel_path_str)
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
                    self.included_files.append(rel_path_str)
                except Exception as e:
                    self.failed_files.append({"path": rel_path_str, "error": str(e)})
                    if self.verbose:
                        print(f"Warning: Failed to read {rel_path_str}: {e}", file=sys.stderr)

        return collected_files

    def get_stats(self) -> dict:
        """Returns detailed statistics about processed files."""
        return {
            "included_count": len(self.included_files),
            "ignored_count": len(self.ignored_files),
            "binary_count": len(self.binary_files),
            "failed_count": len(self.failed_files),
            "included": self.included_files,
            "ignored": self.ignored_files,
            "binary": self.binary_files,
            "failed": self.failed_files,
        }

    def pack(self) -> str:
        """Packs the directory context and returns the rendered string via Memor."""
        files = self.collect_files()
        tree_str = build_tree_structure(self.target_dir, self.active_ignores) if self.include_tree else ""

        prompt_template = PromptTemplate(
            engine=TemplateEngine.JINJA,
            content=self.custom_template,
            custom_map={
                "files": files,
                "tree": tree_str,
                "include_tree": self.include_tree
            }
        )

        prompt = Prompt(template=prompt_template)
        return prompt.render()
