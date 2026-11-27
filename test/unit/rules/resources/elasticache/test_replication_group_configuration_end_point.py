"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest
import yaml

import cfnlint.decode
from cfnlint.rules.resources.elasticache.ReplicationGroupConfigurationEndPoint import (
    ReplicationGroupConfigurationEndPoint,
)
from cfnlint.template import Template

GOOD_TEMPLATE = (
    "test/fixtures/templates/good/resources/elasticache/"
    "replication_group_configuration_end_point.yaml"
)
BAD_TEMPLATE = (
    "test/fixtures/templates/bad/resources/elasticache/"
    "replication_group_configuration_end_point.yaml"
)

TWO_SHARDS = [
    {"NodeGroupId": "0001", "ReplicaCount": 1, "Slots": "0-8191"},
    {"NodeGroupId": "0002", "ReplicaCount": 1, "Slots": "8192-16383"},
]
ONE_SHARD = [{"NodeGroupId": "0001", "ReplicaCount": 1, "Slots": "0-16383"}]


def _message(attribute):
    return (
        f"'{attribute}' is not available on a cluster mode disabled "
        "replication group. 'ConfigurationEndPoint' is only "
        "returned when the replication group is clustered. Use "
        "'PrimaryEndPoint' or 'ReadEndPoint' instead."
    )


def _group(properties):
    return {
        "Type": "AWS::ElastiCache::ReplicationGroup",
        "Properties": properties,
    }


def _reader(getatt):
    return {
        "Type": "AWS::SSM::Parameter",
        "Properties": {"Type": "String", "Value": {"Fn::GetAtt": getatt}},
    }


def _template(resources, **sections):
    template = {"AWSTemplateFormatVersion": "2010-09-09", "Resources": resources}
    template.update(sections)
    return template


@pytest.fixture(scope="module")
def rule():
    rule = ReplicationGroupConfigurationEndPoint()
    yield rule


def _matches(rule, cfn):
    """Run the rule over every replication group in the template."""
    matches = []
    for logical_id, resource in cfn.get_resources().items():
        if not isinstance(resource, dict):
            continue
        if resource.get("Type") != "AWS::ElastiCache::ReplicationGroup":
            continue
        properties = resource.get("Properties")
        if not isinstance(properties, dict):
            continue
        matches.extend(
            rule.match_resource_properties(
                properties,
                "AWS::ElastiCache::ReplicationGroup",
                ["Resources", logical_id, "Properties"],
                cfn,
            )
        )
    return matches


@pytest.mark.parametrize(
    "properties,expected",
    [
        # Explicit ClusterMode decides first
        ({"ClusterMode": "enabled"}, True),
        ({"ClusterMode": "disabled"}, False),
        ({"ClusterMode": "compatible"}, None),
        ({"ClusterMode": {"Ref": "Mode"}}, None),
        (
            {"ClusterMode": "disabled", "NodeGroupConfiguration": TWO_SHARDS},
            False,
        ),
        # Restores and global secondaries inherit cluster mode
        ({"SnapshotName": "my-snapshot"}, None),
        (
            {
                "SnapshotArns": [
                    "arn:aws:elasticache:us-east-1:123456789012:snapshot:my-snapshot"
                ]
            },
            None,
        ),
        ({"GlobalReplicationGroupId": "my-global-group"}, None),
        # NumNodeGroups sizing
        ({"NumNodeGroups": 3}, True),
        ({"NumNodeGroups": "3"}, True),
        ({"NumNodeGroups": 1}, False),
        ({"NumNodeGroups": "one"}, None),
        ({"NumNodeGroups": True}, None),
        ({"NumNodeGroups": {"Ref": "NodeGroups"}}, None),
        # NodeGroupConfiguration sizing agrees with NumNodeGroups
        ({"NodeGroupConfiguration": TWO_SHARDS}, True),
        ({"NodeGroupConfiguration": ONE_SHARD}, False),
        ({"NodeGroupConfiguration": []}, False),
        ({"NodeGroupConfiguration": {"Ref": "NodeGroups"}}, None),
        (
            {
                "NodeGroupConfiguration": TWO_SHARDS,
                "CacheParameterGroupName": "default.valkey8",
            },
            True,
        ),
        # Parameter group names
        ({"CacheParameterGroupName": "default.valkey8.cluster.on"}, True),
        ({"CacheParameterGroupName": "default.valkey8"}, False),
        ({"CacheParameterGroupName": "my-custom-group"}, None),
        ({"CacheParameterGroupName": {"Ref": "ParameterGroup"}}, None),
        (
            {
                "NumNodeGroups": 1,
                "CacheParameterGroupName": "my-custom-group",
            },
            None,
        ),
        (
            {"NumNodeGroups": 1, "CacheParameterGroupName": "default.valkey8"},
            False,
        ),
        # Nothing named: the engine default parameter group applies
        ({}, False),
        # Non-dict properties cannot be determined
        ([], None),
    ],
)
def test_is_cluster_enabled(properties, expected, rule):
    assert rule._is_cluster_enabled(properties) is expected


