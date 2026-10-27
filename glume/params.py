# -*- coding: utf-8 -*-
"""glume params."""

GLUME_VERSION = "0.1"


TARGET_DIR_TYPE_ERROR = "target_dir must be a string or pathlib.Path."
TARGET_DIR_EMPTY_ERROR = "target_dir must not be empty."
TARGET_DIR_INVALID_ERROR = "target_dir must exist and be a directory: {path}"

CUSTOM_TEMPLATE_TYPE_ERROR = "custom_template must be a non-empty string or None."

IGNORE_PATTERNS_TYPE_ERROR = "ignore_patterns must be a list of non-empty strings or None."
IGNORE_PATTERN_TYPE_ERROR = "ignore_patterns[{index}] must be a non-empty string."

BOOLEAN_ARGUMENT_TYPE_ERROR = "{name} must be a boolean."
