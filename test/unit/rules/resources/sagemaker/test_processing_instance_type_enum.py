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
        ("Valid c8i xlarge", "ml.c8i.xlarge", ["ap-east-1"], 0),
        ("Valid c8i 96xlarge", "ml.c8i.96xlarge", ["ap-east-1"], 0),
        ("Valid m7i-flex large", "ml.m7i-flex.large", ["af-south-1"], 0),
        ("Valid c8i-flex xlarge", "ml.c8i-flex.xlarge", ["ap-east-1"], 0),
        ("Valid m8i-flex large", "ml.m8i-flex.large", ["ap-east-1"], 0),
        ("Valid c8i xlarge in us-east-2", "ml.c8i.xlarge", ["us-east-2"], 0),
        ("c8i large is not an API type", "ml.c8i.large", ["us-east-2"], 1),
        ("Unknown size", "ml.c8i.128xlarge", ["us-east-2"], 1),
    ],
)
def test_validate(name, instance, regions, err_count, rule, validator):
    validator = validator.evolve(context=validator.context.evolve(regions=regions))
    errors = list(rule.validate(validator, "", instance, {}))

    assert len(errors) == err_count, f"Test {name!r} got {errors!r}"
