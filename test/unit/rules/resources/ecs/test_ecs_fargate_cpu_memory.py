"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.ecs.FargateCpuMemory import FargateCpuMemory


@pytest.fixture(scope="module")
def rule():
    rule = FargateCpuMemory()
    yield rule


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            {
                "RequiresCompatibilities": ["FARGATE"],
                "Cpu": 256,
                "Memory": "512",
            },
            [],
        ),
        (
            {
                "RequiresCompatibilities": ["FARGATE"],
                "Cpu": "512",
                "Memory": 1024,
            },
            [],
        ),
        (
            {
                "RequiresCompatibilities": ["FARGATE"],
                "Cpu": ".5 vCPU",
                "Memory": "1 GB",
            },
            [],
        ),
        (
            {
                "RequiresCompatibilities": ["FARGATE"],
                "Cpu": "1024",
                "Memory": "2048",
            },
            [],
        ),
        (
            {
                "RequiresCompatibilities": ["FARGATE"],
                "Cpu": 2048,
                "Memory": 4096,
            },
            [],
        ),
        (
            {
                "RequiresCompatibilities": ["FARGATE"],
                "Cpu": "4 vcpu",
                "Memory": 30720,
            },
            [],
        ),
        (
            {
                "RequiresCompatibilities": ["FARGATE"],
                "Cpu": "4 vcpu",
                "Memory": "22 gb",
            },
            [],
        ),
        (
            {
                "RequiresCompatibilities": ["FARGATE"],
                "Cpu": 8192,
                "Memory": "16 GB",
            },
            [],
        ),
        (
            {
                "RequiresCompatibilities": ["FARGATE"],
                "Cpu": "16     vCpU",
                "Memory": 122880,
            },
            [],
        ),
        (
            {
                "RequiresCompatibilities": ["FARGATE"],
                "Cpu": 16384,
                "Memory": 123904,
            },
            [
                ValidationError(
                    "Cpu 16384 is not compatible with memory 123904",
                    rule=FargateCpuMemory(),
                    path=deque([]),
                    validator="anyOf",
                    schema_path=deque(["then", "anyOf"]),
                )
            ],
        ),
        (
            {
                "RequiresCompatibilities": ["FARGATE"],
                "Cpu": 16384,
                "Memory": "1 GB",
            },
            [
                ValidationError(
                    "Cpu 16384 is not compatible with memory '1 GB'",
                    rule=FargateCpuMemory(),
                    path=deque([]),
                    validator="anyOf",
                    schema_path=deque(["then", "anyOf"]),
                )
            ],
        ),
        (
            {
                "RequiresCompatibilities": ["FARGATE", "Foo"],
                "Cpu": 4096,
                "Memory": 512,
            },
            [
                ValidationError(
                    "Cpu 4096 is not compatible with memory 512",
                    rule=FargateCpuMemory(),
                    path=deque([]),
                    validator="anyOf",
                    schema_path=deque(["then", "anyOf"]),
                )
            ],
        ),
        (
            {
                "RequiresCompatibilities": ["FARGATE", "Foo"],
                "Cpu": 4096,
                "Memory": 16385,
            },
            [
                ValidationError(
                    "Cpu 4096 is not compatible with memory 16385",
                    rule=FargateCpuMemory(),
                    path=deque([]),
                    validator="anyOf",
                    schema_path=deque(["then", "anyOf"]),
                )
            ],
        ),
    ],
)
def test_validate(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))

    assert errs == expected, f"Expected {expected} got {errs}"
