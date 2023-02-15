# Python Dependency Scanner

## Overview

This tool scans all of your repositories for dependencies. The intended use case is this: if you use Gitea as the main remote or a mirror for your repositories, you can rapidly scan your repositories for dependency versions. This combined with GitHub's dependabot makes checking your packages much easier.

## Usage

```
usage: scan_python_deps.py [-h] package version

Python dependency scanner for Gitea API

positional arguments:
  package     package name on PyPI
  version     package version

optional arguments:
  -h, --help  show this help message and exit

```
