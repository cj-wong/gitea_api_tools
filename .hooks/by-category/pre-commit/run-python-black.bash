#!/usr/bin/env bash

if ! command -v black &>/dev/null; then
    tput setaf 1
    printf "%s\n" "python-black isn't installed" >&2
    tput sgr0
    exit 1
fi

changed="$(git diff --cached --name-only --diff-filter=M)"
stat_files=()
if [ -n "$changed" ]; then
    while read -r line; do
        if [[ "$line" =~ \.py$ ]]; then
            stat_files+=("$line")
        fi
    done <<< "$changed"
fi

if [[ "${#stat_files[@]}" -gt 0 ]]; then
    if black "${stat_files[@]}"; then
        git add "${stat_files[@]}" || :
    fi
fi
