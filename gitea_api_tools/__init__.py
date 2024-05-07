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
parser.add_argument(
    "--json",
    action="store_true",
    default=False,
    help="whether to output as JSON (default: False)",
)
subparsers = parser.add_subparsers(required=True)

# one-off commands
parser_configure = subparsers.add_parser(
    "configure", help="Configure this script"
)
parser_configure.set_defaults(func=wrap_subparser_configure)

parser_whoami = subparsers.add_parser("whoami", help="Get your user ID")
parser_whoami.set_defaults(func=wrap_subparser_get_uid)

# get ...
parser_get = subparsers.add_parser("get", help="Get individual items")
parser_get_subparsers = parser_get.add_subparsers(required=True)
# get deploy-keys
parser_get_deploykeys = parser_get_subparsers.add_parser(
    "deploy-keys",
    aliases=["keys", "dk"],
    help="Get deploy keys",
    description="Get deploy keys alongside their respective repositories",
)
parser_get_deploykeys.set_defaults(func=wrap_subparser_get_deploykeys)
# get user-id
parser_get_uid = parser_get_subparsers.add_parser(
    "user-id",
    aliases=["uid", "id"],
    help="Get your user ID",
    description="Get your user ID and optionally save to configuration",
)
parser_get_uid.set_defaults(func=wrap_subparser_get_uid)

# get dependencies ...
parser_get_deps = parser_get_subparsers.add_parser(
    "dependencies",
    aliases=["dep", "deps", "dependency"],
    help="Get repositories containing dependencies by programming language",
)
parser_get_dep_langs = parser_get_deps.add_subparsers(required=True)
# get dependencies python
parser_get_dep_python = parser_get_dep_langs.add_parser(
    "python",
    aliases=["py"],
    help="Get repositories with Python dependency",
)
parser_get_dep_python.add_argument(
    "package", help="dependent package (e.g. from PyPI)"
)
parser_get_dep_python.add_argument(
    "-v",
    "--version",
    type=version.Version,
    default=version.SENTINEL_VERSION,
    help="optional version string like 1.0.0; don't prefix with 'v'",
)
parser_get_dep_python.set_defaults(func=wrap_subparser_list_python)


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
