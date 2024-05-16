"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.context import Context, Path
from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.outputs.ImportValue import ImportValue


@pytest.fixture(scope="module")
def rule():
    rule = ImportValue()
    yield rule


@pytest.fixture(scope="module")
def validator():
    context = Context(
        regions=["us-east-1"],
        resources={},
        parameters={},
    )
    yield CfnTemplateValidator(context=context)


@pytest.mark.parametrize(
    "name,instance,path,schema,expected",
    [
        (
            "Valid Fn::ImportValue",
            {"Fn::ImportValue": "Export"},
            deque(["Resources", "MyResource", "Properties", "BucketName"]),
            {"type": "string"},
            [],
        ),
        (
            "Short path",
            {"Fn::ImportValue": "Export"},
            deque(["Outputs"]),
            {"type": "object"},
            [],
        ),
        (
            "Invalid Fn::ImportValue in Output",
            {"Fn::ImportValue": "Export"},
            deque(["Outputs", "MyOutput", "Value"]),
            {"type": "string"},
            [
                ValidationError(
                    (
                        "The output value {'Fn::ImportValue': 'Export'} "
                        "is an import from another output"
                    ),
                    path=deque(["Fn::ImportValue"]),
                    rule=ImportValue(),
                )
            ],
        ),
    ],
)
def test_validate(name, instance, path, schema, expected, rule, validator):
    context = validator.context.evolve(path=Path(path=path))
    validator = validator.evolve(context=context)
    errs = list(rule.validate(validator, schema, instance, {}))
    assert errs == expected, f"Test {name!r} got {errs!r}"
