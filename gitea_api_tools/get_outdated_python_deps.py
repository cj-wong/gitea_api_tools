import argparse
import json

import config
import utils
import utils.python

parser = argparse.ArgumentParser(
    description="Python dependency scanner for Gitea API")
parser.add_argument("package", type=str, help="package name on PyPI")
parser.add_argument("version", type=str, help="package version")


def get_outdated_dep_version(
        dependencies: utils.python.REQUIREMENTS, p_name: str,
        p_ver: utils.Version) -> str:
    """Get the requirement version, if present.

    Args:
        dependencies: list of dependencies in the format 'req==x.y.z'
        p_name: package name
        p_ver: package version as an object

    Returns:
        str: the version of the outdated package

    Raises:
        utils.CouldNotParseDependency: dependency format could not be parsed
        utils.NoDedendency: package was not found in this project
        utils.MismatchedDependency: version could not be adequately compared

    """
    if p_name not in dependencies:
        raise utils.NoDependency

    d_ver = dependencies[p_name]

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
        repos: utils.REPOS, p_name: str, p_ver: utils.Version) -> None:
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
            requirements = utils.python.process_requirements(current_repo)
        except ValueError:
            # Silently ignore missing requirements
            continue

        try:
            dep_ver = get_outdated_dep_version(requirements, p_name, p_ver)
        except utils.NoDependency:
            continue
        except (utils.MismatchedDependency, utils.CouldNotParseDependency):
            config.LOGGER.warning("Encountered an error matching deps")
            config.LOGGER.warning(f"The affected repository is {u_repo}")
            continue
        else:
            config.LOGGER.info(f"{u_repo} is outdated: {dep_ver}")
            outdated += 1

    if not outdated:
        config.LOGGER.info("No packages are affected")


def main() -> None:
    """Run all of the API requests."""
    args = parser.parse_args()
    pkg_name = args.package
    pkg_ver = args.version
    if not config.PACKAGE_VERSION.match(pkg_ver):
        config.LOGGER.warning(f"{pkg_ver} does not appear to match x.y.z.")
        config.LOGGER.warning("Comparisons may not work correctly.")

    repos = utils.list_repos()
    compare_dependency(repos, pkg_name, utils.Version(pkg_ver))


if __name__ == '__main__':
    main()
