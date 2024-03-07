from collections.abc import Iterable

from . import (
    deploy_key,
)

from .. import api


__all__ = [
    "deploy_key",
]

ERR_NO_FILE = (
    FileNotFoundError,
    ValueError,
)


def uses_language(repo: str, language: str) -> bool:
    """Check whether a repository is using a certain programming language.

    Args:
        repo: full repository name
        language: programming language

    Returns:
        bool: True if the repository is using the language; False otherwise

    """
    try:
        languages = api.get_response(f"repos/{repo}/languages")
    except FileNotFoundError:
        # Repository may not have any code
        return False
    except ValueError:
        api.config.logger.error(
            api.ERR_NO_ENCODING.format("checking languages"))
        return False

    return language in languages


def get_file_contents(repo: str, file: str) -> str:
    """Get a file from a repository.

    Args:
        repo: full repository name
        file: file that may belong to the repository; if not, raises exceptions

    Returns:
        str: contents of file in repo

    Raises:
        ValueError: for one of two reasons;
            1. response failed
            2. file encoding not available, so file could not be decoded

    """
    try:
        response = api.get_response(f"repos/{repo}/contents/{file}")
        return api.decode(response)
    except api.EX_NO_RESPONSE as e:
        raise ValueError("Response failed") from e
    except ValueError as e:
        raise ValueError(f"{file} could not be decoded") from e


def get_all_python_pkg_files() -> Iterable[tuple[str, str, str]]:
    """Get all Python package files.

    Returns:
        Iterable[tuple[str, str]]: for each iteration:
            repository name, package file name, contents

    """
    repos = api.list_repos()
    pkg_files = ("poetry.lock", "requirements.txt")
    for user, repo in repos:
        u_repo = f"{user}/{repo}"
        if not uses_language(u_repo, "Python"):
            continue

        # It is possible for a Python project not to have either files, so
        # no error message will be shown.
        for pkg_file in pkg_files:
            try:
                yield (u_repo, pkg_file, get_file_contents(u_repo, pkg_file))
            except ERR_NO_FILE:
                continue
