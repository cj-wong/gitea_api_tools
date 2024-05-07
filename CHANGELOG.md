# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.2.1] - 2024-05-07
### Changed
- `tests`: Use `self.subTest()` whenever possible, to clearly mark separate tests.
- Replaced `flake8` and `black` with `ruff`. `ruff check` is also automatically run with `hooks`.
- Types are now declared in `PascalCase`, with explicit hinting of `typing.TypeAlias`.

### Fixed
- Fixed aliases not calling their respective functions. This was because when using `dest` with a set of sub-parsers, `dest` could be filled by both the exact sub-parser or its aliases. I tried to match against the sub-parser name only. For more details, check out commit 74e494af2266b7315005270b102ae07bbcc11cb9.

### Security
- Bumped dependencies, primarily `idna` to `3.7`.

## [1.2.0] - 2024-03-06
### Changed
- Python code is now formatted with `black`.
- Users can now execute the module with `python3 -m gitea_api_tools` as an alternative to the `poetry` setup.
- Combined `gitea_api_tools/language/` with `package.py`, since `language` has only worked with packages.
- Instead of using a dummy argument, the main command now uses `dest=` in the sub-parser for identifying the executed sub-command.

### Fixed
- `types-request` was added as a dependency, but it is actually only a dev dependency.

### Deprecated
- All the individual scripts are now deprecated. Their functionality has been pulled out to (sub)modules within `gitea_api_tools/gitea/` and `gitea_api_tools/package`. Although the scripts have been updated to work with the new modules, no more work will be done on these scripts, and they will be removed on the next major update.

## [1.1.0] - 2024-02-18
### Added
- Added new sub-command `gitea-api configure`. This command allows users to interactively configure settings.
- Added a new document for `gitea-api` under [docs](./docs).

### Changed
- The `config.py` module is now a full-fledged library/module.
    - Individual parts have been split into new scripts (`logging`, `paths`). This split has allowed me to create the aforementioned sub-command `configure`.

### Security
- Bumped dependencies, including `urllib3` to >=1.26.18.

### Removed
- Removed `requirements.txt` - this project has been using `poetry` for awhile.

## [1.0.0] - 2023-06-14
### Added
- Added support for OS-dependent configuration directories. For Linux (and most likely Cygwin), XDG directories are supported. For Windows, approximate analogs are used. MacOS is currently unsupported, as I have no idea which directories apply.

### Changed
- Configuration is now strictly in the OS-dependent configuration directories as listed above.
- The user configuration is now represented as an object (`config.Config`), simplifying validation and writing/saving.
- Script modules were moved to more descriptive names:
    - `gitea` contains all Gitea-related functionality.
    - `language` contains programming language-specific functions for Gitea.
    - `package.py` is all about packages (formerly dependencies).
- All instances of "dependencies" in the new `package.py` were replaced with "packages".

## [0.4.0] - 2023-02-25
### Added
- Added `get_python_dep_repos`, a script to find all repositories that use a provided dependency. It is a more general script than `get_outdated_python_deps`.
- Added `get_deploy_keys`, a script to view all deploy keys in use along with their public keys and repositories in use.

### Changed
- This project is now managed by `asdf-vm`, `direnv`, and `poetry`.
- Moved project scripts and configuration to `gitea_api_tools`.
- `scan_python_deps` was renamed `get_outdated_python_deps`.
- Made `utils` a sub-module.

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
