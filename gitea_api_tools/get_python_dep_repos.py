import argparse

from . import config
from . import utils


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
        if not utils.is_repo_using_language(current_repo, 'Python'):
            continue

        try:
            requirements = utils.python.process_requirements(current_repo)
        except ValueError:
            # Silently ignore missing requirements
            continue

        # Silently ignore repositories that don't have the dependency
        if dependency in requirements:
            version = requirements[dependency]
            config.logger.info(f"{u_repo}: {version}")


def main() -> None:
    """Use args from command line."""
    args = parser.parse_args()
    search_repos_for_dep(args.package)


if __name__ == '__main__':
    main()
