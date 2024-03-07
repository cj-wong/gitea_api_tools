import json
import time
from base64 import b64decode

import requests

from .. import config


session = requests.Session()

try:
    session.headers = {
        "Authorization": f"token {getattr(config.user_config, 'token')}",
        "Accept": "application/json",
        }
except AttributeError:
    config.logger.error("Could not load token. gitea.api disabled")
    REQUESTS_AVAILABLE = False
else:
    REQUESTS_AVAILABLE = True


REPOS = list[tuple[str, str]]

ERR_NO_TOKEN = "Can't execute requests without token"
ERR_NO_ENCODING = "No encoding was detected when {}"

EX_NO_RESPONSE = (RuntimeError, FileNotFoundError, ValueError)


def get_response(url: str) -> str:
    """Request a file from the Gitea instance given the `url`.

    It also decodes the immediate response for handling later.

    Because this is the most basic function of this module, no requests will
    be served if token is unavailable.

    Args:
        url: URL fragment excluding the hostname

    Returns:
        str: decoded response

    Raises:
        RuntimeError: no token, no requests
        FileNotFoundError: instance does not have a file at the given url
        ValueError: no encoding provided

    """
    if not REQUESTS_AVAILABLE:
        raise RuntimeError(ERR_NO_TOKEN)

    response = session.get(f"{config.user_config.host_api}/{url}")
    if response.status_code != 200:
        raise FileNotFoundError(f"Project does not have file at {url}")
    elif not response.encoding:
        raise ValueError("Could not decode file")

    return response.content.decode(response.encoding).strip()


def decode(response: str) -> str:
    """Decode provided text with its encoding.

    This function is to be used with API calls that may not return encoding in
    UTF-8. For example, some API calls return Base64 encoding.

    It's uncertain whether Gitea has other encoding besides Base64, however.

    Args:
        text: encoded text
        encoding: encoding of text

    Returns:
        str: decoded text

    Raises:
        ValueError: unknown encoding provided

    """
    try:
        full_response = json.loads(response)
        content = full_response["content"]
        encoding = full_response["encoding"]
    except json.decoder.JSONDecodeError:
        raise ValueError(f"Invalid response {response}")
    except KeyError:
        raise ValueError(f"{response} is missing required key 'content'")

    known_encodings = {
        'base64': lambda text: b64decode(text).decode(),
        }

    if encoding not in known_encodings:
        raise ValueError(f"Unknown encoding {encoding}")

    return known_encodings[encoding](content).strip()


def list_repos() -> REPOS:
    """List the repositories on the host.

    Returns:
        REPOS: list of repositories in the format (owner, repo_name)

    Raises:
        RuntimeError: no encoding detected in request; request may be invalid

    """
    try:
        search_archived_repos = getattr(
            config.user_config, 'search_archived_repos')
    except AttributeError as e:
        raise RuntimeError("Configuration is malformed") from e

    url = f"repos/search?archived={search_archived_repos}"

    uid = getattr(config.user_config, 'uid', None)
    if uid:
        url = f"{url}&uid={uid}"

    page = 0
    repos_left = True
    all_repos = []
    while repos_left:
        page += 1
        paged_url = f"{url}&page={page}"

        try:
            response = get_response(paged_url)
        except ValueError:
            raise RuntimeError(ERR_NO_ENCODING.format("fetching repos"))

        try:
            repos = json.loads(response)['data']
        except KeyError:
            raise RuntimeError(f"Page {page} of repositories is missing data")

        if repos:
            all_repos.extend(repos)
            time.sleep(1)
        else:
            repos_left = False

    return [repo["full_name"].split('/') for repo in all_repos]
