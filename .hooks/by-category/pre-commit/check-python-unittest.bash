#!/usr/bin/env bash

if ! python3 -m unittest tests/*.py 2> /dev/null; then
    printf '%s\n' "Tests failed; run 'python3 -m unittest tests/*.py'" >&2
    exit 1
fi
