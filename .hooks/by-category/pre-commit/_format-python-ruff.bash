#!/usr/bin/env bash

if ! command -v ruff &>/dev/null; then
    tput setaf 1
    printf "%s\n" "ruff isn't installed" >&2
    tput sgr0
    exit 1
fi

changed="$(git diff --cached --name-only --diff-filter=AM)"
stat_files=()
if [ -n "${changed}" ]; then
    while read -r line; do
        if [[ "${line}" =~ \.py$ ]]; then
            stat_files+=("${line}")
        fi
    done <<< "${changed}"
fi

if [[ "${#stat_files[@]}" -gt 0 ]]; then
    if ruff format "${stat_files[@]}"; then
        git add "${stat_files[@]}" || :
    fi
fi
