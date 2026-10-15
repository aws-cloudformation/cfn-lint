"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.rules.resources.docdb.DBInstanceClassEnum import DBInstanceClassEnum


@pytest.fixture(scope="module")
def rule():
    rule = DBInstanceClassEnum()
    yield rule


@pytest.mark.parametrize(
    "name,instance,regions,err_count",
    [
        ("Valid instance class", "db.r6g.large", ["us-east-1"], 0),
        ("Valid serverless", "db.serverless", ["us-east-1", "il-central-1"], 0),
        ("Not a DocumentDB instance class", "db.m5.large", ["us-east-1"], 1),
        ("Instance class invalid in one region", "db.r4.large", ["il-central-1"], 1),
    ],
)
def test_validate(name, instance, regions, err_count, rule, validator):
    validator = validator.evolve(context=validator.context.evolve(regions=regions))
    errors = list(rule.validate(validator, "", instance, {}))

    assert len(errors) == err_count, f"Test {name!r} got {errors!r}"
