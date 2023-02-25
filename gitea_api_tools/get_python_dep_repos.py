import argparse
import json

import config
import utils
import utils.python


parser = argparse.ArgumentParser(
    description="Python dependency checker for Gitea API")
parser.add_argument("package", type=str, help="package name on PyPI")


def search_repos_for_dep(dependency: str) -> None:
    """Search repositories for use of the dependency.

    Args:
        dependency: Python dependency

    """
    repos = utils.list_repos()
    for user, repo in repos:
        u_repo = f"{user}/{repo}"
        current_repo = f"{config.HOST_API}/repos/{u_repo}"
        response = utils.get_url(f"{current_repo}/languages")
        if not response.encoding:
            config.LOGGER.error(
                config.NO_ENCODING.format("checking languages"))
            continue

        langs = json.loads(response.content.decode(response.encoding))
        if 'Python' not in langs:
            continue

        try:
            requirements = utils.python.process_requirementstxt(current_repo)
        except ValueError:
            pass

        try:
            # Silently ignore repositories that don't have the dependency
            if dependency in requirements:
                version = requirements[dependency]
                config.LOGGER.info(f"{u_repo}: {version}")
        except NameError:
            # Silently ignore missing requirements
            pass


def main() -> None:
    """Use args from command line."""
    args = parser.parse_args()
    search_repos_for_dep(args.package)


if __name__ == '__main__':
    main()
