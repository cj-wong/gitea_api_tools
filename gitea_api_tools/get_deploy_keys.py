import json
from collections import defaultdict
from typing import Dict, List, Tuple

import config
import utils


REPO_KEYS = Dict[Tuple[str, str], List[str]]
KEY_MESSAGE = """
Public Key:     {}
Fingerprint:    {}

- {}
---"""


def print_key_repos(repo_keys: REPO_KEYS) -> None:
    """Print the repositories that belong to each key from input.

    Args:
        repo_keys: keys tied to repositories

    """
    for (fingerprint, pubkey), repos in repo_keys.items():
        s_repos = '\n- '.join(repos)
        config.LOGGER.info(KEY_MESSAGE.format(pubkey, fingerprint, s_repos))


def main() -> None:
    """Get the deploy keys."""
    repo_keys: REPO_KEYS = defaultdict(list)
    pubkey_words = 2

    repos = utils.list_repos()
    for user, repo in repos:
        u_repo = f"{user}/{repo}"
        current_repo_keys = f"{config.HOST_API}/repos/{u_repo}/keys"
        response = utils.get_url(current_repo_keys)
        if response.status_code != 200:
            config.LOGGER.warning(f"Could not access keys for {u_repo}")
            continue
        elif not response.encoding:
            config.LOGGER.error(
                config.NO_ENCODING.format("getting deploy keys"))
            raise ValueError("Could not decode file")

        contents = response.content.decode(response.encoding).strip()
        keys = json.loads(contents)
        for key in keys:
            if type(key) is not dict:
                config.LOGGER.warning(f"{u_repo} response was not a dict/JSON")
                continue
            fingerprint = key["fingerprint"]
            try:
                pubkey = ' '.join(key["key"].split()[:pubkey_words])
            except KeyError as e:
                print(repo, key)
                raise e
            rp_name = (fingerprint, pubkey)
            repo_keys[rp_name].append(u_repo)

    print_key_repos(repo_keys)


if __name__ == '__main__':
    main()
