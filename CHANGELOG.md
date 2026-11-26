# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- `--config` CLI argument
- `--stdout` CLI argument
- `save` method
- `from_config` method
- `target_dir` property
- `custom_template` property
- `ignore_patterns` property
- `include_patterns` property
- `include_tree` property
- `verbose` property
- `set_target_dir` method
- `set_custom_template` method
- `set_ignore_patterns` method
- `add_ignore_pattern` method
- `remove_ignore_pattern` method
- `set_include_patterns` method
- `add_include_pattern` method
- `remove_include_pattern` method
- `set_include_tree` method
- `set_verbose` method
### Changed
- Test system modified
- Validation system modified
- Default values moved to `params.py`
## [0.2] - 2026-11-22
### Added
- `--directory` CLI argument
- `--version` CLI argument
- `--info` CLI argument
- `--include` CLI argument
- `include_patterns` parameter
### Changed
- `README.md` updated
- Test system modified
- Output mirroring bug fixed
- Wizard mode bug fixed
## [0.1] - 2026-11-10
### Added
- `Glume` class
- `GlumeError` class
- `GlumeValidationError` class
- Command line interface
- Test system

[Unreleased]: https://github.com/sepandhaghighi/glume/compare/v0.2...dev
[0.2]: https://github.com/sepandhaghighi/glume/compare/v0.1...v0.2
[0.1]: https://github.com/sepandhaghighi/glume/compare/56232c8...v0.1
