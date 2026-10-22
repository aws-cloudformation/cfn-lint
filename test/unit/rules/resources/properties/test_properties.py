"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque
from unittest.mock import MagicMock, patch

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.properties.Properties import Properties
from cfnlint.schema._schema import Schema


@pytest.fixture(scope="module")
def rule():
    rule = Properties()
    yield rule


@pytest.mark.parametrize(
    "name,instance,patches,expected",
    [
        (
            "Valid results",
            {
                "Type": "MyType",
            },
            [(["us-east-1"], Schema({"typeName": "MyType", "properties": {}}))],
            [],
        ),
        (
            "Invalid type for Type",
            {
                "Type": {},
            },
            [],
            [],
        ),
        (
            "Valid type but no required fields",
            {
                "Type": "MyType",
            },
            [(["us-east-1"], Schema({"typeName": "MyType", "required": ["Name"]}))],
            [
                ValidationError(
                    "'Name' is a required property",
                    validator="required",
                    path=deque(["Properties"]),
                    schema_path=deque(["required"]),
                )
            ],
        ),
        (
            "Invalid with Ref AWS::NoValue",
            {"Type": "MyType", "Properties": {"Ref": "AWS::NoValue"}},
            [],
            [
                ValidationError(
                    "{'Ref': 'AWS::NoValue'} is not of type object",
                    validator="type",
                    path=deque(["Properties", "Ref"]),
                    rule=None,
                )
            ],
        ),
        (
            "Invalid with Null value",
            {"Type": "AWS::S3::Bucket", "Properties": None},
            [],
            [
                ValidationError(
                    "None is not of type object",
                    validator="type",
                    path=deque(["Properties"]),
                    rule=None,
                )
            ],
        ),
    ],
)
def test_validate(name, instance, patches, expected, rule, validator):
    schema_manager = MagicMock()
    schema_manager.get_resource_schemas_by_regions.return_value = patches

    with patch(
        "cfnlint.rules.resources.properties.Properties.PROVIDER_SCHEMA_MANAGER",
        schema_manager,
    ):
        errs = list(rule.validate(validator, {}, instance, {}))

        assert errs == expected, f"Test {name!r} got {errs!r}"

    if patches:
        schema_manager.get_resource_schemas_by_regions.assert_called_once()
        schema_manager.get_resource_schemas_by_regions.assert_called_with(
            instance.get("Type"), ["us-east-1"]
        )
    else:
        schema_manager.get_resource_schemas_by_regions.assert_not_called()


@pytest.mark.parametrize(
    "template",
    [
        {
            "AWSTemplateFormatVersion": "2010-09-09",
            "Conditions": {
                "IsFeatureOn": {"Fn::Equals": ["false", "true"]},
                "IsFeatureEnabled": {"Fn::Equals": ["false", "true"]},
                "OnAndNotEnabled": {
                    "Fn::And": [
                        {"Condition": "IsFeatureOn"},
                        {"Fn::Not": [{"Condition": "IsFeatureEnabled"}]},
                    ]
                },
            },
        }
    ],
    indirect=True,
)
def test_validate_with_unsatisfiable_condition(rule, validator):
    # Regression test for https://github.com/aws-cloudformation/cfn-lint/issues/4785
    # A resource whose own condition can never be true (here `X and not X`
    # over two identical conditions) must not raise Unsatisfiable (previously
    # surfaced as an E3001 exception); its property errors are reported the
    # same way as on an ungated resource.
    instance = {
        "Type": "MyType",
        "Condition": "OnAndNotEnabled",
        "Properties": {"BogusProperty": 1},
    }
    schema_manager = MagicMock()
    schema_manager.get_resource_schemas_by_regions.return_value = [
        (
            ["us-east-1"],
            Schema(
                {
                    "typeName": "MyType",
                    "properties": {},
                    "additionalProperties": False,
                }
            ),
        )
    ]

    with patch(
        "cfnlint.rules.resources.properties.Properties.PROVIDER_SCHEMA_MANAGER",
        schema_manager,
    ):
        errs = list(rule.validate(validator, {}, instance, {}))

    messages = [e.message for e in errs]
    assert any(
        "Additional properties are not allowed ('BogusProperty' was unexpected)"
        in message
        for message in messages
    ), f"property finding missing on gated resource: {messages!r}"
    assert not any("raised while validating" in message for message in messages), (
        f"crash surfaced: {messages!r}"
    )


