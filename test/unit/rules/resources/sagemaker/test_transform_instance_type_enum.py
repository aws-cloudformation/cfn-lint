"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.rules.resources.sagemaker.TransformInstanceTypeEnum import (
    TransformInstanceTypeEnum,
)


@pytest.fixture(scope="module")
def rule():
    rule = TransformInstanceTypeEnum()
    yield rule


@pytest.mark.parametrize(
    "name,instance,regions,err_count",
    [
        ("Priced in every region", "ml.m5.large", ["us-east-2"], 0),
        # reported in #4884: priced under Train/Host/Cluster, never Tsform
        ("API valid, priced elsewhere", "ml.p3.2xlarge", ["us-east-2"], 0),
        ("API valid, largest p3", "ml.p3.16xlarge", ["us-east-2"], 0),
        ("API valid inf2", "ml.inf2.48xlarge", ["us-east-2"], 0),
        ("API valid trn1", "ml.trn1.32xlarge", ["us-east-2"], 0),
        # ml.p3.* is not priced at all in us-east-2
        ("API valid, unpriced in region", "ml.p3.8xlarge", ["us-east-2"], 0),
        # a region whose Price List carries only ten transform products
        ("API valid in a thin region", "ml.p2.xlarge", ["ap-southeast-4"], 0),
        ("Priced but absent from the API enum", "ml.g6f.large", ["us-east-2"], 0),
        ("Size the API does not list", "ml.p3.24xlarge", ["us-east-2"], 1),
        ("Not a transform type", "ml.trn1.16xlarge", ["us-east-2"], 1),
    ],
)
def test_validate(name, instance, regions, err_count, rule, validator):
    validator = validator.evolve(context=validator.context.evolve(regions=regions))
    errors = list(rule.validate(validator, "", instance, {}))

    assert len(errors) == err_count, f"Test {name!r} got {errors!r}"
