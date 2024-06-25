"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque
from typing import Any

import pytest

from cfnlint.jsonschema._resolvers_cfn import ResolutionResult, Validator
from cfnlint.jsonschema.exceptions import ValidationError
from cfnlint.jsonschema.validators import CfnTemplateValidator


def _resolver(validator: Validator, instance: Any) -> ResolutionResult:
    if instance == "fail":
        yield None, validator, ValidationError("Foo")
        return

    yield "foo", validator, None


@pytest.fixture
def validator():
    validator = CfnTemplateValidator({})
    validator.fn_resolvers = {
        "Ref": _resolver,
    }
    validator.context = validator.context.evolve(functions=["Ref"])
    return validator


@pytest.mark.parametrize(
    "name,instance,expected",
    [
        (
            "Valid with function",
            {"Ref": "fail"},
            [(None, ValidationError("Foo", path=deque(["Ref"])))],
        ),
        ("Valid string", "foo", [("foo", None)]),
        ("Valid with function", {"Ref": "pass"}, [("foo", None)]),
    ],
)
def test_validator_resolver(name, instance, expected, validator):
    results = list(validator.resolve_value(instance))

    if len(results) > len(expected):
        for result, expected_result in zip(results, expected):
            assert result[0] == expected_result[0]
            assert result[2] == expected_result[1]
    else:
        for expected_result, result in zip(expected, results):
            assert result[0] == expected_result[0]
            assert result[2] == expected_result[1]
