import json
from typing import Dict

import utils

PACKAGE = str
VERSION = str
REQUIREMENTS = Dict[PACKAGE, VERSION]


def process_requirementstxt(repo: str) -> REQUIREMENTS:
    """Process Python requirements in the file format requirements.txt.

    requirements.txt is typically generated from using `pip freeze`.

    Args:
        repo: repository URL

    Returns:
        REQUIREMENTS: dictionary of packages to versions

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
