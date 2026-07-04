# commitlint-action

GitHub Action wrapping [DivergentCodes/commitlint](https://github.com/DivergentCodes/commitlint):
Conventional Commits linting for PR titles and commit messages with **no
third-party actions** — the only `uses:` inside are GitHub's own
(`actions/setup-go`), and the linter is a zero-dependency Go binary
installed from source, pinnable by tag.

## Usage

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
      - uses: DivergentCodes/commitlint-action@v1
        with:
          pr-title-mode: block   # squash-merge title is load-bearing
          commits-mode: warn     # advisory; intermediate commits vanish at squash
```

## Inputs

| Input | Default | Meaning |
|---|---|---|
| `version` | `latest` | commitlint version to `go install` (pin a tag in production) |
| `pr-title-mode` | `block` | `block` fails the check, `warn` reports only, `off` skips |
| `commits-mode` | `warn` | same modes, applied to each PR commit |
| `types` | conventional set | comma-separated allowed types |
| `scopes` | any | comma-separated allowed scopes |
| `require-scope` | `false` | require a `(scope)` |
| `max-subject-length` | `72` | subject length limit |
| `github-token` | `github.token` | used to read PR commits |
