"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.rules.resources.neptune.DBInstanceDBInstanceClassEnum import (
    DBInstanceDBInstanceClassEnum,
)


@pytest.fixture(scope="module")
def rule():
    rule = DBInstanceDBInstanceClassEnum()
    yield rule


@pytest.mark.parametrize(
    "name,instance,regions,err_count",
    [
        ("Valid instance class", "db.r6g.large", ["us-east-1"], 0),
        ("Valid serverless", "db.serverless", ["us-east-1"], 0),
        ("x2iezn in us-east-1", "db.x2iezn.2xlarge", ["us-east-1"], 0),
        ("x2iezn 12xlarge in us-west-2", "db.x2iezn.12xlarge", ["us-west-2"], 0),
        ("x2iedn in ap-southeast-1", "db.x2iedn.xlarge", ["ap-southeast-1"], 0),
        (
            "x2iedn 32xlarge in ap-southeast-1",
            "db.x2iedn.32xlarge",
            ["ap-southeast-1"],
            0,
        ),
        ("Not a Neptune instance class", "db.m5.large", ["us-east-1"], 1),
    ],
)
def test_validate(name, instance, regions, err_count, rule, validator):
    validator = validator.evolve(context=validator.context.evolve(regions=regions))
    errors = list(rule.validate(validator, "", instance, {}))

    assert len(errors) == err_count, f"Test {name!r} got {errors!r}"
