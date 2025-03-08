"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.resources.codepipeline.PipelineActionConfiguration import (
    PipelineActionConfiguration,
)


@pytest.fixture
def rule():
    rule = PipelineActionConfiguration()
    yield rule


def format(validator, keywords, instance, schema):
    if instance:
        return

    yield ValidationError("bad")


@pytest.fixture
def validator(cfn, context):
    validator = CfnTemplateValidator({}).extend(
        validators={
            "format": format,
        }
    )

    return validator(
        context=context,
        cfn=cfn,
        schema={},
    )


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            [],
            [],
        ),
        (
            {
                "Configuration": {
                    "TemplatePath": "Source::template.yaml",
                },
                "InputArtifacts": [{"Name": "Source"}],
            },
            [],
        ),
        (
            {
                "Configuration": {
                    "TemplatePath": "Foo::template.yaml",
                },
                "InputArtifacts": [{"Name": "Bar"}],
            },
            [
                ValidationError(
                    "'Foo' is not one of ['Bar']",
                    rule=PipelineActionConfiguration(),
                    validator="enum",
                    path_override=deque(["Configuration", "TemplatePath"]),
                    schema_path=deque([]),
                )
            ],
        ),
        (
            {
                "Configuration": {
                    "TemplatePath": "Foo::template.yaml",
                },
            },
            [
                ValidationError(
                    "'Foo' is not one of []",
                    rule=PipelineActionConfiguration(),
                    validator="enum",
                    path_override=deque(["Configuration", "TemplatePath"]),
                    schema_path=deque([]),
                )
            ],
        ),
        (
            {
                "Configuration": {
                    "RoleArn": True,
                },
            },
            [],
        ),
        (
            {
                "Configuration": {
                    "RoleArn": False,
                },
            },
            [
                ValidationError(
                    "bad",
                    rule=PipelineActionConfiguration(),
                    validator="format",
                    path_override=deque(["Configuration", "RoleArn"]),
                    schema_path=deque(["format"]),
                )
            ],
        ),
    ],
)
def test_validate(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))
    assert errs == expected, f"Expected {expected} got {errs}"
