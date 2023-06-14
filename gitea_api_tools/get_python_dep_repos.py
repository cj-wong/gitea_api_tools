import argparse

from . import config
from . import gitea
from . import language


parser = argparse.ArgumentParser(
    description="Python dependency checker for Gitea API")
parser.add_argument("package", type=str, help="package name on PyPI")


def search_repos_for_dep(dependency: str) -> None:
    """Search repositories for use of the dependency.

    Args:
        dependency: Python dependency

    """
    repos = gitea.list_repos()
    for user, repo in repos:
        u_repo = f"{user}/{repo}"
        current_repo = f"{config.config.host_api}/repos/{u_repo}"
        if not gitea.is_repo_using_language(current_repo, 'Python'):
            continue

        try:
            requirements = language.python.process_requirements(current_repo)
        except ValueError:
            # Silently ignore missing requirements
            continue

        # Silently ignore repositories that don't have the dependency
        if dependency in requirements:
            version = requirements[dependency]
            config.logger.info(f"{u_repo}: {version}")


def oldmain() -> None:
    """Get Python repositories that use the provided package.

    Note: This is the pre-1.0.0 function and has been deprecated.

    """
    args = parser.parse_args()
    main(args.package)


def main(pkg: str) -> None:
    """Get Python repositories that use the provided package."""
    search_repos_for_dep(pkg)


if __name__ == '__main__':
    oldmain()
