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
        ("Valid m8g large", "ml.m8g.large", ["us-east-2"], 0),
        ("Valid m8g medium", "ml.m8g.medium", ["us-east-2"], 0),
        ("Valid m8g 48xlarge", "ml.m8g.48xlarge", ["us-east-2"], 0),
        ("Valid m8g large in another region", "ml.m8g.large", ["eu-west-1"], 0),
        ("Valid m5 large", "ml.m5.large", ["us-east-2"], 0),
        ("Unknown size", "ml.m8g.32xlarge", ["us-east-2"], 1),
    ],
)
def test_validate(name, instance, regions, err_count, rule, validator):
    validator = validator.evolve(context=validator.context.evolve(regions=regions))
    errors = list(rule.validate(validator, "", instance, {}))

    assert len(errors) == err_count, f"Test {name!r} got {errors!r}"
