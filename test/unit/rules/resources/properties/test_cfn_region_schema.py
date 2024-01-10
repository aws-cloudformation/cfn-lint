"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import pytest

from cfnlint.context import Context
from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.resources.properties.CfnRegionSchema import BaseCfnRegionSchema

_schema = {"us-east-1": {"enum": ["foo"]}, "us-west-2": {"enum": ["bar"]}}


class _Error(BaseCfnRegionSchema):
    id = "EXXXX"
    shortdesc = "Rule to create errors"
    description = "Rule to create errors"
    all_matches = True

    def __init__(self) -> None:
        super().__init__()
        self.cfn_schema = _schema


@pytest.mark.parametrize(
    "name,rule,instance,regions,expected_errs",
    [
        (
            "No errors found",
            _Error(),
            "foo",
            ["us-east-1"],
            [],
        ),
        (
            "All matches returned",
            _Error(),
            "bar",
            ["us-east-1"],
            [
                ValidationError("'bar' is not one of ['foo'] in us-east-1"),
            ],
        ),
    ],
)
def test_cfn_region_schema(name, rule, instance, regions, expected_errs):
    context = Context(regions)
    validator = CfnTemplateValidator(schema=_schema, context=context)

    errs = list(rule.validate(validator, instance, regions))
    assert len(errs) == len(expected_errs), name
    for i, expected_err in enumerate(expected_errs):
        assert errs[i].message == expected_err.message, name
