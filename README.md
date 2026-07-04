# commitlint-action

GitHub Action wrapping [DivergentCodes/commitlint](https://github.com/DivergentCodes/commitlint):
Conventional Commits linting for PR titles and commit messages with **no
third-party actions** — the only nested `uses:` is GitHub's own
`actions/setup-go`, and the linter is a zero-dependency Go binary installed
from source.

## Usage

Pin to a **full commit SHA** (with a version comment) — the strongest
supply-chain posture, since a moved or compromised tag can't silently swap
the action:

```yaml
name: pr-lint
on:
  pull_request:
    types: [opened, edited, synchronize, reopened]
permissions:
  pull-requests: read
jobs:
  commitlint:
    runs-on: ubuntu-latest
    steps:
      - uses: DivergentCodes/commitlint-action@<full-sha>  # v1.0.0
        with:
          pr-title-mode: block   # squash-merge title is load-bearing
          commits-mode: warn     # advisory; intermediate commits vanish at squash
```

Tag pinning (`@v1`) also works and is fine for internal repos, but SHA
pinning is recommended for anything security-sensitive.

The `edited` trigger matters: it re-runs the check when a PR title is fixed,
so a failed title clears without pushing a commit.

## Why these defaults

When PRs are **squash-merged**, the PR title becomes the commit message on
`main` — so the title is load-bearing (it drives semantic-release versioning)
and is linted in `block` mode. The individual commits inside the PR are
discarded at squash, so they're linted in `warn` mode: contributors get
feedback without being blocked on work-in-progress commit messages. If you
merge with rebase or merge commits instead, set `commits-mode: block`.

## Inputs

| Input | Default | Meaning |
|---|---|---|
| `version` | `latest` | commitlint version to `go install`; pin a tag (e.g. `v1.0.0`) in production |
| `pr-title-mode` | `block` | `block` fails the check, `warn` reports only, `off` skips |
| `commits-mode` | `warn` | same modes, applied to each PR commit |
| `types` | conventional set | comma-separated allowed types |
| `scopes` | any | comma-separated allowed scopes |
| `require-scope` | `false` | require a `(scope)` |
| `max-subject-length` | `72` | subject length limit |
| `github-token` | `github.token` | reads PR commits via the API |

## Permissions

`permissions: pull-requests: read` is sufficient — the action reads the PR
title from the event payload and PR commits via the API with the default
`github.token`. It does not need `contents` access and never writes anything.

## Runner requirements

Runs on `ubuntu-latest` (and other GitHub-hosted runners) out of the box: it
uses `actions/setup-go` for the linter and `python3` + `base64` (both
preinstalled on hosted runners) to decode commit messages from the API. On
**self-hosted runners**, ensure Go, `python3`, and `base64` are available.

## Troubleshooting

- **"subject must be `type(scope)?: description`"** on a PR title → edit the
  title to a conventional form (e.g. `feat: ...`, `fix(api): ...`); the
  `edited` trigger re-runs the check automatically.
- **PR commits failing unexpectedly** → they're linted in `warn` mode by
  default (non-blocking). If they block, `commits-mode` is set to `block`.
- **Type rejected** → it's not in the allowed set; pass `types:` to extend it.

## Releases

Published as **GitHub tagged releases** with changelogs in the release notes.
Reference a release by SHA (preferred) or tag; there is no committed
changelog file.
