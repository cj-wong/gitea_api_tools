#!/usr/bin/env python3

import subprocess
import sys
from shutil import which


if not which("ruff"):
    subprocess.run("tput setaf 1".split())
    print("ruff isn't installed")
    subprocess.run("tput sgr0".split())
    sys.exit(1)


FILES = list[str]


def get_new_changed_files() -> FILES:
    """Get new or changed files from `git status`.

    Returns:
        FILES: list of new or changed files

    """
    command = "git diff --cached --name-only --diff-filter=AM"
    return (
        subprocess.run(command.split(), capture_output=True)
        .stdout.decode()
        .split("\n")
    )


def get_python_files(files: FILES) -> FILES:
    """Get only Python files from provided list of files

    Args:
        files: files, from `get_new_changed_files()`

    Returns:
        FILES: only Python files

    """
    return [file for file in files if file.endswith(".py")]


def run_ruff_lint(files: FILES) -> None:
    """Run the linter on the files.

    If no files were provided, simply exit. It's possible that no Python files
    were committed this time.

    Args:
        files: files, from `get_python_files()`

    """
    if not files:
        sys.exit(0)
    command = "ruff check".split()
    command.extend(files)
    subprocess.run(command, check=True)


run_ruff_lint(get_python_files(get_new_changed_files()))
