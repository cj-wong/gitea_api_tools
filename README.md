# Tools for [Gitea] API

## Overview

This project contains tools as scripts to manipulate [Gitea] settings.

For detailed information, consult [docs](docs).

## Requirements

The code was tested with the following:

- Python 3.9
    - `requests`
    - other [requirements](requirements.txt)

## Setup

Copy `config.json.example` and make `config.json`, filling in the values.

- "host" is the domain. Do not add the Swagger API path as it will be handled by the program.
- "token" is the API token. Reference: https://docs.gitea.io/en-us/api-usage/#generating-and-listing-api-tokens
- "uid" is an optional integer representing your user account. It can be found using the API.
- "search_archived_repos" defaults to `false`. If `true`, the initial repository search will include archived repositories, which may be undesirable.

## Disclaimer

This project is not affiliated with or endorsed by [Gitea]. See [LICENSE](LICENSE) for more detail.

Additionally, currently only `requirements.txt` is supported. In the future, I may expand functionality to other means of managing dependencies.

[Gitea]: https://gitea.io/
