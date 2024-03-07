# Tools for [Gitea] API

## Overview

This project is a toolbox for viewing [Gitea] settings.

For detailed information, consult the [docs](docs).

## Requirements

The code was tested with the following:

- Python 3.11
    - `requests`
    - other [requirements](pyproject.toml)

## Install

### Using Poetry

Run `poetry install` on the project root to get started. This will grant access to the `gitea-api` script. Once created, `gitea-api` can be sym-linked from wherever the environment is to a more convenient place like `~/.local/bin`.

### Manual

You can also run `pip install pyproject.toml`. Once installed, you can simply run `python3 -m gitea_api_tools` while in the project directory. If you choose this method, replace any mentions of `gitea-api` below with that command.

## Setup

Create an access token. ([Reference][GITEA_API_TOKEN]) The minimum permissions used by this project are "Read" for both "Repository" and "User".

You can now run `gitea-api configure` to interactively configure your settings.

### Manual (not recommended)

Copy `config.json.example` and make `config.json`, replacing the temporary values:

- `"host"` is the URL to access the Gitea instance. Do not add the Swagger API path as it will be handled by the program.
- `"token"` is the API token. Follow the setup steps at the top of this section for the token.
- `"uid"` is an optional integer representing your user account. It can be easily retrieved from `gitea-api user_id`. Although it can also be manually found using the API, the aforementioned command is faster and allows the user to save it to settings at once.
- `"search_archived_repos"` defaults to `false`. If `true`, the initial repository search will include archived repositories, which may be undesirable.

Move the configured `config.json` into a directory named `gitea-api-tools` under one of the following directories, based on OS:

#### Linux (and most likely Cygwin)

The settings file goes into a sub-directory named `gitea-api-tools` under your XDG configuration directory (environment variable `XDG_CONFIG_HOME`) or if that's not set, `${HOME}/.config`. The resulting path should look like `${HOME}/.config/gitea-api-tools`.

#### Windows

`%LOCALAPPDATA%` is approximately close to `XDG_CONFIG_HOME` (and `XDG_STATE_HOME`). In recent Windows versions, the resulting path should look like `C:\Users\user\AppData\Local\gitea-api-tools`.

#### MacOS and other OSes

Currently unsupported, as I'm unsure what paths are analogous to those provided.

## Disclaimer

This project is not affiliated with or endorsed by [Gitea]. See [LICENSE](LICENSE) for more detail.

[Gitea]: https://gitea.io/
[GITEA_API_TOKEN]: https://docs.gitea.io/en-us/api-usage/#generating-and-listing-api-tokens
