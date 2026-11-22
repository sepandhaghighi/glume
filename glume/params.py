# -*- coding: utf-8 -*-
"""glume params."""

GLUME_VERSION = "0.2"

GLUME_REPO = "https://github.com/sepandhaghighi/glume"

OVERVIEW = """Glume is a lightweight Python tool for packing project files into a structured text representation optimized for LLM context windows.
It collects readable files from a target directory and combines their contents into a single formatted output, optionally including the directory structure tree.
Glume supports customizable Jinja2 templates, glob-based include and ignore patterns, automatic .gitignore integration, and file processing statistics.
It can be used both as a CLI tool and as an importable Python library.
"""

TARGET_DIR_TYPE_ERROR = "target_dir must be a string or pathlib.Path."
TARGET_DIR_EMPTY_ERROR = "target_dir must not be empty."
TARGET_DIR_INVALID_ERROR = "target_dir must exist and be a directory: {path}"

CUSTOM_TEMPLATE_TYPE_ERROR = "custom_template must be a non-empty string or None."

IGNORE_PATTERNS_TYPE_ERROR = "ignore_patterns must be a list of non-empty strings or None."
IGNORE_PATTERN_TYPE_ERROR = "ignore_patterns[{index}] must be a non-empty string."
INCLUDE_PATTERNS_TYPE_ERROR = "include_patterns must be a list of non-empty strings or None."
INCLUDE_PATTERN_TYPE_ERROR = "include_patterns[{index}] must be a non-empty string."

INVALID_CONFIG_TYPE_ERROR = "config must be str, pathlib.Path, or dict."
INVALID_CONFIG_FILE_ERROR = "Failed to load config file: {error}"
INVALID_CONFIG_FORMAT_ERROR = "Config file content must be a valid TOML format."

BOOLEAN_ARGUMENT_TYPE_ERROR = "{name} must be a boolean."

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
