"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.context import create_context_for_template
from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.parameters.NoEcho import NoEcho
from cfnlint.template import Template


@pytest.fixture(scope="module")
def rule():
    rule = NoEcho()
    yield rule


@pytest.fixture(scope="module")
def cfn():
    return Template(
        "",
        {
            "Parameters": {
                "Echo": {"Type": "String", "NoEcho": "true"},
                "EchoTrue": {
                    "Type": "String",
                    "NoEcho": True,
                },
                "NoEcho": {"Type": "String", "NoEcho": "false"},
                "MyParameter": {"Type": "String"},
            },
            "Resources": {},
        },
        regions=["us-east-1"],
    )


@pytest.fixture(scope="module")
def context(cfn):
    return create_context_for_template(cfn)


@pytest.mark.parametrize(
    "name,instance,path,expected",
    [
        (
            "An Invalid Ref",
            {"Ref": []},
            deque(["Metadata"]),
            [],
        ),
        (
            "A ref to something that isn't a parameter",
            {"Ref": "AWS::Region"},
            deque(["Metadata"]),
            [],
        ),
        (
            "Using NoEcho in Resources Properties",
            {"Ref": "Echo"},
            deque(["Resources", "MyResource", "Properties", "Name"]),
            [],
        ),
        (
            "Using NoEcho in Resource Metadata",
            {"Ref": "Echo"},
            deque(["Resources", "MyResource", "Metadata"]),
            [
                ValidationError(
                    "Don't use 'NoEcho' parameter 'Echo' in resource metadata",
                    rule=NoEcho(),
                    path=deque(["Ref"]),
                )
            ],
        ),
        (
            "Using NoEcho in Metadata",
            {"Ref": "Echo"},
            deque(["Metadata"]),
            [
                ValidationError(
                    "Don't use 'NoEcho' parameter 'Echo' in 'Metadata'",
                    rule=NoEcho(),
                    path=deque(["Ref"]),
                )
            ],
        ),
        (
            "Using NoEcho in Metadata",
            {"Ref": "EchoTrue"},
            deque(["Metadata"]),
            [
                ValidationError(
                    "Don't use 'NoEcho' parameter 'EchoTrue' in 'Metadata'",
                    rule=NoEcho(),
                    path=deque(["Ref"]),
                )
            ],
        ),
        (
            "Using Non NoEcho in Metadata",
            {"Ref": "NoEcho"},
            deque(["Metadata"]),
            [],
        ),
        (
            "Using a parameter in Metadata",
            {"Ref": "MyParameter"},
            deque(["Metadata"]),
            [],
        ),
        (
            "Using NoEcho in Outputs",
            {"Ref": "Echo"},
            deque(["Outputs", "Name", "Value"]),
            [
                ValidationError(
                    "Don't use 'NoEcho' parameter 'Echo' in 'Outputs'",
                    rule=NoEcho(),
                    path=deque(["Ref"]),
                )
            ],
        ),
    ],
)
def test_validate(name, instance, path, expected, rule, context, cfn):
    for p in path:
        context = context.evolve(path=p)
    validator = CfnTemplateValidator(context=context, cfn=cfn)
    errs = list(rule.validate(validator, {}, instance, {}))
    assert errs == expected, f"Test {name!r} got {errs!r}"
