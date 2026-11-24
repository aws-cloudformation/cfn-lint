"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import json

import pytest

from cfnlint.api import lint
from cfnlint.rules.resources.emr.ClusterInstanceTypeConfigInstanceTypeEnum import (
    ClusterInstanceTypeConfigInstanceTypeEnum,
)


@pytest.fixture(scope="module")
def rule():
    rule = ClusterInstanceTypeConfigInstanceTypeEnum()
    yield rule


@pytest.mark.parametrize(
    "name,instance,err_count",
    [
        ("Valid instance type", "m5.xlarge", 0),
        ("Invalid instance type", "m9z.huge", 1),
    ],
)
def test_validate(name, instance, err_count, rule, validator):
    errors = list(rule.validate(validator, "", instance, {}))

    assert len(errors) == err_count, f"Test {name!r} got {errors!r}"
    if err_count:
        assert errors[0].message.startswith("'m9z.huge' is not one of [")
        assert errors[0].message.endswith("] in 'us-east-1'")


def _instance_group(instance_type):
    return {"InstanceType": instance_type}


def _instance_fleet(instance_type):
    return {"InstanceTypeConfigs": [{"InstanceType": instance_type}]}


@pytest.mark.parametrize(
    "name,resource_type,properties,expected",
    [
        (
            "Invalid core instance group",
            "AWS::EMR::Cluster",
            {"Instances": {"CoreInstanceGroup": _instance_group("m9z.huge")}},
            ["E3675"],
        ),
        (
            "Invalid core instance fleet",
            "AWS::EMR::Cluster",
            {"Instances": {"CoreInstanceFleet": _instance_fleet("m9z.huge")}},
            ["E3675"],
        ),
        (
            "Invalid primary instance group",
            "AWS::EMR::Cluster",
            {"Instances": {"MasterInstanceGroup": _instance_group("m9z.huge")}},
            ["E3675"],
        ),
        (
            "Invalid primary instance fleet",
            "AWS::EMR::Cluster",
            {"Instances": {"MasterInstanceFleet": _instance_fleet("m9z.huge")}},
            ["E3675"],
        ),
        (
            "Invalid task instance groups",
            "AWS::EMR::Cluster",
            {"Instances": {"TaskInstanceGroups": [_instance_group("m9z.huge")]}},
            ["E3675"],
        ),
        (
            "Invalid task instance fleets",
            "AWS::EMR::Cluster",
            {"Instances": {"TaskInstanceFleets": [_instance_fleet("m9z.huge")]}},
            ["E3675"],
        ),
        (
            "Invalid instance group config",
            "AWS::EMR::InstanceGroupConfig",
            _instance_group("m9z.huge"),
            ["E3675"],
        ),
        (
            "Invalid instance fleet config",
            "AWS::EMR::InstanceFleetConfig",
            _instance_fleet("m9z.huge"),
            ["E3675"],
        ),
        (
            "Valid primary instance group",
            "AWS::EMR::Cluster",
            {"Instances": {"MasterInstanceGroup": _instance_group("m5.xlarge")}},
            [],
        ),
        (
            "Valid instance group config",
            "AWS::EMR::InstanceGroupConfig",
            _instance_group("m5.xlarge"),
            [],
        ),
        (
            "Valid instance fleet config",
            "AWS::EMR::InstanceFleetConfig",
            _instance_fleet("m5.xlarge"),
            [],
        ),
        (
            "Ref to a parameter is not checked",
            "AWS::EMR::InstanceGroupConfig",
            _instance_group({"Ref": "InstanceType"}),
            [],
        ),
        (
            "Instance type absent",
            "AWS::EMR::InstanceGroupConfig",
            {"InstanceCount": 1},
            [],
        ),
    ],
)
def test_keywords(name, resource_type, properties, expected):
    template = {
        "Parameters": {"InstanceType": {"Type": "String"}},
        "Resources": {
            "Resource": {"Type": resource_type, "Properties": properties},
        },
    }
    matches = lint(json.dumps(template), regions=["us-east-1"])

    assert [m.rule.id for m in matches if m.rule.id == "E3675"] == expected, (
        f"Test {name!r} got {matches!r}"
    )
