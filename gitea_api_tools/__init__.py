import argparse

from . import gitea
from . import package
from .config import configure
from .package import version


# These functions serve purely as wrappers for the sub-commands' function.
def wrap_subparser_configure(args: argparse.Namespace) -> None:
    configure.configure_interactively()


def wrap_subparser_get_deploykeys(args: argparse.Namespace) -> None:
    gitea.repo.deploy_key.get_keyed_repos()


def wrap_subparser_get_uid(args: argparse.Namespace) -> None:
    gitea.user.store_retrieved_id()


def wrap_subparser_list_python(args: argparse.Namespace) -> None:
    package.python.list_dependent_repos(args.package, args.version)


parser = argparse.ArgumentParser(description="A toolbox for Gitea API")
subparsers = parser.add_subparsers(required=True)

# Sub-commands that take no arguments
parser_configure = subparsers.add_parser("configure")
parser_configure.set_defaults(func=wrap_subparser_configure)

parser_deploy_keys = subparsers.add_parser(
    "deploy_keys",
    aliases=["dep", "keys", "dk"],
    description="View deploy keys",
)
parser_deploy_keys.set_defaults(func=wrap_subparser_get_deploykeys)

parser_user_id = subparsers.add_parser(
    "user_id", aliases=["uid", "id", "whoami"], description="View your user ID"
)
parser_user_id.set_defaults(func=wrap_subparser_get_uid)

# Sub-commands that require at least one argument
parser_python = subparsers.add_parser(
    "python", aliases=["py"], description="View your Python repositories"
)
parser_python.add_argument(
    "package", help="dependent package (e.g. from PyPI)"
)
parser_python.add_argument(
    "-v",
    "--version",
    type=version.Version,
    default=version.SENTINEL_VERSION,
    help="optional version string like 1.0.0; don't prefix with 'v'",
)
parser_python.set_defaults(func=wrap_subparser_list_python)


def main() -> None:
    """Run the Gitea API toolkit.

    Raises:
        RuntimeError: invalid option from command line

    """
    args = parser.parse_args()
    try:
        args.func(args)
    except AttributeError:
        raise RuntimeError("Invalid option provided")


if __name__ == "__main__":
    main()
