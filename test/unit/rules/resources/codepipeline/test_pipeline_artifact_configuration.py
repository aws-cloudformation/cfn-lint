"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.codepipeline.PipelineActionConfiguration import (
    PipelineActionConfiguration,
)


@pytest.fixture
def rule():
    rule = PipelineActionConfiguration()
    yield rule


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
    ],
)
def test_validate(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))
    assert errs == expected, f"Expected {expected} got {errs}"
