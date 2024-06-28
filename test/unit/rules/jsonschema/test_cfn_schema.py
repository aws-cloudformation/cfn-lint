"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from collections import deque

import pytest

from cfnlint.context import Context
from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema

_schema = {
    "type": "object",
    "properties": {
        "a": {
            "type": "string",
        },
        "b": {"type": "object", "properties": {"1": {"type": "string"}}},
        "c": {
            "type": "string",
            "pattern": "^foo$",
        },
    },
}


class _Error(CfnLintJsonSchema):
    id = "EXXXX"
    shortdesc = "Rule to create errors"
    description = "Rule to create errors"

    def __init__(self) -> None:
        super().__init__([], None, True)


class _BestError(CfnLintJsonSchema):
    id = "EXXXX"
    shortdesc = "Rule that returns the best error"
    description = "A longer description"

    def __init__(self) -> None:
        super().__init__([], None, False)


@pytest.mark.parametrize(
    "name,rule,instance,expected_errs",
    [
        (
            "All matches returned",
            _Error(),
            {"a": [], "b": []},
            [
                ValidationError(
                    message="[] is not of type 'string'",
                    rule=_Error(),
                    validator="type",
                    path=deque(["a"]),
                    schema_path=deque(["properties", "a", "type"]),
                ),
                ValidationError(
                    message="[] is not of type 'object'",
                    rule=_Error(),
                    validator="type",
                    path=deque(["b"]),
                    schema_path=deque(["properties", "b", "type"]),
                ),
            ],
        ),
        (
            "Best match",
            _BestError(),
            {"a": [], "b": []},
            [
                ValidationError(
                    message="Rule that returns the best error",
                    validator="type",
                    path=deque(["a"]),
                    rule=_BestError(),
                    schema_path=deque(["properties", "a", "type"]),
                ),
            ],
        ),
        (
            "Validation error with dynamic reference",
            _BestError(),
            {"c": "{{resolve:ssm:/SQS_Queue/SQS_ARN}}"},
            [
                ValidationError(
                    message="Rule that returns the best error",
                    validator="pattern",
                    path=deque(["c"]),
                    rule=_BestError(),
                    schema_path=deque(["properties", "c", "pattern"]),
                ),
            ],
        ),
    ],
)
def test_cfn_schema(name, rule, instance, expected_errs):
    context = Context(regions=["us-east-1"])
    validator = CfnTemplateValidator(schema=_schema, context=context)

    errs = list(rule.validate(validator, {}, instance, _schema))
    assert errs == expected_errs
