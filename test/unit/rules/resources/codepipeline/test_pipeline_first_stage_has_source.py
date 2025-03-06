"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque
from typing import Iterable

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.codepipeline.PipelineFirstStageHasSource import (
    PipelineFirstStageHasSource,
)


@pytest.fixture(scope="module")
def rule():
    rule = PipelineFirstStageHasSource()
    yield rule


_standard_path = deque(["Resources", "TestPipeline", "Properties", "Stages"])


def _append_queues(queue1: Iterable, queue2: Iterable) -> deque:
    new_queue: deque = deque()
    new_queue.extend(queue1)
    new_queue.extend(queue2)
    return new_queue


@pytest.mark.parametrize(
    "instance,path,expected",
    [
        (
            [],
            {
                "path": _append_queues(
                    _standard_path, [0, "Actions", 0, "ActionTypeId", "Category"]
                ),
            },
            [],
        ),
        (
            "Source",
            {
                "path": _standard_path,
            },
            [],
        ),
        (
            "Source",
            {
                "path": _append_queues(
                    _standard_path, [0, "Actions", 0, "ActionTypeId", "Category"]
                ),
            },
            [],
        ),
        (
            "Build",
            {
                "path": _append_queues(
                    _standard_path, [1, "Actions", 0, "ActionTypeId", "Category"]
                ),
            },
            [],
        ),
        (
            "Source",
            {
                "path": _append_queues(
                    _standard_path,
                    ["Fn::If", 2, 0, "Actions", 0, "ActionTypeId", "Category"],
                ),
            },
            [],
        ),
        (
            "Build",
            {
                "path": _append_queues(
                    _standard_path,
                    ["Fn::If", 1, 1, "Actions", 0, "ActionTypeId", "Category"],
                ),
            },
            [],
        ),
        (
            "Build",
            {
                "path": _append_queues(
                    _standard_path, [0, "Actions", 0, "ActionTypeId", "Category"]
                ),
            },
            [
                ValidationError(
                    "'Build' is not one of ['Source']",
                    rule=PipelineFirstStageHasSource(),
                    validator="enum",
                )
            ],
        ),
        (
            "Build",
            {
                "path": _append_queues(
                    _standard_path,
                    ["Fn::If", 2, 0, "Actions", 0, "ActionTypeId", "Category"],
                ),
            },
            [
                ValidationError(
                    "'Build' is not one of ['Source']",
                    rule=PipelineFirstStageHasSource(),
                    validator="enum",
                )
            ],
        ),
        (
            "Source",
            {
                "path": _append_queues(
                    _standard_path, [1, "Actions", 0, "ActionTypeId", "Category"]
                ),
            },
            [
                ValidationError(
                    (
                        "'Source' is not one of ['Build', 'Approval', "
                        "'Deploy', 'Test', 'Invoke', 'Compute']"
                    ),
                    rule=PipelineFirstStageHasSource(),
                    validator="enum",
                )
            ],
        ),
        (
            "Source",
            {
                "path": _append_queues(
                    _standard_path,
                    ["Fn::If", 1, 1, "Actions", 0, "ActionTypeId", "Category"],
                ),
            },
            [
                ValidationError(
                    (
                        "'Source' is not one of ['Build', 'Approval', "
                        "'Deploy', 'Test', 'Invoke', 'Compute']"
                    ),
                    rule=PipelineFirstStageHasSource(),
                    validator="enum",
                )
            ],
        ),
    ],
    indirect=["path"],
)
def test_validate(instance, path, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))

    assert errs == expected, f"Expected {expected} got {errs}"
