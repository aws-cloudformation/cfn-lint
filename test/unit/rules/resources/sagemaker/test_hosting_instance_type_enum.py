"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.rules.resources.sagemaker.HostingInstanceTypeEnum import (
    HostingInstanceTypeEnum,
)


@pytest.fixture(scope="module")
def rule():
    rule = HostingInstanceTypeEnum()
    yield rule


@pytest.mark.parametrize(
    "name,instance,regions,err_count",
    [
        ("Priced in every region", "ml.m5.large", ["us-east-2"], 0),
        # reported in #4884: priced only under Cluster, never Host
        ("API valid, priced elsewhere", "ml.m8g.large", ["us-east-2"], 0),
        ("API valid, smallest m8g", "ml.m8g.medium", ["us-east-2"], 0),
        ("API valid, largest m8g", "ml.m8g.48xlarge", ["us-east-2"], 0),
        ("API valid c6in", "ml.c6in.xlarge", ["us-east-1"], 0),
        # a region whose Price List carries only 45 hosting products
        ("API valid in a thin region", "ml.m6i.4xlarge", ["af-south-1"], 0),
        ("Priced but absent from the API enum", "ml.c7g.medium", ["us-east-1"], 0),
        ("Size the API does not list", "ml.m8g.32xlarge", ["us-east-2"], 1),
        ("Not an instance type", "ml.m8g.nano", ["us-east-2"], 1),
    ],
)
def test_validate(name, instance, regions, err_count, rule, validator):
    validator = validator.evolve(context=validator.context.evolve(regions=regions))
    errors = list(rule.validate(validator, "", instance, {}))

    assert len(errors) == err_count, f"Test {name!r} got {errors!r}"
