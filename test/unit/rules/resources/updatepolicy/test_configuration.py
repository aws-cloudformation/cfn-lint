"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.updatepolicy.Configuration import Configuration


@pytest.fixture(scope="module")
def rule():
    rule = Configuration()
    yield rule


@pytest.mark.parametrize(
    "name,instance,expected",
    [
        ("Valid with a non updatable type", {"Type": "AWS::Foo::Bar"}, []),
        (
            "Invalid with autoscaling group wrong type",
            {"Type": "AWS::AutoScaling::AutoScalingGroup", "UpdatePolicy": []},
            [
                ValidationError(
                    "[] is not of type 'object'",
                    path=["UpdatePolicy"],
                    rule=Configuration(),
                    instance=[],
                    validator="type",
                    validator_value="object",
                    schema_path=[
                        "allOf",
                        0,
                        "then",
                        "properties",
                        "UpdatePolicy",
                        "type",
                    ],
                )
            ],
        ),
        (
            "Invalid with autoscaling group wrong property",
            {
                "Type": "AWS::AutoScaling::AutoScalingGroup",
                "UpdatePolicy": {"Foo": "Bar"},
            },
            [
                ValidationError(
                    "Additional properties are not allowed ('Foo' was unexpected)",
                    path=["UpdatePolicy", "Foo"],
                    rule=Configuration(),
                    instance={"Foo": "Bar"},
                    validator="additionalProperties",
                    validator_value=False,
                    schema_path=[
                        "allOf",
                        0,
                        "then",
                        "properties",
                        "UpdatePolicy",
                        "additionalProperties",
                    ],
                )
            ],
        ),
        (
            "Valid with autoscaling group",
            {
                "Type": "AWS::AutoScaling::AutoScalingGroup",
                "UpdatePolicy": {
                    "AutoScalingReplacingUpdate": {
                        "WillReplace": True,
                    },
                    "AutoScalingRollingUpdate": {
                        "MaxBatchSize": 1,
                        "MinInstancesInService": "1",  # also allows strings
                        "MinSuccessfulInstancesPercent": 100,
                        "PauseTime": "PT1M",
                        "WaitOnResourceSignals": True,
                        "SuspendProcesses": ["AZRebalance"],
                    },
                    "AutoScalingScheduledAction": {
                        "IgnoreUnmodifiedGroupSizeProperties": True,
                    },
                },
            },
            [],
        ),
        (
            "Valid with lambda function",
            {
                "Type": "AWS::Lambda::Alias",
                "UpdatePolicy": {
                    "CodeDeployLambdaAliasUpdate": {
                        "AfterAllowTrafficHook": "Foo",
                        "ApplicationName": "Foo",
                        "BeforeAllowTrafficHook": "Foo",
                        "DeploymentGroupName": "Foo",
                    }
                },
            },
            [],
        ),
        (
            "Valid with search resource",
            {
                "Type": "AWS::Elasticsearch::Domain",
                "UpdatePolicy": {
                    "EnableVersionUpgrade": True,
                },
            },
            [],
        ),
        (
            "Valid with ElastiCache resource",
            {
                "Type": "AWS::ElastiCache::ReplicationGroup",
                "UpdatePolicy": {"UseOnlineResharding": True},
            },
            [],
        ),
    ],
)
def test_update_policy_configuration(name, instance, expected, rule, validator):
    errors = list(rule.validate(validator, {}, instance, {}))
    assert errors == expected, f"Test {name!r} got {errors!r}"
