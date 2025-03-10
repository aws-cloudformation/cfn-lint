"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque
from typing import Iterable

import pytest

from cfnlint.context import Path
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.codepipeline.PipelineArtifactNames import (
    PipelineArtifactNames,
)


@pytest.fixture
def rule():
    rule = PipelineArtifactNames()
    yield rule


@pytest.fixture
def template():
    return {
        "Conditions": {
            "IsUsEast1": {"Fn::Equals": [{"Ref": "AWS::Region"}, "us-east-1"]},
            "IsUsEast2": {"Fn::Equals": [{"Ref": "AWS::Region"}, "us-east-2"]},
            "IsUsEast": {
                "Fn::Or": [
                    {"Condition": "IsUsEast1"},
                    {"Condition": "IsUsEast2"},
                ]
            },
        }
    }


_standard_path = deque(["Resources", "TestPipeline", "Properties", "Stages"])


def _append_queues(queue1: Iterable, queue2: Iterable) -> deque:
    new_queue: deque = deque()
    new_queue.extend(queue1)
    new_queue.extend(queue2)
    return new_queue


@pytest.mark.parametrize(
    "instances,expected",
    [
        (
            [
                (
                    [],
                    _append_queues(
                        _standard_path, [0, "Actions", 0, "OutputArtifacts", 0, "Name"]
                    ),
                    {},
                ),
                (
                    [],
                    _standard_path,
                    {},
                ),
            ],
            [],
        ),
        (
            [
                (
                    "Foo",
                    _append_queues(
                        _standard_path, [0, "Actions", 0, "OutputArtifacts", 0, "Name"]
                    ),
                    {},
                ),
                (
                    "Bar",
                    _append_queues(
                        _standard_path, [0, "Actions", 0, "OutputArtifacts", 1, "Name"]
                    ),
                    {},
                ),
                (
                    "Foo",
                    _append_queues(
                        _standard_path, [0, "Actions", 1, "InputArtifacts", 0, "Name"]
                    ),
                    {},
                ),
                (
                    "Bar",
                    _append_queues(
                        _standard_path, [0, "Actions", 1, "InputArtifacts", 1, "Name"]
                    ),
                    {},
                ),
            ],
            [],
        ),
        (
            [
                (
                    "Foo",
                    _append_queues(
                        _standard_path, [0, "Actions", 0, "OutputArtifacts", 0, "Name"]
                    ),
                    {},
                ),
                (
                    "Foo",
                    deque(
                        [
                            "Resources",
                            1,
                            "Properties",
                            "Stages",
                            0,
                            "Actions",
                            0,
                            "OutputArtifacts",
                            0,
                            "Name",
                        ]
                    ),
                    {},
                ),
            ],
            [],
        ),
        (
            [
                (
                    "Foo",
                    _append_queues(
                        _standard_path, [0, "Actions", 0, "OutputArtifacts", 0, "Name"]
                    ),
                    {},
                ),
                (
                    "Foo",
                    deque(
                        [
                            "Resources",
                            "AnotherPipeline",
                            "Properties",
                            "Stages",
                            0,
                            "Actions",
                            0,
                            "OutputArtifacts",
                            0,
                            "Name",
                        ]
                    ),
                    {},
                ),
            ],
            [],
        ),
        (
            [
                (
                    "Foo",
                    _append_queues(
                        _standard_path, [0, "Actions", 0, "OutputArtifacts", 0, "Name"]
                    ),
                    {},
                ),
                (
                    "Foo",
                    _append_queues(
                        _standard_path, [0, "Actions", 0, "OutputArtifacts", 1, "Name"]
                    ),
                    {},
                ),
            ],
            [
                ValidationError(
                    "'Foo' is already a defined 'OutputArtifact' Name",
                    rule=PipelineArtifactNames(),
                )
            ],
        ),
        (
            [
                (
                    "Foo",
                    _append_queues(
                        _standard_path, [0, "Actions", 0, "OutputArtifacts", 0, "Name"]
                    ),
                    {
                        "IsUsEast1": True,
                        "IsUsEast2": False,
                    },
                ),
                (
                    "Foo",
                    _append_queues(
                        _standard_path, [0, "Actions", 1, "OutputArtifacts", 0, "Name"]
                    ),
                    {
                        "IsUsEast1": False,
                        "IsUsEast2": True,
                    },
                ),
                (
                    "Foo",
                    _append_queues(
                        _standard_path, [0, "Actions", 1, "InputArtifacts", 0, "Name"]
                    ),
                    {
                        "IsUsEast1": True,
                        "IsUsEast2": False,
                    },
                ),
                (
                    "Foo",
                    _append_queues(
                        _standard_path, [0, "Actions", 1, "InputArtifacts", 1, "Name"]
                    ),
                    {
                        "IsUsEast1": False,
                        "IsUsEast2": True,
                    },
                ),
            ],
            [],
        ),
        (
            [
                (
                    "Foo",
                    _append_queues(
                        _standard_path, [0, "Actions", 0, "OutputArtifacts", 0, "Name"]
                    ),
                    {
                        "IsUsEast1": True,
                        "IsUsEast2": False,
                    },
                ),
                (
                    "Foo",
                    _append_queues(
                        _standard_path, [0, "Actions", 1, "OutputArtifacts", 0, "Name"]
                    ),
                    {
                        "IsUsEast1": True,
                        "IsUsEast2": False,
                    },
                ),
                (
                    "Foo",
                    _append_queues(
                        _standard_path, [0, "Actions", 0, "InputArtifacts", 0, "Name"]
                    ),
                    {
                        "IsUsEast1": False,
                        "IsUsEast2": True,
                    },
                ),
            ],
            [
                ValidationError(
                    "'Foo' is already a defined 'OutputArtifact' Name",
                    rule=PipelineArtifactNames(),
                ),
                ValidationError(
                    "'Foo' is not previously defined as an 'OutputArtifact'",
                    rule=PipelineArtifactNames(),
                ),
            ],
        ),
    ],
)
def test_validate(instances, expected, rule, validator):

    errs = []
    for instance in instances:
        instance_validator = validator.evolve(
            context=validator.context.evolve(
                path=Path(path=instance[1]),
                conditions=validator.context.conditions.evolve(
                    instance[2],
                ),
            )
        )
        errs.extend(list(rule.validate(instance_validator, "", instance[0], {})))

    assert errs == expected, f"Expected {expected} got {errs}"
