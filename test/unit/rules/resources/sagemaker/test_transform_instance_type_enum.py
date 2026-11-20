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
        ("Valid p3 2xlarge", "ml.p3.2xlarge", ["us-east-2"], 0),
        ("Valid p3 8xlarge", "ml.p3.8xlarge", ["us-east-2"], 0),
        ("Valid p3 16xlarge", "ml.p3.16xlarge", ["us-east-2"], 0),
        ("Valid inf2 xlarge", "ml.inf2.xlarge", ["us-east-2"], 0),
        ("Valid inf2 48xlarge", "ml.inf2.48xlarge", ["us-east-2"], 0),
        ("Valid trn1 2xlarge", "ml.trn1.2xlarge", ["us-east-2"], 0),
        ("Valid trn1 32xlarge", "ml.trn1.32xlarge", ["us-east-2"], 0),
        ("Valid m5 large", "ml.m5.large", ["us-east-2"], 0),
        ("Unknown size", "ml.p3.24xlarge", ["us-east-2"], 1),
        ("Not a transform type", "ml.trn1.16xlarge", ["us-east-2"], 1),
    ],
)
def test_validate(name, instance, regions, err_count, rule, validator):
    validator = validator.evolve(context=validator.context.evolve(regions=regions))
    errors = list(rule.validate(validator, "", instance, {}))

    assert len(errors) == err_count, f"Test {name!r} got {errors!r}"
