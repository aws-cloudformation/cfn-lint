"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque
from unittest import mock

import pytest

from cfnlint.context import Path
from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.resources.properties.ReadOnly import ReadOnly
from cfnlint.schema.resolver import RefResolutionError


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
    "name,path,side_effect,expected",
    [
        (
            "Not using read only property",
            deque(["Resources", "Test", "Properties", "Name"]),
            None,
            [],
        ),
        (
            "Not in outputs",
            deque(["Outputs"]),
            None,
            [],
        ),
        (
            "Not in resource properties",
            deque(["Resources"]),
            None,
            [],
        ),
        (
            "Not in resource properties",
            deque(["Resources", "*", "Metadata"]),
            None,
            [],
        ),
        (
            "Setting a read only property",
            deque(["Resources", "Test", "Properties", "Id"]),
            None,
            [ValidationError("Read only properties are not allowed ('Id')")],
        ),
        (
            "No readonlyProperties in schema",
            deque(["Resources", "Test", "Properties", "Id"]),
            RefResolutionError("not found"),
            [],
        ),
    ],
)
def test_validate(name, path, side_effect, expected, rule, validator):
    validator = validator.evolve(
        context=validator.context.evolve(
            path=Path(
                cfn_path=path,
            )
        ),
    )

    if side_effect:
        validator.resolver = mock.MagicMock()
        validator.resolver.resolve_from_url.side_effect = side_effect

    errs = list(rule.validate(validator, "", "", {}))

    assert errs == expected, f"{name} got errors {errs!r}"
