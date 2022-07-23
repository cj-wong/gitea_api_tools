# Python Dependency Scanner for [Gitea] API

## Overview

This project scans all of your [Gitea] repositories for dependencies. The intended use case is this: if you use [Gitea] as the main remote or a mirror for your repositories, you can rapidly scan your repositories for dependency versions. This combined with GitHub's dependabot makes checking your packages much easier.

## Usage

`$ python main.py PACKAGE_NAME PACKAGE_VER`

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
