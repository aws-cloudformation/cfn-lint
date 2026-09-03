"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.core import get_rules, run_checks
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
            "Valid with autoscaling group instance refresh",
            {
                "Type": "AWS::AutoScaling::AutoScalingGroup",
                "UpdatePolicy": {
                    "AutoScalingInstanceRefresh": {
                        "Strategy": "Rolling",
                        "Preferences": {
                            "AlarmSpecification": {"Alarms": ["my-alarm"]},
                            "BakeTime": 600,
                            "CheckpointDelay": 300,
                            "CheckpointPercentages": [50, 100],
                            "InstanceWarmup": 300,
                            "MaxHealthyPercentage": 200,
                            "MinHealthyPercentage": 100,
                            "ScaleInProtectedInstances": "Ignore",
                            "SkipMatching": True,
                            "StandbyInstances": "Terminate",
                        },
                    },
                },
            },
            [],
        ),
        (
            "Invalid with both instance refresh and rolling update",
            {
                "Type": "AWS::AutoScaling::AutoScalingGroup",
                "UpdatePolicy": {
                    "AutoScalingInstanceRefresh": {"Strategy": "Rolling"},
                    "AutoScalingRollingUpdate": {"MaxBatchSize": 1},
                },
            },
            [
                ValidationError(
                    "'AutoScalingRollingUpdate' should not be included with "
                    "'AutoScalingInstanceRefresh'",
                    path=["UpdatePolicy", "AutoScalingRollingUpdate"],
                    rule=Configuration(),
                    instance={
                        "AutoScalingInstanceRefresh": {"Strategy": "Rolling"},
                        "AutoScalingRollingUpdate": {"MaxBatchSize": 1},
                    },
                    validator="dependentExcluded",
                    validator_value={
                        "AutoScalingInstanceRefresh": ["AutoScalingRollingUpdate"]
                    },
                    schema_path=[
                        "allOf",
                        0,
                        "then",
                        "properties",
                        "UpdatePolicy",
                        "dependentExcluded",
                    ],
                )
            ],
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


def test_update_policy_allows_refs_to_template_resources():
    template = {
        "Resources": {
            "MyApp": {
                "Type": "AWS::CodeDeploy::Application",
                "Properties": {"ComputePlatform": "Lambda"},
            },
            "MyDeploymentGroup": {
                "Type": "AWS::CodeDeploy::DeploymentGroup",
                "Properties": {
                    "ApplicationName": {"Ref": "MyApp"},
                    "ServiceRoleArn": "arn:aws:iam::123456789012:role/CodeDeployRole",
                },
            },
            "MyFunction": {
                "Type": "AWS::Lambda::Function",
                "Properties": {
                    "Code": {"ZipFile": "def handler(e, c): pass"},
                    "Handler": "index.handler",
                    "Role": "arn:aws:iam::123456789012:role/LambdaRole",
                    "Runtime": "python3.13",
                },
            },
            "MyVersion": {
                "Type": "AWS::Lambda::Version",
                "Properties": {"FunctionName": {"Ref": "MyFunction"}},
            },
            "MyAlias": {
                "Type": "AWS::Lambda::Alias",
                "Properties": {
                    "FunctionName": {"Ref": "MyFunction"},
                    "FunctionVersion": {"Fn::GetAtt": ["MyVersion", "Version"]},
                    "Name": "live",
                },
                "UpdatePolicy": {
                    "CodeDeployLambdaAliasUpdate": {
                        "ApplicationName": {"Ref": "MyApp"},
                        "DeploymentGroupName": {"Ref": "MyDeploymentGroup"},
                    }
                },
            },
        }
    }

    matches = run_checks(
        "test.yaml", template, get_rules([], [], ["E1020", "E3016"]), ["us-east-1"]
    )

    assert matches == []
