import base64
import json
import sys
from typing import List, Tuple

import requests

import config
import utils


REPOS = List[Tuple[str, str]]
NO_ENCODING = "No encoding was detected when {}"


def list_repos() -> REPOS:
    """List the repositories on the host.

    Returns:
        REPOS: list of repositories in the format (owner, repo_name)

    Raises:
        RuntimeError: no encoding detected in request; request may be invalid

    """
    url = f"{config.HOST_API}/repos/search?limit={config.SWAGGER_API_LIMIT}"
    url = f"{url}&archived={config.SEARCH_ARCHIVED_REPOS}"
    if config.UID:
        url = f"{url}&uid={config.UID}"
    response = requests.get(url, headers=config.HEADERS)
    if not response.encoding:
        raise RuntimeError(NO_ENCODING.format("fetching repos"))
    repos = json.loads(response.content.decode(response.encoding))['data']
    return [repo["full_name"].split('/') for repo in repos]


def get_outdated_dep_version(
        dependencies: List[str], p_name: str, p_ver: utils.Version) -> str:
    """Get the requirement version, if present.

    Args:
        dependencies (List[str]): list of dependencies in the format
            'req==x.y.z'
        p_name (str): package name
        p_ver (utils.Version): package version as an object

    Returns:
        str: the version of the outdated package

    Raises:
        utils.NoDedendency: package was not found in this project
        utils.MismatchedDependency: version could not be adequately compared

    """
    for dependency in dependencies:
        d_name, d_ver = dependency.split('==')
        if d_name != p_name:
            continue
        try:
            if p_ver > utils.Version(d_ver):
                return d_ver
        except TypeError:
            config.LOGGER.warning(f"{p_ver} can't be compared against {d_ver}")
            raise utils.MismatchedDependency
        except ValueError:
            # Implicitly raised by comparison between Versions. Raised when the
            # number of components don't match between versions.
            # e.g. x.y.z compared against x.y
            config.LOGGER.warning(f"{p_ver} can't be compared against {d_ver}")
            config.LOGGER.warning("The version format may be different.")
            raise utils.MismatchedDependency

    raise utils.NoDependency


def compare_dependency(
        repos: REPOS, p_name: str, p_ver: utils.Version) -> None:
    """Compare dependency against Python-only repositories.

    Args:
        repos (REPOS): list of repositories
        p_name (str): package name
        p_ver (utils.Version): package version as an object

    Raises:
        ValueError: unknown encoding detected in requirements file

    """
    outdated = 0
    for user, repo in repos:
        u_repo = f"{user}/{repo}"
        url = f"{config.HOST_API}/repos/{u_repo}"
        response = requests.get(f"{url}/languages", headers=config.HEADERS)
        if not response.encoding:
            config.LOGGER.error(NO_ENCODING.format("checking languages"))
            continue
        langs = json.loads(response.content.decode(response.encoding))
        if 'Python' not in langs:
            continue
        response = requests.get(
            f"{url}/contents/requirements.txt", headers=config.HEADERS)
        if response.status_code != 200:
            continue
        elif not response.encoding:
            config.LOGGER.error(NO_ENCODING.format("getting requirements.txt"))
            continue
        resp_cont = json.loads(response.content.decode(response.encoding))
        # Uncertain whether Gitea has other encoding besides base64
        # for file contents
        if resp_cont['encoding'] != 'base64':
            raise ValueError(f"Unknown encoding {resp_cont['encoding']}")
        else:
            requirements = (
                base64.b64decode(resp_cont['content']).decode().split())
            try:
                dep_ver = get_outdated_dep_version(requirements, p_name, p_ver)
            except utils.NoDependency:
                continue
            except utils.MismatchedDependency:
                config.LOGGER.warning(f"The affected repository is {u_repo}")
                continue
            else:
                config.LOGGER.info(f"{u_repo} is outdated: {dep_ver}")
                outdated += 1

    if not outdated:
        config.LOGGER.info("No packages are affected")


def main() -> None:
    """Run all of the API requests."""
    if len(sys.argv) != 3:
        config.LOGGER.error("Usage: main.py PACKAGE_NAME PACKAGE_VER")
        sys.exit(config.EXIT_NO_ARGS)
    package_name, package_ver = sys.argv[1:]
    if not config.PACKAGE_VERSION.match(package_ver):
        config.LOGGER.warning(f"{package_ver} does not appear to match x.y.z.")
        config.LOGGER.warning("Comparisons may not work correctly.")

    repos = list_repos()
    compare_dependency(repos, package_name, utils.Version(package_ver))


if __name__ == '__main__':
    main()
