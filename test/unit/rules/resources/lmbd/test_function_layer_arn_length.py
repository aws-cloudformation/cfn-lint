"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.lmbd.FunctionLayerArnLength import FunctionLayerArnLength


@pytest.fixture(scope="module")
def rule():
    rule = FunctionLayerArnLength()
    yield rule


@pytest.mark.parametrize(
    "instance,regions,expected",
    [
        (
            "arn:aws:lambda:us-east-1:123456789012:layer:short:1",
            ["us-east-1"],
            [],
        ),
        (
            # 189 chars, us-east-1 max is 188
            "arn:aws:lambda:us-east-1:123456789012:layer:" + "a" * 143 + ":1",
            ["us-east-1"],
            [
                ValidationError(
                    f"'arn:aws:lambda:us-east-1:123456789012:layer:{'a' * 143}:1'"
                    " is longer than 188 in 'us-east-1'"
                ),
            ],
        ),
        (
            # Same ARN passes in ap-southeast-1 (max 193)
            "arn:aws:lambda:us-east-1:123456789012:layer:" + "a" * 143 + ":1",
            ["ap-southeast-1"],
            [],
        ),
        (
            # us-gov partition (max 199)
            "arn:aws:lambda:us-east-1:123456789012:layer:" + "a" * 143 + ":1",
            ["us-gov-west-1"],
            [],
        ),
        (
            # cn partition (max 192 for cn-north-1)
            "arn:aws:lambda:cn-north-1:123456789012:layer:" + "a" * 146 + ":1",
            ["cn-north-1"],
            [
                ValidationError(
                    f"'arn:aws:lambda:cn-north-1:123456789012:layer:{'a' * 146}:1'"
                    " is longer than 192 in 'cn-north-1'"
                ),
            ],
        ),
        (
            # iso partition
            "arn:aws:lambda:us-east-1:123456789012:layer:short:1",
            ["us-iso-east-1"],
            [],
        ),
        (
            # isob partition
            "arn:aws:lambda:us-east-1:123456789012:layer:short:1",
            ["us-isob-east-1"],
            [],
        ),
        (
            # isoe partition
            "arn:aws:lambda:us-east-1:123456789012:layer:short:1",
            ["eu-isoe-west-1"],
            [],
        ),
        (
            # isof partition
            "arn:aws:lambda:us-east-1:123456789012:layer:short:1",
            ["eusc-de-east-1"],
            [],
        ),
        (
            {"Ref": "LayerArn"},
            ["us-east-1"],
            [],
        ),
    ],
)
def test_validate(instance, regions, expected, rule, validator):
    validator = validator.evolve(
        context=validator.context.evolve(regions=regions),
    )
    errs = list(rule.validate(validator, None, instance, {}))
    assert errs == expected, f"Expected {expected} got {errs}"
