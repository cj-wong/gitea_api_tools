# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.3.0] - 2023-02-15
### Added
- Added a new script `get_user_id.py` for retrieving and optionally storing the user's ID.

### Changed
- Renamed `main.py` to `scan_python_deps.py` so that additional tools may be added in the future.
- In `scan_python_deps.py`:
    - Switched to using `argparse` over bare `sys.argv`.
- `utils.MismatchedDependency` now inherits from `ValueError` instead of `BaseException`, as it more closely matches `ValueError` in intent.

### Fixed
- In `scan_python_deps.py`:
    - Fixed crash when a dependency could not be parsed in the expected format.
    - Split only newlines when parsing dependencies, not any white-space.

## [0.2.1] - 2022-12-11
### Added
- When a dependency format mismatches, the affected repository will be printed to output.

### Fixed
- Fixed code to comply with `mypy` and `flake8`.

## [0.2.0] - 2022-10-15
### Added
- Added better version comparisons via `utils.Version`.

## [0.1.1] - 2022-07-23
### Fixed
- Fixed incorrect version regex. (Failed on e.g. `10.10.10`)
- Adjusted conditional statement in `config.py` so that `flake8` would not complain about line length.

## [0.1.0] - 2022-07-23
### Added
- Initial version
