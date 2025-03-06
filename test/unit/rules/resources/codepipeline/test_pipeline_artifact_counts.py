"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.codepipeline.PipelineArtifactCounts import (
    PipelineArtifactCounts,
)


@pytest.fixture
def rule():
    rule = PipelineArtifactCounts()
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
                "Name": "Github",
                "ActionTypeId": {
                    "Category": "Source",
                    "Owner": "ThirdParty",
                    "Provider": "GitHub",
                    "Version": "1",
                },
                "OutputArtifacts": [{"Name": "MyApp"}],
            },
            [],
        ),
        (
            {
                "Name": "Github",
                "ActionTypeId": {
                    "Category": "FOO",
                    "Owner": "FOO",
                    "Provider": "FOO",
                    "Version": "1",
                },
            },
            [],
        ),
        (
            {
                "Name": "Github",
                "ActionTypeId": {
                    "Category": "FOO",
                    "Owner": "AWS",
                    "Provider": "FOO",
                    "Version": "1",
                },
            },
            [],
        ),
        (
            {
                "Name": "Github",
                "ActionTypeId": {
                    "Category": "Deploy",
                    "Owner": "AWS",
                    "Provider": "FOO",
                    "Version": "1",
                },
            },
            [],
        ),
        (
            {
                "Name": "Github",
                "ActionTypeId": {
                    "Category": "Source",
                    "Owner": "ThirdParty",
                    "Provider": "GitHub",
                    "Version": "1",
                },
                "OutputArtifacts": [{"Name": "Foo"}, {"Name": "Bar"}],
            },
            [
                ValidationError(
                    (
                        "expected maximum item count: 1, found: 2 "
                        "when using {'Owner': 'ThirdParty', "
                        "'Category': 'Source', 'Provider': 'GitHub'}"
                    ),
                    rule=PipelineArtifactCounts(),
                    validator="maxItems",
                    path=deque(["OutputArtifacts"]),
                    schema_path=deque(["properties", "OutputArtifacts", "maxItems"]),
                )
            ],
        ),
        (
            {
                "Name": "Github",
                "ActionTypeId": {
                    "Category": "Build",
                    "Owner": "AWS",
                    "Provider": "CodeBuild",
                    "Version": "1",
                },
            },
            [
                ValidationError(
                    (
                        "'InputArtifacts' is a required "
                        "property when using {'Owner': 'AWS', "
                        "'Category': 'Build', 'Provider': 'CodeBuild'}"
                    ),
                    rule=PipelineArtifactCounts(),
                    validator="required",
                    path=deque([]),
                    schema_path=deque(["required"]),
                )
            ],
        ),
        (
            {
                "Name": "Github",
                "ActionTypeId": {
                    "Category": "Deploy",
                    "Owner": "AWS",
                    "Provider": "S3",
                    "Version": "1",
                },
                "OutputArtifacts": [{"Name": "Foo"}, {"Name": "Bar"}],
                "InputArtifacts": [{"Name": "Foo"}, {"Name": "Bar"}],
            },
            [
                ValidationError(
                    (
                        "expected maximum item count: 1, found: 2 when "
                        "using {'Owner': 'AWS', 'Category': "
                        "'Deploy', 'Provider': 'S3'}"
                    ),
                    rule=PipelineArtifactCounts(),
                    validator="maxItems",
                    path=deque(["InputArtifacts"]),
                    schema_path=deque(["properties", "InputArtifacts", "maxItems"]),
                ),
                ValidationError(
                    (
                        "expected maximum item count: 0, found: 2 "
                        "when using {'Owner': 'AWS', 'Category': "
                        "'Deploy', 'Provider': 'S3'}"
                    ),
                    rule=PipelineArtifactCounts(),
                    validator="maxItems",
                    path=deque(["OutputArtifacts"]),
                    schema_path=deque(["properties", "OutputArtifacts", "maxItems"]),
                ),
            ],
        ),
    ],
)
def test_validate(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))

    assert errs == expected, f"Expected {expected} got {errs}"
