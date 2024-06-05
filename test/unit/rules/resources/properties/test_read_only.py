"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.context import Path
from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.resources.properties.ReadOnly import ReadOnly


@pytest.fixture(scope="module")
def rule():
    yield ReadOnly()


@pytest.fixture(scope="module")
def validator():
    yield CfnTemplateValidator(
        schema={
            "properties": {"Id": {"type": "string"}},
            "type": "object",
            "readOnlyProperties": ["/properties/Id"],
            "typeName": "Test",
        }
    )


@pytest.mark.parametrize(
    "name,path,expected",
    [
        (
            "Not using read only property",
            deque(["Resources", "Test", "Properties", "Name"]),
            [],
        ),
        (
            "Not in outputs",
            deque(["Outputs"]),
            [],
        ),
        (
            "Not in resource properties",
            deque(["Resources"]),
            [],
        ),
        (
            "Not in resource properties",
            deque(["Resources", "*", "Metadata"]),
            [],
        ),
        (
            "Setting a read only property",
            deque(["Resources", "Test", "Properties", "Id"]),
            [ValidationError("Read only properties are not allowed ('Id')")],
        ),
    ],
)
def test_validate(name, path, expected, rule, validator):
    validator = validator.evolve(
        context=validator.context.evolve(
            path=Path(
                cfn_path=path,
            )
        ),
    )

    errs = list(rule.validate(validator, "", "", {}))

    assert errs == expected, f"{name} got errors {errs!r}"
