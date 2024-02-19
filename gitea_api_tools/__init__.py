import argparse

from . import get_deploy_keys
from . import get_user_id
from . import get_outdated_python_deps
from . import get_python_dep_repos
from .config import configure


parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(required=True)

# Sub-commands that take no arguments
parser_configure = subparsers.add_parser("configure")
parser_deploy_keys = subparsers.add_parser("deploy_keys")
parser_user_id = subparsers.add_parser("user_id")

# Sub-commands that require at least one argument
parser_python = subparsers.add_parser("python")
parser_python.add_argument("package")
parser_python.add_argument("-v", "--version")

# Because the contents of parsers get flattened into a single namespace, it's
# necessary to add a sentinel argument to know which sub-command was called.
for subparser in subparsers.choices.values():
    subparser.add_argument(
        "_", action="store_const", const=subparser.prog, help="ignore this")


def main() -> None:
    """Run the Gitea API toolkit."""
    args = parser.parse_args()
    match args._.split():
        case [_, "configure"]:
            configure.configure_interactively()
        case [_, "deploy_keys"]:
            get_deploy_keys.main()
        case [_, "user_id"]:
            get_user_id.main()
        case [_, "python"]:
            if args.version:
                get_outdated_python_deps.main(args.package, args.version)
            else:
                get_python_dep_repos.main(args.package)
        case _:
            raise RuntimeError("Invalid option provided")


if __name__ == "__main__":
    main()
