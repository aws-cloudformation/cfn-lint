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
            # 205 chars, us-east-1 max is 204
            "arn:aws:lambda:us-east-1:123456789012:layer:" + "a" * 159 + ":1",
            ["us-east-1"],
            [
                ValidationError(
                    f"'arn:aws:lambda:us-east-1:123456789012:layer:{'a' * 159}:1'"
                    " is longer than 204 in 'us-east-1'"
                ),
            ],
        ),
        (
            # 140-char layer name with a 4-digit version (issue #4849)
            "arn:aws:lambda:us-east-1:123456789012:layer:" + "a" * 140 + ":1000",
            ["us-east-1"],
            [],
        ),
        (
            # exactly 204 chars, the us-east-1 max, so no error
            "arn:aws:lambda:us-east-1:123456789012:layer:" + "a" * 158 + ":1",
            ["us-east-1"],
            [],
        ),
        (
            # 159-char name: errors in us-east-1 (max 204), passes here (max 209)
            "arn:aws:lambda:us-east-1:123456789012:layer:" + "a" * 159 + ":1",
            ["ap-southeast-1"],
            [],
        ),
        (
            # us-gov partition (max 215)
            "arn:aws:lambda:us-east-1:123456789012:layer:" + "a" * 159 + ":1",
            ["us-gov-west-1"],
            [],
        ),
        (
            # cn partition (max 208 for cn-north-1)
            "arn:aws:lambda:cn-north-1:123456789012:layer:" + "a" * 162 + ":1",
            ["cn-north-1"],
            [
                ValidationError(
                    f"'arn:aws:lambda:cn-north-1:123456789012:layer:{'a' * 162}:1'"
                    " is longer than 208 in 'cn-north-1'"
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
