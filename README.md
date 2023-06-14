# Tools for [Gitea] API

## Overview

This project contains tools as scripts to manipulate [Gitea] settings.

For detailed information, consult [docs](docs).

## Requirements

The code was tested with the following:

- Python 3.11
    - `requests`
    - other [requirements](pyproject.toml)

## Setup

Run `poetry install` on the project root to get started. This will grant access to the `gitea-api` script.

Copy `config.json.example` and make `config.json`, replacing the temporary values:

- `"host"` is the URL to access the Gitea instance. Do not add the Swagger API path as it will be handled by the program.
- `"token"` is the API token. Reference: https://docs.gitea.io/en-us/api-usage/#generating-and-listing-api-tokens
    - Gitea now supports scoped tokens. The minimum scope required for this project is `repo`, at the very top of the list.
- `"uid"` is an optional integer representing your user account. It can be easily retrieved from `get-user-id`. It can also be manually found using the API.
- `"search_archived_repos"` defaults to `false`. If `true`, the initial repository search will include archived repositories, which may be undesirable.

Move the configured `config.json` into a directory named `gitea-api-tools` under one of the following directories, based on OS:

### Linux (and most likely Cygwin)

Either your XDG configuration directory (environment variable `XDG_CONFIG_HOME`) or if that's not set, `${HOME}/.config`. The resulting path should be something like `${HOME}/.config/gitea-api-tools`.

### Windows

`%LOCALAPPDATA%` is approximately close to `XDG_CONFIG_HOME` (and `XDG_STATE_HOME`). In recent Windows versions, the resulting path should be something like `C:\Users\user\AppData\Local\gitea-api-tools`.

### MacOS and other OSes

Currently unsupported, as I'm unsure what paths are analogous to those provided.

## Disclaimer

This project is not affiliated with or endorsed by [Gitea]. See [LICENSE](LICENSE) for more detail.

[Gitea]: https://gitea.io/
