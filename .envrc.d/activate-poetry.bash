#!/usr/bin/env bash

if poetry_env="$(poetry env info --path)"; then
    # shellcheck disable=SC1091
    . "${poetry_env}/bin/activate"
else
    tput setaf 1
    printf "%s\n" "Error: poetry env does not exist"
    tput sgr0
fi
