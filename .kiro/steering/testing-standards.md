# Testing Standards

## Test Structure

- Tests mirror the source tree under `test/unit/`
- One test file per rule: `test_<rule_name>.py` (snake_case of the rule class)
- Rule tests are **pytest** style — a fixture plus `@pytest.mark.parametrize`

## Rule Testing Pattern

This is the pattern current rules use. Copy it.

```python
"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.rules.resources.lmbd.FunctionCapacityProviderTimeout import (
    FunctionCapacityProviderTimeout,
)


@pytest.fixture(scope="module")
def rule():
    rule = FunctionCapacityProviderTimeout()
    yield rule


@pytest.mark.parametrize(
    "instance,expected_count,expected_message",
    [
        # Valid: property absent entirely
        ({"Runtime": "python3.13"}, 0, None),
        # Valid: exactly at the boundary
        ({"Timeout": 900}, 0, None),
        # Valid: made legal by a sibling property
        ({"Timeout": 5400, "CapacityProviderConfig": {...}}, 0, None),
        # Valid: wrong type is handled by another rule
        ([], 0, None),
        # Invalid: one past the boundary
        (
            {"Timeout": 901},
            1,
            "901 is greater than the maximum of 900 for functions "
            "without 'CapacityProviderConfig' (Lambda Managed Instances)",
        ),
    ],
)
def test_validate(instance, expected_count, expected_message, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))

    assert len(errs) == expected_count, (
        f"Expected {expected_count} errors got {len(errs)}"
    )
    if expected_message:
        assert errs[0].message == expected_message
```

### The `validator` fixture

`validator` is supplied by `test/unit/conftest.py`. It is built from the `cfn`,
`context`, and `validators` fixtures, which in turn derive from `template`,
`regions` (default `["us-east-1"]`), and `parameters`. Override any of them with
`@pytest.mark.parametrize(..., indirect=True)` when a rule needs a specific
template or region.

`conftest.py` also falls back to the small fixture schema set in
`test/fixtures/schemas/` when the real provider schemas have not been
downloaded. Run `cfn-lint --update-specs` or your results will not reflect
reality.

### Legacy harness

`test/unit/rules/__init__.py` provides `BaseRuleTestCase` with
`helper_file_positive` / `helper_file_negative`, used by older unittest-style
tests that drive whole template files. Do not use it for new rule tests.

## Required Cases

Every rule test must cover all five. The silent cases are the point — see
[`../context/false-positives.md`](../context/false-positives.md).

| Case | Expectation |
|---|---|
| Invalid value | fires, with the exact message |
| Boundary valid value | **silent** |
| Made legal by a sibling property or condition | **silent** |
| Non-scalar / unresolvable (`Ref`, `GetAtt`, `Fn::If`, `[]`) | **silent** |
| Property absent | **silent** |

A rule tested only on its failing case is incomplete, and in review that is a
blocking comment.

## Fixtures

### Inline instances
Preferred for rule tests. A dict literal with only the relevant properties
keeps the expectation obvious.

### Template fixtures
`test/fixtures/templates/`, split into `good/` and `bad/`. Templates under
`good/` must stay clean: a new rule that fires on them is a false positive, not
a fixture problem. Verify with:

```shell
.venv/bin/cfn-lint -t "test/fixtures/templates/good/**/*.yaml"
```

### Snapshot results
Some suites compare against recorded JSON under `test/fixtures/results/`. When
a deliberate change moves them, refresh with
`scripts/update_snapshot_results.sh` and review the diff — do not regenerate to
make a failure disappear.

## Coverage

- Aim for 100% line coverage on new rules
- Cover both branches of every condition in the rule
- CI runs `tox` on Python 3.10–3.15 across Linux, macOS, and Windows

## Running Tests

```shell
.venv/bin/python -m pytest test/unit/rules/resources/<service>/test_<rule>.py
.venv/bin/python -m pytest test/unit/rules/      # all rule tests
.venv/bin/python -m pytest test                  # full suite
.venv/bin/python -m pytest -n auto test          # parallel
```

`pyproject.toml` sets `addopts = ["-m not data"]`, so the slow data-driven
tests are deselected by default. Add `-m data` to include them.
