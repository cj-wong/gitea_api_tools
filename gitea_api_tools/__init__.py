import argparse

from . import gitea
from . import package
from .config import configure
from .package import version


parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(required=True, dest="command")

# Sub-commands that take no arguments
parser_configure = subparsers.add_parser("configure")
parser_deploy_keys = subparsers.add_parser("deploy_keys")
parser_user_id = subparsers.add_parser("user_id")

# Sub-commands that require at least one argument
parser_python = subparsers.add_parser("python")
parser_python.add_argument("package")
parser_python.add_argument(
    "-v", "--version", type=version.Version, default=version.SENTINEL_VERSION
)


def main() -> None:
    """Run the Gitea API toolkit."""
    args = parser.parse_args()
    match args.command:
        case "configure":
            configure.configure_interactively()
        case "deploy_keys":
            gitea.repo.deploy_key.get_keyed_repos()
        case "user_id":
            gitea.user.store_retrieved_id()
        case "python":
            package.python.list_dependent_repos(args.package, args.version)
        case _:
            raise RuntimeError("Invalid option provided")


if __name__ == "__main__":
    main()
