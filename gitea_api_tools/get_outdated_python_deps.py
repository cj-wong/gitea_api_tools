import argparse

from . import config
from . import gitea
from . import package


config.validate()


parser = argparse.ArgumentParser(
    description="Python package tracker for Gitea API"
)
parser.add_argument("package", type=str, help="package name on PyPI")
parser.add_argument("version", type=str, help="package version")


def get_outdated_dep_version(
    dependencies: package.formats.Requirements,
    p_name: str,
    p_ver: package.version.Version,
) -> str:
    """Get the requirement version, if present.

    Args:
        dependencies: list of dependencies in the format 'req==x.y.z'
        p_name: package name
        p_ver: package version as an object

    Returns:
        str: the version of the outdated package

    Raises:
        package.CouldNotParse: dependency format could not be parsed
        package.NotFound: package was not found in this project
        package.MismatchedFormat: version could not be adequately
            compared

    """
    if p_name not in dependencies:
        raise package.NotFound

    d_ver = dependencies[p_name]

    try:
        if p_ver > package.version.Version(d_ver):
            return d_ver
    except TypeError:
        config.logger.warning(f"{p_ver} can't be compared against {d_ver}")
        raise package.version.MismatchedFormat
    except ValueError:
        # Implicitly raised by comparison between Versions. Raised when the
        # number of components don't match between versions.
        # e.g. x.y.z compared against x.y
        config.logger.warning(f"{p_ver} can't be compared against {d_ver}")
        config.logger.warning("The version format may be different.")
        raise package.version.MismatchedFormat

    raise package.NotFound


def compare_dependency(
    repos: gitea.api.Repos, p_name: str, p_ver: package.version.Version
) -> None:
    """Compare dependency against Python-only repositories.

    Args:
        repos: list of repositories
        p_name: package name
        p_ver: package version as an object

    Raises:
        ValueError: unknown encoding detected in requirements file

    """
    outdated = 0
    for user, repo in repos:
        u_repo = f"{user}/{repo}"
        current_repo = f"{config.user_config.host_api}/repos/{u_repo}"
        if not gitea.repo.uses_language(current_repo, "Python"):
            continue

        try:
            requirements = package.python.process_requirements(current_repo)
        except ValueError:
            # Silently ignore missing requirements
            continue

        try:
            dep_ver = get_outdated_dep_version(requirements, p_name, p_ver)
        except package.NotFound:
            continue
        except (package.version.MismatchedFormat, package.CouldNotParse):
            config.logger.warning("Encountered an error matching deps")
            config.logger.warning(f"The affected repository is {u_repo}")
            continue
        else:
            config.logger.info(f"{u_repo} is outdated: {dep_ver}")
            outdated += 1

    if not outdated:
        config.logger.info("No packages are affected")


def oldmain() -> None:
    """Get the outdated Python packages.

    Note: This is the pre-1.0.0 function and has been deprecated.

    """
    args = parser.parse_args()
    main(args.package, args.version)


def main(pkg: str, version: str) -> None:
    """Get the outdated Python packages.

    Args:
        pkg: package name
        version: version string

    """
    if not package.version.VERSION_PATTERN.match(version):
        config.logger.warning(f"{version} does not appear to match x.y.z.")
        config.logger.warning("Comparisons may not work correctly.")

    repos = gitea.api.list_repos()
    compare_dependency(repos, pkg, package.version.Version(version))


if __name__ == "__main__":
    oldmain()
