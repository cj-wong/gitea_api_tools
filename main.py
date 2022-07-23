import base64
import json
import sys
from typing import List, Tuple

import requests

import config


REPOS = List[Tuple[str, str]]


def list_repos() -> REPOS:
    """List the repositories on the host.

    Returns:
        REPOS: list of repositories in the format (owner, repo_name)

    """
    url = f"{config.HOST_API}/repos/search?limit={config.SWAGGER_API_LIMIT}"
    url = f"{url}&archived={config.SEARCH_ARCHIVED_REPOS}"
    if config.UID:
        url = f"{url}&uid={config.UID}"
    response = requests.get(url, headers=config.HEADERS)
    repos = json.loads(response.content.decode(response.encoding))['data']
    return [repo["full_name"].split('/') for repo in repos]


def compare_dependency(repos: REPOS, p_name: str, p_ver: str) -> None:
    """Compare dependency against Python-only repositories.

    Args:
        repos (REPOS): list of repositories
        p_name (str): package name
        p_ver (str): package version; usually in format x.y.z

    Raises:
        ValueError: unknown encoding detected in requirements file

    """
    outdated = 0
    for user, repo in repos:
        url = f"{config.HOST_API}/repos/{user}/{repo}"
        response = requests.get(f"{url}/languages", headers=config.HEADERS)
        langs = json.loads(response.content.decode(response.encoding))
        if 'Python' not in langs:
            continue
        response = requests.get(
            f"{url}/contents/requirements.txt", headers=config.HEADERS)
        if response.status_code != 200:
            continue
        resp_cont = json.loads(response.content.decode(response.encoding))
        # Uncertain whether Gitea has other encoding besides base64
        # for file contents
        if resp_cont['encoding'] != 'base64':
            raise ValueError(f"Unknown encoding {resp_cont['encoding']}")
        else:
            requirements = [
                requirement.split('==')
                for requirement in
                base64.b64decode(resp_cont['content']).decode().split()
                ]
            try:
                version, = [
                    version
                    for (package, version) in requirements
                    if package == p_name
                    ]
            except ValueError:
                continue
            if p_ver > version:
                config.LOGGER.info(f"{user}/{repo} is outdated: {version}")
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

    repos = list_repos()
    compare_dependency(repos, package_name, package_ver)


if __name__ == '__main__':
    main()
