#!/bin/sh
# Derive the next semver tag from the latest tag and a conventional commit
# subject. Prints the new tag (e.g. v1.2.0) on stdout, or nothing at all when
# the commit does not warrant a release.
#
#   next-version.sh "<subject>" [<latest-tag>]
#
# Bump rules, per Conventional Commits:
#   `!` before the colon, or a BREAKING CHANGE trailer -> major
#   feat                                               -> minor
#   fix, perf                                          -> patch
#   anything else (docs, ci, chore, refactor, ...)     -> no release
#
# Kept as a script rather than inline YAML so it can be tested directly.
set -eu

subject="${1:?usage: next-version.sh <subject> [latest-tag]}"
latest="${2:-}"

if [ -z "$latest" ]; then
	latest="$(git tag --list 'v*' --sort=-v:refname | head -n1)"
fi
[ -n "$latest" ] || latest="v0.0.0"

# Strip the leading v and any trailing pre-release/build metadata.
core="${latest#v}"
core="${core%%-*}"
major="${core%%.*}"
rest="${core#*.}"
minor="${rest%%.*}"
patch="${rest#*.}"

case "$major$minor$patch" in
*[!0-9]*)
	echo "cannot parse tag '$latest' as vMAJOR.MINOR.PATCH" >&2
	exit 1
	;;
esac

# type(scope)?!?: description  -- capture the type and whether ! is present.
type="$(printf '%s' "$subject" | sed -n 's/^\([a-z][a-z0-9-]*\)\((.*)\)\{0,1\}!\{0,1\}:.*/\1/p')"
breaking=no
case "$subject" in
*'!:'* | *'!):'*) breaking=yes ;;
esac
case "$subject" in
*'BREAKING CHANGE'*) breaking=yes ;;
esac

if [ "$breaking" = yes ]; then
	major=$((major + 1))
	minor=0
	patch=0
else
	case "$type" in
	feat)
		minor=$((minor + 1))
		patch=0
		;;
	fix | perf)
		patch=$((patch + 1))
		;;
	*)
		# Not a releasable change.
		exit 0
		;;
	esac
fi

printf 'v%s.%s.%s\n' "$major" "$minor" "$patch"
