#!/usr/bin/env python3
"""Check that action.yml is one GitHub can actually load and run.

v1.0.0 and v1 both once pointed at an action.yml that did not parse, so the
action could not be loaded at all by anyone who referenced them. Parsing alone
is not enough: a file can be valid YAML and still be unusable, so this also
checks the structure GitHub requires.

    validate-action.py [path]        # default: action.yml

Exits non-zero and prints every problem found, rather than only the first.
"""
import sys

import yaml

# Every step in a composite action must say how to run: either it delegates to
# another action (uses:) or it runs a script, which then requires a shell.
COMPOSITE_STEP_KEYS = ("uses", "run")


def problems(path):
    try:
        with open(path) as fh:
            raw = fh.read()
    except OSError as exc:
        return [f"cannot read {path}: {exc}"]

    try:
        doc = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        # The original failure mode: a dedented heredoc ended the block scalar
        # and YAML read the script as a mapping.
        return [f"not valid YAML: {str(exc).splitlines()[0]}"]

    if not isinstance(doc, dict):
        return [f"top level must be a mapping, got {type(doc).__name__}"]

    found = []
    for key in ("name", "description", "runs"):
        if key not in doc:
            found.append(f"missing required top-level key: {key}")

    runs = doc.get("runs")
    if not isinstance(runs, dict):
        if runs is not None:
            found.append("runs: must be a mapping")
        return found

    using = runs.get("using")
    if not using:
        found.append("runs.using is required")
    elif using == "composite":
        steps = runs.get("steps")
        if not isinstance(steps, list) or not steps:
            found.append("composite actions need a non-empty runs.steps list")
        else:
            for i, step in enumerate(steps):
                label = step.get("name", f"#{i}") if isinstance(step, dict) else f"#{i}"
                if not isinstance(step, dict):
                    found.append(f"step {label}: must be a mapping")
                    continue
                if not any(k in step for k in COMPOSITE_STEP_KEYS):
                    found.append(f"step {label}: needs either uses: or run:")
                if "run" in step and not step.get("shell"):
                    # GitHub rejects the whole action, not just this step.
                    found.append(f"step {label}: run: requires shell:")

    # Inputs are optional, but a malformed block breaks the action at load time.
    inputs = doc.get("inputs")
    if inputs is not None and not isinstance(inputs, dict):
        found.append("inputs: must be a mapping")
    elif isinstance(inputs, dict):
        for name, spec in inputs.items():
            if not isinstance(spec, dict):
                found.append(f"input {name}: must be a mapping")
            elif "description" not in spec:
                found.append(f"input {name}: missing description")

    return found


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "action.yml"
    found = problems(path)
    if found:
        print(f"{path} is not a loadable action:", file=sys.stderr)
        for p in found:
            print(f"  - {p}", file=sys.stderr)
        return 1
    print(f"{path} is a loadable action")
    return 0


if __name__ == "__main__":
    sys.exit(main())
