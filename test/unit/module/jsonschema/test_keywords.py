"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError, _keywords
from cfnlint.jsonschema.validators import CfnTemplateValidator
from cfnlint.rules import CloudFormationLintRule


class Error(CloudFormationLintRule):
    id = "E1111"

    def validate(self, validator, s, instance, schema):
        if s:
            yield ValidationError(
                "Error",
                rule=self,
            )


class Warning(CloudFormationLintRule):
    id = "W1111"

    def validate(self, validator, s, instance, schema):
        yield ValidationError(
            "Warning",
            rule=self,
        )


@pytest.fixture
def validator():
    validator = CfnTemplateValidator(schema={})
    validator = validator.extend(
        validators={
            "error": Error().validate,
            "warning": Warning().validate,
        }
    )
    return validator({})


@pytest.mark.parametrize(
    "name,instance,schema,expected",
    [
        (
            "Valid anyOf",
            "foo",
            [{"const": "foo"}, {"const": "bar"}],
            [],
        ),
        (
            "Valid anyOf with error rule",
            "foo",
            [{"const": "foo"}, {"error": True}],
            [],
        ),
        (
            "Invalid anyOf with error rule",
            "foo",
            [{"error": True}, {"error": True}],
            [
                ValidationError(
                    "'foo' is not valid under any of the given schemas",
                    path=deque([]),
                    schema_path=deque([]),
                    context=[
                        ValidationError(
                            "Error",
                            rule=Error(),
                            path=deque([]),
                            validator="error",
                            schema_path=deque([0, "error"]),
                        ),
                        ValidationError(
                            "Error",
                            rule=Error(),
                            path=deque([]),
                            validator="error",
                            schema_path=deque([1, "error"]),
                        ),
                    ],
                ),
            ],
        ),
        (
            "Valid anyOf with a warning validation error",
            "foo",
            [{"warning": True, "error": True}, {"error": True}],
            [
                ValidationError(
                    "'foo' is not valid under any of the given schemas",
                    path=deque([]),
                    schema_path=deque([]),
                    context=[
                        ValidationError(
                            "Error",
                            rule=Error(),
                            path=deque([]),
                            validator="error",
                            schema_path=deque([0, "error"]),
                        ),
                        ValidationError(
                            "Error",
                            rule=Error(),
                            path=deque([]),
                            validator="error",
                            schema_path=deque([1, "error"]),
                        ),
                        ValidationError(
                            "Warning",
                            rule=Warning(),
                            path=deque([]),
                            validator="warning",
                            schema_path=deque([0, "warning"]),
                        ),
                    ],
                ),
            ],
        ),
        (
            "Valid anyOf without a warning validation error",
            "foo",
            [{"error": True}, {"warning": True}],
            [],
        ),
    ],
)
def test_anyof(name, instance, schema, validator, expected):
    errs = list(_keywords.anyOf(validator, schema, instance, schema))
    assert errs == expected, f"{name!r} got errors {errs!r}"
