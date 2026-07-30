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
  contents: read
jobs:
  commitlint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@<full-sha>  # required for commits-mode
      - uses: DivergentCodes/commitlint-action@<full-sha>  # v1.0.1
        with:
          pr-title-mode: block   # squash-merge title is load-bearing
          commits-mode: warn     # advisory; intermediate commits vanish at squash
```

`actions/checkout` is required whenever `commits-mode` is not `off`, because
the action reads the PR's commits from git. With `commits-mode: off` the title
comes from the event payload and no checkout is needed.

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
| `version` | `latest` | commitlint version to `go install`; pin a tag (e.g. `v1.1.2`) in production |
| `pr-title-mode` | `block` | `block` fails the check, `warn` reports only, `off` skips |
| `commits-mode` | `warn` | same modes, applied to each PR commit |
| `types` | conventional set | comma-separated allowed types |
| `scopes` | any | comma-separated allowed scopes |
| `require-scope` | `false` | require a `(scope)` |
| `max-subject-length` | `72` | subject length limit |
| `github-token` | `github.token` | fetches the commitlint module while its repo is private; unused once public |

## Permissions

`permissions: contents: read` is sufficient — enough for `actions/checkout`
to fetch the commits. The action makes no API calls and never writes anything.
With `commits-mode: off` it reads only the event payload.

The action installs the linter with a public `go install` first. If the
`commitlint` repository is public, that path is used and the module proxy's
**checksum-database verification applies** — nothing else is needed.

If that fetch fails, the repository is private and credentials are required.
The action then rewrites only `github.com/DivergentCodes/` URLs to carry
`github-token`, so the token is never offered to another host or org, and sets
`GOPRIVATE` for the retry. `GOPRIVATE` bypasses the proxy and checksum
database — unavoidable for a private module, which is why it is scoped to the
fallback rather than applied unconditionally. Pass a token that can read the
repo:

```yaml
      - uses: DivergentCodes/commitlint-action@<full-sha>
        with:
          github-token: ${{ secrets.COMMITLINT_READ_TOKEN }}
```

Once `commitlint` is public this is unnecessary and the default applies.

## Using this in another DivergentCodes repository

Both repositories are private, which needs two one-time settings. Neither has
to be made public.

**1. Let other org repos use this action.** Private actions are not callable
across repositories by default. In **this** repo: Settings → Actions → General
→ Access → *Accessible from repositories in the DivergentCodes organization*.
Without it, consuming workflows fail before the action runs.

**2. Provide a token that can read `DivergentCodes/commitlint`.** The default
`github.token` is scoped to the repository running the workflow, so it cannot
read a *different* private repo. Create a fine-grained PAT (or GitHub App
token) with **Contents: read** on `DivergentCodes/commitlint` only, and add it
as an organization secret named `COMMITLINT_READ_TOKEN`.

Then, in the consuming repository:

```yaml
name: pr-lint
on:
  pull_request:
    types: [opened, edited, synchronize, reopened]
permissions:
  contents: read
jobs:
  commitlint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@<full-sha>
      - uses: DivergentCodes/commitlint-action@<full-sha>  # v1.0.1
        with:
          github-token: ${{ secrets.COMMITLINT_READ_TOKEN }}
          pr-title-mode: block
          commits-mode: warn
```

If `commitlint` later becomes public, drop the `github-token` line and delete
the secret; nothing else changes.

### Troubleshooting org setup

- **`terminal prompts disabled`** during *Install commitlint* → the token is
  missing, expired, or lacks Contents: read on `DivergentCodes/commitlint`.
- **The workflow fails before any step runs**, with a message about the
  action not being found → step 1 above has not been applied.
- **`could not read Username`** with a token set → the secret is defined in
  the wrong scope; organization secrets must be made visible to the consuming
  repository.

## Runner requirements

Runs on `ubuntu-latest` (and other GitHub-hosted runners) out of the box: it
uses `actions/setup-go` to install the linter and reads commits with `git`. On
**self-hosted runners**, ensure Go and `git` are available.

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

## License

[MIT](LICENSE)
