"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.rules.resources.glue.TableInputTableType import TableInputTableType

_MESSAGE = (
    "{!r} is not a recognized TableType, Glue stores it but query engines "
    "look for one of ['EXTERNAL_TABLE', 'GOVERNED', 'INDEX_TABLE', "
    "'MANAGED_TABLE', 'MATERIALIZED_VIEW', 'VIRTUAL_VIEW']"
)


@pytest.fixture(scope="module")
def rule():
    rule = TableInputTableType()
    yield rule


@pytest.fixture
def template():
    return {
        "Parameters": {"TableType": {"Type": "String"}},
        "Conditions": {"IsView": {"Fn::Equals": [{"Ref": "TableType"}, "view"]}},
        "Resources": {
            "Table": {
                "Type": "AWS::Glue::Table",
                "Properties": {
                    "CatalogId": "123456789012",
                    "DatabaseName": "db",
                    "TableInput": {"Name": "t"},
                },
            }
        },
    }


@pytest.mark.parametrize(
    "instance,expected_count,expected_message,expected_path",
    [
        # Valid: property absent
        ({"Name": "t"}, 0, None, None),
        # Valid: Glue's own default
        ({"TableType": "EXTERNAL_TABLE"}, 0, None, None),
        # Valid: Lake Formation governed table
        ({"TableType": "GOVERNED"}, 0, None, None),
        # Valid: Hive view type
        ({"TableType": "VIRTUAL_VIEW"}, 0, None, None),
        # Valid: unresolvable value
        ({"TableType": {"Ref": "TableType"}}, 0, None, None),
        # Valid: both branches of a condition are recognized
        (
            {"TableType": {"Fn::If": ["IsView", "VIRTUAL_VIEW", "EXTERNAL_TABLE"]}},
            0,
            None,
            None,
        ),
        # Valid: wrong type is handled by another rule
        ([], 0, None, None),
        # Invalid: a typo
        (
            {"TableType": "EXTERNAL_TABL"},
            1,
            _MESSAGE.format("EXTERNAL_TABL"),
            deque(["TableType"]),
        ),
        # Invalid: lower case, which Hive and Athena do not match
        (
            {"TableType": "external_table"},
            1,
            _MESSAGE.format("external_table"),
            deque(["TableType"]),
        ),
        # Invalid: one branch of a condition
        (
            {"TableType": {"Fn::If": ["IsView", "VIRTUAL_VIEW", "EXTERNAL_TABL"]}},
            1,
            _MESSAGE.format("EXTERNAL_TABL"),
            deque(["TableType"]),
        ),
    ],
)
def test_validate(
    instance, expected_count, expected_message, expected_path, rule, validator
):
    errs = list(rule.validate(validator, "", instance, {}))

    assert len(errs) == expected_count, (
        f"Expected {expected_count} errors got {len(errs)}"
    )
    if expected_message:
        assert errs[0].message == expected_message
        assert errs[0].path == expected_path
