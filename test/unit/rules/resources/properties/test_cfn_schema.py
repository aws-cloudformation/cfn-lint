"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import pytest

from cfnlint.context import Context
from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.resources.properties.CfnSchema import BaseCfnSchema

_schema = {
    "type": "object",
    "properties": {
        "a": {
            "type": "string",
        },
        "b": {"type": "object", "properties": {"1": {"type": "string"}}},
    },
}


class _Error(BaseCfnSchema):
    id = "EXXXX"
    shortdesc = "Rule to create errors"
    description = "Rule to create errors"
    all_matches = True

    def __init__(self) -> None:
        super().__init__()
        self.cfn_schema = _schema


class _BestError(BaseCfnSchema):
    id = "EXXXX"
    shortdesc = "Rule that returns the best error"
    description = "A longer description"

    def __init__(self) -> None:
        super().__init__()
        self.cfn_schema = _schema


@pytest.mark.parametrize(
    "name,rule,instance,expected_errs",
    [
        (
            "All matches returned",
            _Error(),
            {"a": [], "b": []},
            [
                ValidationError("[] is not of type 'string'"),
                ValidationError("[] is not of type 'object'"),
            ],
        ),
        (
            "Best match",
            _BestError(),
            {"a": [], "b": []},
            [
                ValidationError(_BestError.shortdesc),
            ],
        ),
    ],
)
def test_cfn_schema(name, rule, instance, expected_errs):
    context = Context("us-east-1")
    validator = CfnTemplateValidator(schema=_schema, context=context)

    errs = list(rule.validate(validator, instance))
    for i, expected_err in enumerate(expected_errs):
        assert errs[i].message == expected_err.message, name
