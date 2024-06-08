"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.rules.resources.rds.DbInstanceDbInstanceClassEnum import (
    DbInstanceDbInstanceClassEnum,
)


@pytest.fixture(scope="module")
def rule():
    rule = DbInstanceDbInstanceClassEnum()
    yield rule


@pytest.mark.parametrize(
    "name,instance,regions,err_count",
    [
        (
            "Valid version",
            {"DBInstanceClass": "db.x2iedn.8xlarge", "Engine": "mysql"},
            ["us-east-1"],
            0,
        ),
        (
            "Valid but wrong type",
            [],
            ["us-east-1"],
            0,
        ),
        (
            "Valid but wrong type for Engine",
            {"Engine": []},
            ["us-east-1"],
            0,
        ),
        (
            "No error ref value",
            {
                "DBInstanceClass": "notanappropriatetype",
                "Engine": "sqlserver-se",
                "LicenseModel": {"Ref": "License"},
            },
            ["us-east-1"],
            0,
        ),
        (
            "Bad instance type with no license",
            {"DBInstanceClass": "db.m4.xlarge", "Engine": "aurora-mysql"},
            ["us-east-1"],
            1,
        ),
        (
            "Bad value on bring your own license",
            {
                "DBInstanceClass": "db.x2e.xlarge",
                "Engine": "oracle-se2",
                "LicenseModel": "bring-your-own-license",
            },
            ["us-east-1"],
            1,
        ),
        (
            "Bad value on bring your own license",
            {
                "DBInstanceClass": "db.x2e.xlarge",
                "Engine": "oracle-se2",
                "LicenseModel": "bring-your-own-license",
            },
            ["us-east-1"],
            1,
        ),
        (
            "Bad value on license included",
            {
                "DBInstanceClass": "db.x1e.xlarge",
                "Engine": "oracle-se2",
                "LicenseModel": "license-included",
            },
            ["us-east-1"],
            1,
        ),
        (
            "Bad value on license included and uppser case Engine",
            {
                "DBInstanceClass": "db.x1e.xlarge",
                "Engine": "Oracle-SE2",
                "LicenseModel": "license-included",
            },
            ["us-east-1"],
            1,
        ),
        (
            "Instance type invalid in one region",
            {"DBInstanceClass": "db.x2iedn.8xlarge", "Engine": "mysql"},
            ["us-east-1", "ca-west-1"],
            1,
        ),
    ],
)
def test_validate(name, instance, regions, err_count, rule, validator):
    validator = validator.evolve(context=validator.context.evolve(regions=regions))
    errors = list(rule.validate(validator, "", instance, {}))

    # we use error counts in this one as the instance types are
    # always changing so we aren't going to hold ourselves up by that
    assert len(errors) == err_count, f"Test {name!r} got {errors!r}"
