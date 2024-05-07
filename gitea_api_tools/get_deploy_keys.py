import json
from collections import defaultdict
from typing import Dict, List, Tuple

from . import config
from . import gitea


config.validate()


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
        s_repos = "\n- ".join(repos)
        config.logger.info(KEY_MESSAGE.format(pubkey, fingerprint, s_repos))


def main() -> None:
    """Get the deploy keys."""
    repo_keys: REPO_KEYS = defaultdict(list)
    pubkey_words = 2

    repos = gitea.api.list_repos()
    for user, repo in repos:
        u_repo = f"{user}/{repo}"
        curr_repo_keys = f"{config.user_config.host_api}/repos/{u_repo}/keys"
        try:
            response = gitea.api.get_response(curr_repo_keys)
        except FileNotFoundError:
            config.logger.warning(f"Could not access keys for {u_repo}")
            continue
        except ValueError:
            config.logger.error(
                gitea.api.ERR_NO_ENCODING.format("getting deploy keys")
            )
            raise ValueError("Could not decode file")

        keys = json.loads(response)
        for key in keys:
            if not isinstance(key, dict):
                config.logger.warning(f"{u_repo} response was not a dict/JSON")
                continue
            try:
                fingerprint = key["fingerprint"]
                pubkey = " ".join(key["key"].split()[:pubkey_words])
            except KeyError as e:
                config.logger.error(
                    f"Couldn't find fingerprint or pubkey for {key} in {repo}"
                )
                raise e
            rp_name = (fingerprint, pubkey)
            repo_keys[rp_name].append(u_repo)

    print_key_repos(repo_keys)


if __name__ == "__main__":
    main()
