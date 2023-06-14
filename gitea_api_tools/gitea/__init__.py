import json
import time
from base64 import b64decode
from typing import List, Tuple

import requests

from .. import config


REPOS = List[Tuple[str, str]]
NO_ENCODING = "No encoding was detected when {}"


def get_url(url: str) -> requests.models.Response:
    """Call requests.get with headers from config."""
    return requests.get(url, headers=config.HEADERS)


def get_repo_file_contents(repo: str, file: str) -> str:
    """Get a file from a repository.

    Args:
        repo: repository
        file: file that may belong to the repository; if not, raises exceptions

    Returns:
        str: contents of file in repo

    Raises:
        FileNotFoundError: file doesn't exist
        ValueError: file encoding not available, so file could not be decoded

    """
    response = get_url(f"{repo}/contents/{file}")
    if response.status_code != 200:
        raise FileNotFoundError(f"Project does not use {file}")
    elif not response.encoding:
        config.logger.error(NO_ENCODING.format(f"getting {file}"))
        raise ValueError("Could not decode file")

    contents = response.content.decode(response.encoding).strip()
    if not json.loads(contents):
        raise ValueError("Empty file")

    return contents


def decode(text: str, encoding: str) -> str:
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
    known_encodings = {
        'base64': lambda text: b64decode(text).decode(),
        }

    if encoding not in known_encodings:
        raise ValueError(f"Unknown encoding {encoding}")

    return known_encodings[encoding](text).strip()


def list_repos() -> REPOS:
    """List the repositories on the host.

    Returns:
        REPOS: list of repositories in the format (owner, repo_name)

    Raises:
        RuntimeError: no encoding detected in request; request may be invalid

    """
    try:
        search_archived_repos = getattr(config.config, 'search_archived_repos')
    except AttributeError as e:
        raise RuntimeError("Configuration is malformed") from e

    url = f"{config.config.host_api}/repos/search"
    url = f"{url}?archived={search_archived_repos}"

    uid = getattr(config.config, 'uid', None)
    if uid:
        url = f"{url}&uid={uid}"

    page = 0
    repos_left = True
    all_repos = []
    while repos_left:
        page += 1
        paged_url = f"{url}&page={page}"
        response = get_url(paged_url)
        if not response.encoding:
            raise RuntimeError(NO_ENCODING.format("fetching repos"))
        repos = json.loads(response.content.decode(response.encoding))['data']
        if repos:
            all_repos.extend(repos)
            time.sleep(1)
        else:
            repos_left = False
    return [repo["full_name"].split('/') for repo in all_repos]


def is_repo_using_language(repo: str, language: str) -> bool:
    """Check whether a repository is using a certain programming language.

    Args:
        repo: repository
        language: programming language

    Returns:
        bool: True if the repository is using the language; False otherwise

    """
    response = get_url(f"{repo}/languages")
    if not response.encoding:
        config.logger.error(NO_ENCODING.format("checking languages"))
        return False

    langs = json.loads(response.content.decode(response.encoding))
    return language in langs