_RDS_READ_REPLICA_SCHEMA = {
    "typeName": "AWS::RDS::DBInstance",
    # Mirrors the upstream enhanced schema: these may not be set with
    # SourceDBInstanceIdentifier
    "dependentExcluded": {
        "SourceDBInstanceIdentifier": [
            "CharacterSetName",
            "DBName",
            "MasterUserPassword",
            "MasterUsername",
            "StorageEncrypted",
        ]
    },
}


def _rds_schema_manager():
    schema_manager = MagicMock()
    schema_manager.get_resource_schemas_by_regions.return_value = [
        (["us-east-1"], Schema(_RDS_READ_REPLICA_SCHEMA)),
    ]
    return schema_manager


@pytest.mark.parametrize(
    "properties,expected_messages",
    [
        # Ignored on a read replica (inherited from the source): the hard
        # E3020 is wrong severity here, W3692 warns instead, so no errors.
        (
            {
                "SourceDBInstanceIdentifier": "foo",
                "StorageEncrypted": True,
            },
            [],
        ),
        (
            {
                "SourceDBInstanceIdentifier": "foo",
                "MasterUsername": "foo",
            },
            [],
        ),
        (
            {
                "SourceDBInstanceIdentifier": "foo",
                "DBName": "foo",
            },
            [],
        ),
        (
            {
                "SourceDBInstanceIdentifier": "foo",
                "StorageEncrypted": True,
                "MasterUsername": "foo",
                "DBName": "foo",
            },
            [],
        ),
        # Still hard errors: MasterUserPassword is rejected by RDS on
        # physical replication read replicas, CharacterSetName is untouched
        # by this change.
        (
            {
                "SourceDBInstanceIdentifier": "foo",
                "MasterUserPassword": "foo",
            },
            [
                "'MasterUserPassword' should not be included with "
                "'SourceDBInstanceIdentifier'"
            ],
        ),
        (
            {
                "SourceDBInstanceIdentifier": "foo",
                "CharacterSetName": "foo",
            },
            [
                "'CharacterSetName' should not be included with "
                "'SourceDBInstanceIdentifier'"
            ],
        ),
        # Not a read replica: dependentExcluded cannot fire without the
        # trigger property present.
        (
            {
                "DBInstanceClass": "db.t3.micro",
                "StorageEncrypted": True,
            },
            [],
        ),
    ],
)
def test_validate_rds_read_replica_dependent_excluded(
    properties, expected_messages, rule, validator
):
    # Regression test for https://github.com/aws-cloudformation/cfn-lint/issues/4817
    # dependentExcluded violations for properties a read replica silently
    # ignores (StorageEncrypted, MasterUsername, DBName) must not surface as
    # E3020 errors; they are reported by W3692 at warning severity instead.
    instance = {
        "Type": "AWS::RDS::DBInstance",
        "Properties": properties,
    }

    with patch(
        "cfnlint.rules.resources.properties.Properties.PROVIDER_SCHEMA_MANAGER",
        _rds_schema_manager(),
    ):
        errs = list(rule.validate(validator, {}, instance, {}))

    messages = [e.message for e in errs]
    assert sorted(messages) == sorted(expected_messages), (
        f"properties {properties!r} produced {messages!r}"
    )
    assert all(e.validator == "dependentExcluded" for e in errs)
    assert all(e.rule is None or e.rule.id == "E3020" for e in errs)


def test_validate_rds_read_replica_dependent_excluded_other_resource(rule, validator):
    # The suppression is scoped to AWS::RDS::DBInstance; other resources keep
    # their dependentExcluded errors untouched.
    schema_manager = MagicMock()
    schema_manager.get_resource_schemas_by_regions.return_value = [
        (
            ["us-east-1"],
            Schema(
                {
                    "typeName": "AWS::S3::Bucket",
                    "dependentExcluded": {"Foo": ["Bar"]},
                }
            ),
        )
    ]
    instance = {
        "Type": "AWS::S3::Bucket",
        "Properties": {"Foo": "foo", "Bar": "bar"},
    }

    with patch(
        "cfnlint.rules.resources.properties.Properties.PROVIDER_SCHEMA_MANAGER",
        schema_manager,
    ):
        errs = list(rule.validate(validator, {}, instance, {}))

    assert [e.message for e in errs] == ["'Bar' should not be included with 'Foo'"]
