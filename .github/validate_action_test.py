#!/usr/bin/env python3
"""Tests for validate-action.py.

A guardrail that cannot fail is not a guardrail, so every case here asserts
the direction it should resolve in — including the exact file that shipped as
v1.0.0 and could not be loaded.

    python3 .github/validate_action_test.py
"""
import importlib.util
import pathlib
import sys
import tempfile

HERE = pathlib.Path(__file__).parent
spec = importlib.util.spec_from_file_location("va", HERE / "validate-action.py")
va = importlib.util.module_from_spec(spec)
spec.loader.exec_module(va)

VALID = """\
name: x
description: y
runs:
  using: composite
  steps:
    - run: echo hi
      shell: bash
"""

# Each case is (label, content, must_be_rejected).
CASES = [
    ("valid minimal", VALID, False),
    (
        "valid with uses: step",
        "name: x\ndescription: y\nruns:\n  using: composite\n  steps:\n    - uses: actions/checkout@v4\n",
        False,
    ),
    # The v1.0.0 failure: a dedented script ended the block scalar.
    (
        "script dedented out of block scalar",
        "name: x\ndescription: y\nruns:\n  using: composite\n  steps:\n    - run: |\n        python3 -c 'import sys\nif True: pass\n'\n      shell: bash\n",
        True,
    ),
    ("missing runs", "name: x\ndescription: y\n", True),
    ("missing name", "description: y\n" + VALID.split("\n", 1)[1], True),
    (
        "run without shell",
        "name: x\ndescription: y\nruns:\n  using: composite\n  steps:\n    - run: echo hi\n",
        True,
    ),
    (
        "empty steps",
        "name: x\ndescription: y\nruns:\n  using: composite\n  steps: []\n",
        True,
    ),
    (
        "step with neither uses nor run",
        "name: x\ndescription: y\nruns:\n  using: composite\n  steps:\n    - name: nothing\n",
        True,
    ),
    (
        "runs without using",
        "name: x\ndescription: y\nruns:\n  steps: []\n",
        True,
    ),
    (
        "input missing description",
        "name: x\ndescription: y\ninputs:\n  foo:\n    default: '1'\n"
        + VALID.split("description: y\n", 1)[1],
        True,
    ),
    ("not a mapping", "- just\n- a list\n", True),
]


def main():
    failures = 0
    for label, content, must_reject in CASES:
        with tempfile.NamedTemporaryFile("w", suffix=".yml", delete=False) as fh:
            fh.write(content)
            path = fh.name
        found = va.problems(path)
        rejected = bool(found)
        if rejected != must_reject:
            failures += 1
            want = "rejected" if must_reject else "accepted"
            print(f"FAIL {label}: expected {want}, got {found or 'accepted'}")
        else:
            detail = f" ({found[0]})" if found else ""
            print(f"ok   {label}{detail}")

    # A missing file is a failure, not a crash.
    if not va.problems("/nonexistent/action.yml"):
        failures += 1
        print("FAIL missing file should be reported")
    else:
        print("ok   missing file reported")

    print(f"\n{len(CASES) + 1} cases, {failures} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
