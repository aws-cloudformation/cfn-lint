"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.rules.resources.amazonmq.BrokerInstanceTypeEnum import (
    BrokerInstanceTypeEnum,
)


@pytest.fixture(scope="module")
def rule():
    rule = BrokerInstanceTypeEnum()
    yield rule


@pytest.mark.parametrize(
    "name,instance,regions,err_count",
    [
        ("Valid m7g large", "mq.m7g.large", ["us-east-1"], 0),
        ("Valid m7g 2xlarge", "mq.m7g.2xlarge", ["us-east-1"], 0),
        ("Valid m7g 4xlarge", "mq.m7g.4xlarge", ["us-east-1"], 0),
        ("Valid m7g 8xlarge", "mq.m7g.8xlarge", ["us-east-1"], 0),
        ("Valid m7g 12xlarge", "mq.m7g.12xlarge", ["us-east-1"], 0),
        ("Valid m7g 16xlarge", "mq.m7g.16xlarge", ["us-east-1"], 0),
        ("Valid m5 2xlarge", "mq.m5.2xlarge", ["us-east-1"], 0),
        (
            "Valid m7i 2xlarge",
            "mq.m7i.2xlarge",
            ["ap-east-2", "ap-southeast-6"],
            0,
        ),
        (
            "Valid m7i 4xlarge",
            "mq.m7i.4xlarge",
            ["ap-east-2", "ap-southeast-6"],
            0,
        ),
        ("Price List abbreviation", "mq.m7g.2xl", ["us-east-1"], 1),
        ("Unknown size", "mq.m7g.32xlarge", ["us-east-1"], 1),
        ("m7i not in this region", "mq.m7i.2xlarge", ["us-east-1"], 1),
    ],
)
def test_validate(name, instance, regions, err_count, rule, validator):
    validator = validator.evolve(context=validator.context.evolve(regions=regions))
    errors = list(rule.validate(validator, "", instance, {}))

    assert len(errors) == err_count, f"Test {name!r} got {errors!r}"
