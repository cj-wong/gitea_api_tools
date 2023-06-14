import json
import re
import tomllib
from typing import Dict

from .. import utils


PACKAGE = str
VERSION = str
REQUIREMENTS = Dict[PACKAGE, VERSION]
PACKAGE_VERSION = re.compile(r'^[0-9]+\.[0-9]+\.[0-9]+$')


def process_requirementstxt(repo: str) -> REQUIREMENTS:
    """Process Python requirements in the file format requirements.txt.

    requirements.txt is typically generated from using `pip freeze`.

    Args:
        repo: repository URL

    Returns:
        REQUIREMENTS: dictionary of packages to versions

    Raises:
        ValueError: file could not be read or is invalid

    """
    try:
        file_contents = utils.get_repo_file_contents(repo, 'requirements.txt')
    except (FileNotFoundError, ValueError) as e:
        raise ValueError("File could not be read") from e

    resp_cont = json.loads(file_contents)
    text = resp_cont['content']
    encoding = resp_cont['encoding']

    try:
        contents = utils.decode(text, encoding)
    except ValueError as e:
        # Unknown encoding
        raise e

    requirements: REQUIREMENTS = {}

    for req in contents.split('\n'):
        try:
            package, version = req.split('==')
        except ValueError as e:
            raise utils.CouldNotParseDependency from e
        requirements[package] = version

    return requirements


def process_poetrylock(repo: str) -> REQUIREMENTS:
    """Process Python requirements in the file format poetry.lock.

    poetry.lock is typically generated from using `poetry install`.

    Args:
        repo: repository URL

    Returns:
        REQUIREMENTS: dictionary of packages to versions

    Raises:
        ValueError: one of several reasons:

            1. remote file not found (repository may not use poetry)
            2. unknown decoding from remote poetry.lock

    """
    try:
        file_contents = utils.get_repo_file_contents(repo, 'poetry.lock')
    except (FileNotFoundError, ValueError) as e:
        raise ValueError("File could not be read") from e

    resp_cont = json.loads(file_contents)
    text = resp_cont['content']
    encoding = resp_cont['encoding']

    try:
        contents = utils.decode(text, encoding)
    except ValueError as e:
        # Unknown encoding
        raise e

    poetry_reqs = tomllib.loads(contents)
    requirements: REQUIREMENTS = {}

    for requirement in poetry_reqs['package']:
        name = requirement['name']
        version = requirement['version']
        requirements[name] = version

    return requirements


def process_requirements(repo: str) -> REQUIREMENTS:
    """Process requirements in any and all formats.

    This function is a wrapper for processing the requirements in a set
    priority.

    Priority is the following:

        1. poetry.lock
        2. requirements.txt

    Whichever file is found/met first will be used.

    Args:
        repo: repository URL

    Returns:
        REQUIREMENTS: dictionary of packages to versions

    Raises:
        ValueError: no requirements could be parsed

    """
    try:
        return process_poetrylock(repo)
    except ValueError:
        pass

    try:
        return process_requirementstxt(repo)
    except (ValueError, utils.CouldNotParseDependency):
        pass

    raise ValueError("Could not process any requirements at all.")
