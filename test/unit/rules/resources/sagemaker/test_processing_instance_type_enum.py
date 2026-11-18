"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.rules.resources.sagemaker.ProcessingInstanceTypeEnum import (
    ProcessingInstanceTypeEnum,
)


@pytest.fixture(scope="module")
def rule():
    rule = ProcessingInstanceTypeEnum()
    yield rule


@pytest.mark.parametrize(
    "name,instance,regions,err_count",
    [
        ("Priced in every region", "ml.m5.large", ["us-east-2"], 0),
        # reported in #4884: no Processing products in ap-east-1
        ("API valid, unpriced in region", "ml.c8i.xlarge", ["ap-east-1"], 0),
        ("API valid, smallest c8i", "ml.c8i.xlarge", ["us-east-2"], 0),
        ("API valid, largest c8i", "ml.c8i.96xlarge", ["us-east-2"], 0),
        ("API valid flex", "ml.m7i-flex.large", ["af-south-1"], 0),
        ("API valid c8i-flex", "ml.c8i-flex.xlarge", ["ap-east-1"], 0),
        # a region whose Price List carries only 24 processing products
        ("API valid in a thin region", "ml.g7e.2xlarge", ["ap-east-2"], 0),
        ("Priced but absent from the API enum", "ml.c6i.large", ["ap-southeast-6"], 0),
        # the API lists ml.c8i.* from xlarge up
        ("Size the API does not list", "ml.c8i.large", ["us-east-2"], 1),
        ("Size above the API range", "ml.c8i.128xlarge", ["us-east-2"], 1),
    ],
)
def test_validate(name, instance, regions, err_count, rule, validator):
    validator = validator.evolve(context=validator.context.evolve(regions=regions))
    errors = list(rule.validate(validator, "", instance, {}))

    assert len(errors) == err_count, f"Test {name!r} got {errors!r}"
