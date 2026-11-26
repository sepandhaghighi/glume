# -*- coding: utf-8 -*-
import pytest

from glume import GlumeError, GlumeValidationError
from glume import Glume


def test_error_inheritance():
    error = GlumeValidationError("invalid input")

    assert isinstance(error, GlumeError)
    assert isinstance(error, ValueError)
    assert str(error) == "invalid input"


def test_base_error_can_be_raised():
    with pytest.raises(GlumeError, match="packing failed"):
        raise GlumeError("packing failed")


def test_validation_error_for_invalid_target_type(tmp_path):
    with pytest.raises(GlumeValidationError, match="target_dir must be a string or pathlib.Path"):
        Glume(target_dir=123)


def test_validation_error_for_empty_target(tmp_path):
    with pytest.raises(GlumeValidationError, match="target_dir must not be empty"):
        Glume(target_dir="  ")


def test_validation_error_for_missing_target():
    with pytest.raises(GlumeValidationError, match="target_dir must exist and be a directory"):
        Glume(target_dir="__missing_glume_directory__")


def test_validation_error_when_target_is_file(tmp_path):
    file_path = tmp_path / "file.txt"
    file_path.write_text("content", encoding="utf-8")

    with pytest.raises(GlumeValidationError, match="target_dir must exist and be a directory"):
        Glume(target_dir=file_path)


@pytest.mark.parametrize("template", [123, "", "   "])
def test_validation_error_for_invalid_custom_template(tmp_path, template):
    with pytest.raises(GlumeValidationError, match="custom_template must be a non-empty string or None"):
        Glume(target_dir=tmp_path, custom_template=template)


@pytest.mark.parametrize("patterns", ["*.py", (), 123])
def test_validation_error_for_invalid_ignore_patterns_type(tmp_path, patterns):
    with pytest.raises(GlumeValidationError, match="ignore_patterns must be a list of non-empty strings or None"):
        Glume(target_dir=tmp_path, ignore_patterns=patterns)


@pytest.mark.parametrize("pattern", [123, "", "   ", None])
def test_validation_error_for_invalid_ignore_pattern(tmp_path, pattern):
    with pytest.raises(GlumeValidationError, match=r"ignore_patterns\[0\] must be a non-empty string."):
        Glume(target_dir=tmp_path, ignore_patterns=[pattern])


@pytest.mark.parametrize("patterns", ["*.py", (), 123])
def test_validation_error_for_invalid_include_patterns_type(tmp_path, patterns):
    with pytest.raises(GlumeValidationError, match="include_patterns must be a list of non-empty strings or None"):
        Glume(target_dir=tmp_path, include_patterns=patterns)


@pytest.mark.parametrize("pattern", [123, "", "   ", None])
def test_validation_error_for_invalid_include_pattern(tmp_path, pattern):
    with pytest.raises(GlumeValidationError, match=r"include_patterns\[0\] must be a non-empty string."):
        Glume(target_dir=tmp_path, include_patterns=[pattern])


@pytest.mark.parametrize("argument", ["use_gitignore", "include_tree", "verbose"])
def test_validation_error_for_non_boolean_flags(tmp_path, argument):
    values = {"use_gitignore": False, "include_tree": True, "verbose": False}
    values[argument] = "yes"

    with pytest.raises(GlumeValidationError, match=f"{argument} must be a boolean"):
        Glume(target_dir=tmp_path, **values)


def test_validation_error_for_set_target_dir(tmp_path):
    packer = Glume(target_dir=tmp_path)

    with pytest.raises(GlumeValidationError, match="target_dir must be a string or pathlib.Path."):
        packer.set_target_dir(123)


@pytest.mark.parametrize("template", [123, "", "   "])
def test_validation_error_for_set_custom_template(tmp_path, template):
    packer = Glume(target_dir=tmp_path)

    with pytest.raises(GlumeValidationError, match="custom_template must be a non-empty string or None"):
        packer.set_custom_template(template)


@pytest.mark.parametrize("patterns", ["*.py", (), 123])
def test_validation_error_for_set_ignore_patterns(tmp_path, patterns):
    packer = Glume(target_dir=tmp_path)

    with pytest.raises(GlumeValidationError, match="ignore_patterns must be a list of non-empty strings or None"):
        packer.set_ignore_patterns(patterns)


@pytest.mark.parametrize("pattern", [123, "", "   ", None])
def test_validation_error_for_add_ignore_pattern(tmp_path, pattern):
    packer = Glume(target_dir=tmp_path)

    with pytest.raises(GlumeValidationError, match=r"ignore_patterns\[1\] must be a non-empty string."):
        packer.add_ignore_pattern(pattern)


@pytest.mark.parametrize("pattern", [123, "", "   ", None])
def test_validation_error_for_remove_ignore_pattern(tmp_path, pattern):
    packer = Glume(target_dir=tmp_path)

    with pytest.raises(GlumeValidationError, match=r"ignore_patterns\[0\] must be a non-empty string."):
        packer.remove_ignore_pattern(pattern)


@pytest.mark.parametrize("patterns", ["*.py", (), 123])
def test_validation_error_for_set_include_patterns(tmp_path, patterns):
    packer = Glume(target_dir=tmp_path)

    with pytest.raises(GlumeValidationError, match="include_patterns must be a list of non-empty strings or None"):
        packer.set_include_patterns(patterns)


@pytest.mark.parametrize("pattern", [123, "", "   ", None])
def test_validation_error_for_add_include_pattern(tmp_path, pattern):
    packer = Glume(target_dir=tmp_path)

    with pytest.raises(GlumeValidationError, match=r"include_patterns\[0\] must be a non-empty string."):
        packer.add_include_pattern(pattern)


@pytest.mark.parametrize("pattern", [123, "", "   ", None])
def test_validation_error_for_remove_include_pattern(tmp_path, pattern):
    packer = Glume(target_dir=tmp_path)

    with pytest.raises(GlumeValidationError, match=r"include_patterns\[0\] must be a non-empty string."):
        packer.remove_include_pattern(pattern)


@pytest.mark.parametrize("value", [1, "true", None])
def test_validation_error_for_set_include_tree(tmp_path, value):
    packer = Glume(target_dir=tmp_path)

    with pytest.raises(GlumeValidationError, match="include_tree must be a boolean"):
        packer.set_include_tree(value)


@pytest.mark.parametrize("value", [1, "true", None])
def test_validation_error_for_set_verbose(tmp_path, value):
    packer = Glume(target_dir=tmp_path)

    with pytest.raises(GlumeValidationError, match="verbose must be a boolean"):
        packer.set_verbose(value)
