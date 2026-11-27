"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.rules.resources.sagemaker.ClusterInstanceTypeEnum import (
    ClusterInstanceTypeEnum,
)


@pytest.fixture(scope="module")
def rule():
    rule = ClusterInstanceTypeEnum()
    yield rule


@pytest.mark.parametrize(
    "name,instance,regions,err_count",
    [
        ("Priced in every region", "ml.p5.48xlarge", ["us-east-2"], 0),
        # reported in #4884: priced under TrSpt, never Cluster
        ("API valid, priced elsewhere", "ml.p5e.48xlarge", ["us-east-2"], 0),
        ("API valid, not priced at all", "ml.trn2.48xlarge", ["us-east-1"], 0),
        # a region whose Price List carries only ten cluster products
        ("API valid in a thin region", "ml.m5.large", ["ap-southeast-5"], 0),
        ("Priced but absent from the API enum", "ml.trn1.2xlarge", ["us-east-2"], 0),
        ("Size the API does not list", "ml.p5e.24xlarge", ["us-east-2"], 1),
        ("Not a cluster type", "ml.t2.medium", ["us-east-2"], 1),
    ],
)
def test_validate(name, instance, regions, err_count, rule, validator):
    validator = validator.evolve(context=validator.context.evolve(regions=regions))
    errors = list(rule.validate(validator, "", instance, {}))

    assert len(errors) == err_count, f"Test {name!r} got {errors!r}"
