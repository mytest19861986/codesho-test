#!/usr/bin/env sh
set -eu

status=0

check_no_carriage_returns() {
    file=$1
    if LC_ALL=C grep -q "$(printf '\r')" "$file"; then
        printf 'FAIL: CR character found in %s\n' "$file" >&2
        status=1
    fi
}

check_policy() {
    file=$1
    attr=$(git check-attr eol -- "$file" | awk -F': ' '{print $3}')
    if [ "$attr" != "lf" ]; then
        printf 'FAIL: %s must have eol=lf (found %s)\n' "$file" "$attr" >&2
        status=1
    fi
    check_no_carriage_returns "$file"
}

if ! git ls-files -z -- '*.sh' '*.bash' | tr '\0' '\n' |
    while IFS= read -r file; do
        [ -n "$file" ] || continue
        check_policy "$file" || exit 1
    done
then
    status=1
fi

# Catch CRLF in any tracked executable/shebang text file, including future
# script extensions that are not covered by the explicit shell patterns.
if ! git grep -Il '^#!' -- . | while IFS= read -r file; do
    check_policy "$file" || exit 1
done
then
    status=1
fi

if [ "$status" -ne 0 ]; then
    exit 1
fi

printf 'Line-ending policy check passed.\n'