@pytest.mark.parametrize(
    "template,expected_messages",
    [
        # Invalid: the #5049 shape reports with the exact message
        (
            _template(
                {
                    "Group": _group(
                        {
                            "ReplicationGroupDescription": "one shard",
                            "Engine": "valkey",
                            "CacheNodeType": "cache.t4g.micro",
                            "NumNodeGroups": 1,
                            "ReplicasPerNodeGroup": 0,
                        }
                    ),
                    "Endpoint": _reader("Group.ConfigurationEndPoint.Address"),
                }
            ),
            [_message("Group.ConfigurationEndPoint.Address")],
        ),
        # Invalid: explicit ClusterMode disabled, list form GetAtt
        (
            _template(
                {
                    "Group": _group({"ClusterMode": "disabled"}),
                    "Endpoint": _reader(["Group", "ConfigurationEndPoint.Port"]),
                }
            ),
            [_message("Group.ConfigurationEndPoint.Port")],
        ),
        # Invalid: one entry in NodeGroupConfiguration is one shard
        (
            _template(
                {
                    "Group": _group({"NodeGroupConfiguration": ONE_SHARD}),
                    "Endpoint": _reader("Group.ConfigurationEndPoint.Address"),
                }
            ),
            [_message("Group.ConfigurationEndPoint.Address")],
        ),
        # Valid: PrimaryEndPoint exists on a disabled group
        (
            _template(
                {
                    "Group": _group({"NumNodeGroups": 1}),
                    "Endpoint": _reader("Group.PrimaryEndPoint.Address"),
                }
            ),
            [],
        ),
        # Valid: cluster mode enabled
        (
            _template(
                {
                    "Group": _group({"ClusterMode": "enabled"}),
                    "Endpoint": _reader("Group.ConfigurationEndPoint.Address"),
                }
            ),
            [],
        ),
        # Valid: three shards by NumNodeGroups
        (
            _template(
                {
                    "Group": _group({"NumNodeGroups": 3}),
                    "Endpoint": _reader("Group.ConfigurationEndPoint.Address"),
                }
            ),
            [],
        ),
        # Valid: two shards by NodeGroupConfiguration, no parameter group
        (
            _template(
                {
                    "Group": _group(
                        {
                            "Engine": "redis",
                            "NodeGroupConfiguration": TWO_SHARDS,
                        }
                    ),
                    "Endpoint": _reader("Group.ConfigurationEndPoint.Address"),
                }
            ),
            [],
        ),
        # Valid: two shards by NodeGroupConfiguration, Ref parameter group
        (
            _template(
                {
                    "ClusterParams": {
                        "Type": "AWS::ElastiCache::ParameterGroup",
                        "Properties": {
                            "CacheParameterGroupFamily": "redis7",
                            "Description": "cluster mode on",
                            "Properties": {"cluster-enabled": "yes"},
                        },
                    },
                    "Group": _group(
                        {
                            "Engine": "redis",
                            "CacheParameterGroupName": {"Ref": "ClusterParams"},
                            "NodeGroupConfiguration": TWO_SHARDS,
                        }
                    ),
                    "Endpoint": _reader("Group.ConfigurationEndPoint.Address"),
                }
            ),
            [],
        ),
        # Valid: one shard by ReplicasPerNodeGroup, Ref parameter group
        (
            _template(
                {
                    "ClusterParams": {
                        "Type": "AWS::ElastiCache::ParameterGroup",
                        "Properties": {
                            "CacheParameterGroupFamily": "redis7",
                            "Description": "cluster mode on",
                            "Properties": {"cluster-enabled": "yes"},
                        },
                    },
                    "Group": _group(
                        {
                            "Engine": "redis",
                            "CacheParameterGroupName": {"Ref": "ClusterParams"},
                            "ReplicasPerNodeGroup": 1,
                        }
                    ),
                    "Endpoint": _reader("Group.ConfigurationEndPoint.Address"),
                }
            ),
            [],
        ),
        # Valid: a custom parameter group name is undetermined
        (
            _template(
                {
                    "Group": _group(
                        {
                            "NumNodeGroups": 1,
                            "CacheParameterGroupName": "my-custom-group",
                        }
                    ),
                    "Endpoint": _reader("Group.ConfigurationEndPoint.Address"),
                }
            ),
            [],
        ),
        # Valid: a restore inherits cluster mode from the snapshot
        (
            _template(
                {
                    "Group": _group({"SnapshotName": "my-snapshot"}),
                    "Endpoint": _reader("Group.ConfigurationEndPoint.Address"),
                }
            ),
            [],
        ),
        # Valid: clustered in one Fn::If scenario only
        (
            _template(
                {
                    "Group": _group(
                        {"NumNodeGroups": {"Fn::If": ["UseCluster", 3, 1]}}
                    ),
                    "Endpoint": _reader("Group.ConfigurationEndPoint.Address"),
                },
                Parameters={"NodeGroups": {"Type": "Number", "Default": 1}},
                Conditions={"UseCluster": {"Fn::Equals": [{"Ref": "NodeGroups"}, 3]}},
            ),
            [],
        ),
        # Valid: the GetAtt reads a different, clustered group
        (
            _template(
                {
                    "Group": _group({"NumNodeGroups": 1}),
                    "Other": _group({"ClusterMode": "enabled"}),
                    "Endpoint": _reader("Other.ConfigurationEndPoint.Address"),
                }
            ),
            [],
        ),
    ],
)
def test_match(template, expected_messages, rule):
    decoded = cfnlint.decode.cfn_yaml.loads(yaml.safe_dump(template))
    cfn = Template("", decoded, ["us-east-1"], [])

    matches = _matches(rule, cfn)

    assert [match.message for match in matches] == expected_messages


def test_good_fixture(rule):
    template = cfnlint.decode.cfn_yaml.load(GOOD_TEMPLATE)
    cfn = Template(GOOD_TEMPLATE, template, ["us-east-1"], [])

    assert _matches(rule, cfn) == []


def test_bad_fixture(rule):
    template = cfnlint.decode.cfn_yaml.load(BAD_TEMPLATE)
    cfn = Template(BAD_TEMPLATE, template, ["us-east-1"], [])

    messages = sorted(match.message for match in _matches(rule, cfn))

    assert messages == sorted(
        [
            _message("DisabledGroup.ConfigurationEndPoint.Address"),
            _message("DisabledGroup.ConfigurationEndPoint.Port"),
            _message("DisabledGroupNoNodeGroups.ConfigurationEndPoint.Address"),
            _message("DisabledGroupExplicit.ConfigurationEndPoint.Port"),
        ]
    )
