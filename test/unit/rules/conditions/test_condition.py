"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.context import Path, create_context_for_template
from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.conditions.Condition import Condition
from cfnlint.template import Template


@pytest.fixture(scope="module")
def rule():
    rule = Condition()
    yield rule


@pytest.fixture(scope="module")
def validator():
    cfn = Template(
        "",
        {
            "Conditions": {
                "IsUsEast1": {"Fn::Equals": [{"Ref": "AWS::Region"}, "us-east-1"]}
            },
        },
    )
    context = create_context_for_template(cfn).evolve(
        functions=[],
        path=Path(path=deque(["Resources", "MyRdsDbInstance", "Properties"])),
    )
    yield CfnTemplateValidator(schema={}, context=context, cfn=cfn)


@pytest.mark.parametrize(
    "name,instance,errors",
    [
        ("Valid with string", {"Condition": "IsUsEast1"}, []),
        (
            "Invalid Type",
            {"Condition": []},
            [
                ValidationError(
                    "[] is not of type 'string'",
                    validator="condition",
                    schema_path=deque(["type"]),
                    path=deque(["Condition"]),
                ),
                ValidationError(
                    "[] is not one of ['IsUsEast1']",
                    validator="condition",
                    schema_path=deque(["enum"]),
                    path=deque(["Condition"]),
                ),
            ],
        ),
        (
            "Non existent condition",
            {"Condition": "IsUsWest2"},
            [
                ValidationError(
                    "'IsUsWest2' is not one of ['IsUsEast1']",
                    validator="condition",
                    schema_path=deque(["enum"]),
                    path=deque(["Condition"]),
                )
            ],
        ),
    ],
)
def test_condition(name, instance, errors, rule, validator):
    errs = list(rule.validate(validator, {}, instance, {}))

    assert errs == errors, name
