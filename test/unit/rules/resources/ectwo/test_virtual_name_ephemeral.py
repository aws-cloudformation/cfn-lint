"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.rules.resources.ectwo.VirtualNameEphemeral import VirtualNameIgnored

_EBS_IGNORES_VIRTUAL_NAME = "'VirtualName' is ignored when 'Ebs' is specified"
_EBS_IGNORES_NO_DEVICE = "'NoDevice' is ignored when 'Ebs' is specified"
_VIRTUAL_NAME_IGNORES_NO_DEVICE = (
    "'NoDevice' is ignored when 'VirtualName' is specified"
)

_REQUIRED_XOR = {"requiredXor": ["VirtualName", "Ebs", "NoDevice"]}
_REQUIRED_OR = {"requiredOr": ["VirtualName", "Ebs", "NoDevice"]}


@pytest.fixture(scope="module")
def rule():
    rule = VirtualNameIgnored()
    yield rule


@pytest.fixture
def template():
    return {
        "Parameters": {"Env": {"Type": "String"}},
        "Conditions": {"IsProd": {"Fn::Equals": [{"Ref": "Env"}, "prod"]}},
        "Resources": {},
    }


@pytest.mark.parametrize(
    "instance,schema,expected",
    [
        # none of the three specified
        ({"DeviceName": "/dev/sdb"}, _REQUIRED_OR, []),
        # exactly one of the three is always fine
        ({"DeviceName": "/dev/sdb", "Ebs": {"VolumeSize": 8}}, _REQUIRED_OR, []),
        ({"DeviceName": "/dev/sdb", "VirtualName": "ephemeral0"}, _REQUIRED_OR, []),
        ({"DeviceName": "/dev/sdb", "NoDevice": {}}, _REQUIRED_OR, []),
        # not an object
        ([], _REQUIRED_OR, []),
        ("", _REQUIRED_OR, []),
        (None, _REQUIRED_OR, []),
        # every pair, and all three
        (
            {"Ebs": {"VolumeSize": 8}, "VirtualName": "ephemeral0"},
            _REQUIRED_OR,
            [_EBS_IGNORES_VIRTUAL_NAME],
        ),
        (
            {"Ebs": {"VolumeSize": 8}, "NoDevice": {}},
            _REQUIRED_OR,
            [_EBS_IGNORES_NO_DEVICE],
        ),
        (
            {"VirtualName": "ephemeral0", "NoDevice": {}},
            _REQUIRED_OR,
            [_VIRTUAL_NAME_IGNORES_NO_DEVICE],
        ),
        (
            {"Ebs": {"VolumeSize": 8}, "VirtualName": "ephemeral0", "NoDevice": {}},
            _REQUIRED_OR,
            [_EBS_IGNORES_VIRTUAL_NAME, _EBS_IGNORES_NO_DEVICE],
        ),
        # requiredXor already reports this as an error (E3014)
        ({"Ebs": {"VolumeSize": 8}, "VirtualName": "ephemeral0"}, _REQUIRED_XOR, []),
        (
            {"Ebs": {"VolumeSize": 8}, "VirtualName": "ephemeral0", "NoDevice": {}},
            _REQUIRED_XOR,
            [],
        ),
        # a property set to AWS::NoValue is not specified
        (
            {"Ebs": {"VolumeSize": 8}, "VirtualName": {"Ref": "AWS::NoValue"}},
            _REQUIRED_OR,
            [],
        ),
        (
            {"Ebs": {"VolumeSize": 8}, "NoDevice": {"Ref": "AWS::NoValue"}},
            _REQUIRED_OR,
            [],
        ),
        # Fn::If that leaves the lower precedence property out of every branch
        (
            {
                "Ebs": {"VolumeSize": 8},
                "VirtualName": {
                    "Fn::If": [
                        "IsProd",
                        {"Ref": "AWS::NoValue"},
                        {"Ref": "AWS::NoValue"},
                    ]
                },
            },
            _REQUIRED_OR,
            [],
        ),
        # Fn::If where one branch specifies both
        (
            {
                "Ebs": {"VolumeSize": 8},
                "VirtualName": {
                    "Fn::If": ["IsProd", "ephemeral0", {"Ref": "AWS::NoValue"}]
                },
            },
            _REQUIRED_OR,
            [_EBS_IGNORES_VIRTUAL_NAME],
        ),
        # Fn::If on the higher precedence property
        (
            {
                "Ebs": {
                    "Fn::If": ["IsProd", {"VolumeSize": 8}, {"Ref": "AWS::NoValue"}]
                },
                "VirtualName": "ephemeral0",
            },
            _REQUIRED_OR,
            [_EBS_IGNORES_VIRTUAL_NAME],
        ),
        # an unresolvable value still specifies the property
        (
            {"Ebs": {"VolumeSize": {"Ref": "Env"}}, "VirtualName": {"Ref": "Env"}},
            _REQUIRED_OR,
            [_EBS_IGNORES_VIRTUAL_NAME],
        ),
    ],
)
def test_validate(instance, schema, expected, rule, validator):
    errs = list(rule.validate(validator.evolve(schema=schema), "", instance, {}))

    assert [err.message for err in errs] == expected, (
        f"Expected {expected} got {[err.message for err in errs]}"
    )
    for err in errs:
        assert len(err.path) == 1
        assert err.path[0] in instance
