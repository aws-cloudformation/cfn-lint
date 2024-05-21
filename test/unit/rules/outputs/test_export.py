"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.jsonschema import CfnTemplateValidator
from cfnlint.rules.functions.GetAz import GetAz
from cfnlint.rules.functions.Ref import Ref
from cfnlint.rules.outputs.Export import Export


@pytest.fixture(scope="module")
def rule():
    rule = Export()
    yield rule


@pytest.fixture(scope="module")
def validator():
    yield CfnTemplateValidator(schema={}).extend(
        validators={
            "fn_getazs": GetAz().fn_getazs,
            "ref": Ref().ref,
        }
    )(schema={})


@pytest.mark.parametrize(
    "name,instance,errors",
    [
        ("Valid with string", "foo", []),
        ("Invalid with an array", ["foo"], ["['foo'] is not of type 'string'"]),
        (
            "Invalid with a function that returns an array",
            {"Fn::GetAZs": ""},
            ["{'Fn::GetAZs': ''} is not of type 'string'"],
        ),
        (
            "Valid with a function that returns a string",
            {"Ref": "AWS::Region"},
            [],
        ),
    ],
)
def test_functions(name, instance, errors, rule, validator):
    errs = list(rule.validate(validator, {}, instance, {}))
    assert len(errs) == len(errors), name
    for i, err in enumerate(errors):
        assert err == errs[i].message
