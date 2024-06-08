"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.context import Path
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.properties.PropertiesTemplated import PropertiesTemplated
from cfnlint.template import Template


@pytest.fixture(scope="module")
def rule():
    rule = PropertiesTemplated()
    yield rule


@pytest.fixture
def path():
    return Path(
        path=deque(["Resources/AWS::CloudFormation::Template/Properties/TemplateURL"])
    )


@pytest.mark.parametrize(
    "name,instance,transforms,expected",
    [
        (
            "A s3 string should be fine",
            "s3://my-bucket/key/value.yaml",
            [],
            [],
        ),
        (
            "An object isn't a string so we skip",
            {"foo": "bar"},
            [],
            [],
        ),
        (
            "A transform will result in non failure",
            "./folder",
            "AWS::Serverless-2016-10-31",
            [],
        ),
        (
            "String with no transform",
            "./folder",
            [],
            [
                ValidationError(
                    ("This code may only work with 'package' cli command"),
                )
            ],
        ),
    ],
)
def test_validate(name, instance, transforms, expected, rule, validator):
    validator = validator.evolve(cfn=Template("", {"Transform": transforms}))

    errs = list(rule.validate(validator, {}, instance, {}))
    assert errs == expected, f"Test {name!r} got {errs!r}"
