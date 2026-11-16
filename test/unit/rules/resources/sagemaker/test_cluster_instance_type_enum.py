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
        ("Valid p5e 48xlarge", "ml.p5e.48xlarge", ["us-east-2"], 0),
        ("Valid p5e 48xlarge in another region", "ml.p5e.48xlarge", ["eu-west-1"], 0),
        ("Valid p5 48xlarge", "ml.p5.48xlarge", ["us-east-2"], 0),
        ("Unknown size", "ml.p5e.24xlarge", ["us-east-2"], 1),
        ("Not a cluster type", "ml.t2.medium", ["us-east-2"], 1),
    ],
)
def test_validate(name, instance, regions, err_count, rule, validator):
    validator = validator.evolve(context=validator.context.evolve(regions=regions))
    errors = list(rule.validate(validator, "", instance, {}))

    assert len(errors) == err_count, f"Test {name!r} got {errors!r}"
