import json
from collections import defaultdict
from typing import TypeAlias

from .. import api
from ..api import config


config.validate()


ReposKeys: TypeAlias = dict[tuple[str, str], list[str]]
KEY_MESSAGE = """
Public Key:     {}
Fingerprint:    {}

- {}
---"""

EX_REPO_KEYS = (
    KeyError,
    RuntimeError,
    ValueError,
)


def list_keyed_repos(repos_keys: ReposKeys) -> None:
    """List the repositories that belong to each key from input.

    Args:
        repos_keys: keys tied to repositories

    """
    for (fingerprint, pubkey), repos in repos_keys.items():
        s_repos = "\n- ".join(repos)
        config.logger.info(KEY_MESSAGE.format(pubkey, fingerprint, s_repos))


def get_repo_keys(user_repo: str) -> list[tuple[str, str]]:
    """Get the key(s), if any, from a repository.

    Args:
        user_repo: full name of a repository in the format user/repo

    Returns:
        list[tuple[str, str]]: a list of keys associated with the repository,
            with each tuple being fingerprint (a hashed representation) and the
            public key of the key itself

    Raises:
        RuntimeError: could not access deploy keys at all
        ValueError: missing encoding for response
        KeyError: key response is missing "key" field

    """
    pubkey_words = 2
    keys = []

    curr_repo_keys = f"repos/{user_repo}/keys"
    try:
        response = api.get_response(curr_repo_keys)
    except FileNotFoundError as e:
        config.logger.warning(f"Could not access keys for {user_repo}")
        raise RuntimeError from e
    except ValueError:
        config.logger.error(api.ERR_NO_ENCODING.format("getting deploy keys"))
        raise ValueError("Could not decode file")

    key_data = json.loads(response)
    for key in key_data:
        if not isinstance(key, dict):
            config.logger.warning(f"{user_repo} response was not a dict/JSON")
            continue
        fingerprint = key["fingerprint"]
        try:
            pubkey = " ".join(key["key"].split()[:pubkey_words])
        except KeyError as e:
            config.logger.error(f"{user_repo} has malformed key: {key}")
            raise e
        rp_name = (fingerprint, pubkey)
        keys.append(rp_name)
    return keys


def get_keyed_repos() -> None:
    """Get the deploy keys for all repositories."""
    repos_keys: ReposKeys = defaultdict(list)

    repos = api.list_repos()
    for user, repo in repos:
        u_repo = f"{user}/{repo}"
        try:
            keys = get_repo_keys(u_repo)
        except EX_REPO_KEYS:
            config.logger.error(f"Due to errors, {u_repo} has been skipped")
            continue
        for key in keys:
            repos_keys[key].append(u_repo)

    list_keyed_repos(repos_keys)
