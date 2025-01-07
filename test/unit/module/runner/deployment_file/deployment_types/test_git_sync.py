"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.rules import RuleMatch
from cfnlint.runner.deployment_file.deployment import DeploymentFileData
from cfnlint.runner.deployment_file.deployment_types import (
    create_deployment_from_git_sync,
)


@pytest.mark.parametrize(
    "name, instance, expected",
    [
        (
            "A standard git sync file",
            {
                "template-file-path": "../a/path",
                "parameters": {
                    "Foo": "Bar",
                },
                "tags": {
                    "Key": "Value",
                },
            },
            (
                DeploymentFileData(
                    template_file_path="../a/path",
                    parameters={
                        "Foo": "Bar",
                    },
                    tags={
                        "Key": "Value",
                    },
                ),
                None,
            ),
        ),
        (
            "Bad template-file-path type",
            {
                "template-file-path": ["../a/path"],
                "parameters": {
                    "Foo": "Bar",
                },
                "tags": {
                    "Key": "Value",
                },
            },
            (
                None,
                [
                    RuleMatch(
                        message="['../a/path'] is not of type 'string'",
                        path=["template-file-path"],
                    )
                ],
            ),
        ),
        (
            "No template file path",
            {
                "parameters": {
                    "Foo": "Bar",
                },
                "tags": {
                    "Key": "Value",
                },
            },
            (
                None,
                [
                    RuleMatch(
                        message="'template-file-path' is a required property",
                        path=[],
                    )
                ],
            ),
        ),
        (
            "Bad type on parameters",
            {
                "template-file-path": "../a/path",
                "parameters": ["Foo=Bar"],
                "tags": {
                    "Key": "Value",
                },
            },
            (
                None,
                [
                    RuleMatch(
                        message="['Foo=Bar'] is not of type 'object'",
                        path=["parameters"],
                    )
                ],
            ),
        ),
        (
            "Bad type on tags",
            {
                "template-file-path": "../a/path",
                "parameters": {
                    "Foo": "Bar",
                },
                "tags": ["Foo=Bar"],
            },
            (
                None,
                [
                    RuleMatch(
                        message="['Foo=Bar'] is not of type 'object'",
                        path=["tags"],
                    )
                ],
            ),
        ),
    ],
)
def test_git_sync(name, instance, expected):

    results = create_deployment_from_git_sync(instance)

    assert results == expected, f"{name}: {results} != {expected}"
