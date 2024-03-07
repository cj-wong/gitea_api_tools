import tomllib

from . import version
from .. import config
from .. import gitea
from .. import package


def process_requirementstxt_OLD(repo: str) -> package.formats.REQUIREMENTS:
    """Process Python requirements in the file format requirements.txt.

    requirements.txt is typically generated from using `pip freeze`.

    Args:
        repo: repository URL

    Returns:
        package.formats.REQUIREMENTS: dictionary of packages to versions

    Raises:
        ValueError: file could not be read or is invalid

    """
    try:
        file_contents = gitea.repo.get_file_contents(repo, 'requirements.txt')
    except gitea.repo.ERR_NO_FILE as e:
        raise ValueError("File could not be read") from e

    try:
        contents = gitea.api.decode(file_contents)
    except ValueError as e:
        # Unknown encoding
        raise e

    requirements: package.formats.REQUIREMENTS = {}

    for req in contents.split('\n'):
        try:
            pkg, version = req.split('==')
        except ValueError as e:
            raise package.CouldNotParse from e
        requirements[pkg] = version

    return requirements


def process_poetrylock_OLD(repo: str) -> package.formats.REQUIREMENTS:
    """Process Python requirements in the file format poetry.lock.

    poetry.lock is typically generated from using `poetry install`.

    Args:
        repo: repository URL

    Returns:
        package.formats.REQUIREMENTS: dictionary of packages to versions

    Raises:
        ValueError: one of several reasons:

            1. remote file not found (repository may not use poetry)
            2. unknown decoding from remote poetry.lock

    """
    try:
        file_contents = gitea.repo.get_file_contents(repo, 'poetry.lock')
    except gitea.repo.ERR_NO_FILE as e:
        raise ValueError("File could not be read") from e

    try:
        contents = gitea.api.decode(file_contents)
    except ValueError as e:
        # Unknown encoding
        raise e

    poetry_reqs = tomllib.loads(contents)
    requirements: package.formats.REQUIREMENTS = {}

    for requirement in poetry_reqs['package']:
        name = requirement['name']
        version = requirement['version']
        requirements[name] = version

    return requirements


def process_requirements(repo: str) -> package.formats.REQUIREMENTS:
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
        package.formats.REQUIREMENTS: dictionary of packages to versions

    Raises:
        ValueError: no requirements could be parsed

    """
    try:
        return process_poetrylock_OLD(repo)
    except ValueError:
        pass

    try:
        return process_requirementstxt_OLD(repo)
    except (ValueError, package.CouldNotParse):
        pass

    raise ValueError("Could not process any requirements at all.")


def process_requirements_txt(contents: str) -> package.formats.REQUIREMENTS:
    """Process Python requirements in the file format requirements.txt.

    requirements.txt is typically generated from using `pip freeze`.

    Args:
        contents: contents of package file

    Returns:
        package.formats.REQUIREMENTS: dictionary of packages to versions

    """
    requirements: package.formats.REQUIREMENTS = {}

    for req in contents.split('\n'):
        try:
            pkg, version = req.split('==')
        except ValueError as e:
            raise package.CouldNotParse from e
        requirements[pkg] = version

    return requirements


def process_poetry_lock(contents: str) -> package.formats.REQUIREMENTS:
    """Process Python requirements in the file format poetry.lock.

    poetry.lock is typically generated from using `poetry install`.

    Args:
        contents: contents of package file

    Returns:
        package.formats.REQUIREMENTS: dictionary of packages to versions

    """
    poetry_reqs = tomllib.loads(contents)
    requirements: package.formats.REQUIREMENTS = {}

    for requirement in poetry_reqs['package']:
        name = requirement['name']
        version = requirement['version']
        requirements[name] = version

    return requirements


def list_dependent_repos(
        package: str, ver_restrict: version.Version = version.SENTINEL_VERSION
        ) -> None:
    """List repositories dependent on given `package`.

    Args:
        package: a third party package
        ver_restrict: optional; a version to restrict listings; any below;
            defaults to the sentinel version

    """
    for repo, file, contents in gitea.repo.get_all_python_pkg_files():
        match file:
            case "poetry.lock":
                packages = process_poetry_lock(contents)
            case "requirements.txt":
                packages = process_requirements_txt(contents)
            case _:
                config.logger.error(f"Unknown Python package file {file}")
                continue
        if package not in packages:
            continue

        if not ver_restrict:
            config.logger.info(f"{repo}: {packages[package]}")
        else:
            repo_version = version.Version(packages[package])
            try:
                if ver_restrict > repo_version:
                    config.logger.info(f"{repo} is outdated: {repo_version}")
            except (TypeError, ValueError):
                config.logger.warning(
                    f"{ver_restrict} can't be compared against {repo_version}")
                continue
