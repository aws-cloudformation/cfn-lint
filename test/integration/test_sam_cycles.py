"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from copy import deepcopy
from pathlib import Path

import pytest

from cfnlint import lint
from cfnlint.rules.resources.CircularDependency import CircularDependency
from cfnlint.template import Template


@pytest.mark.parametrize("fixture,expected", [("a", 0), ("b", 0), ("c", 2)])
def test_sam_cycles(fixture, expected):
    template = Path(
        f"test/fixtures/templates/issues/sam_cycles_{fixture}.yaml"
    ).read_text()
    matches = [match for match in lint(template) if match.rule.id == "E3004"]
    assert len(matches) == expected, matches


@pytest.mark.parametrize("property_name", ["Environment", "Policies", "Events"])
def test_sam_dependencies_and_independent_native_cycle(property_name):
    if property_name == "Environment":
        value = {"Variables": {"TARGET": {"Ref": "Target"}}}
    elif property_name == "Policies":
        value = [
            {
                "Statement": [
                    {"Effect": "Allow", "Action": "s3:*", "Resource": {"Ref": "Target"}}
                ]
            }
        ]
    else:
        value = {
            "Api": {
                "Type": "Api",
                "Properties": {
                    "RestApiId": {"Ref": "Target"},
                    "Path": "/",
                    "Method": "GET",
                },
            }
        }
    template = {
        "Transform": "AWS::Serverless-2016-10-31",
        "Resources": {
            "Function": {
                "Type": "AWS::Serverless::Function",
                "Properties": {
                    "Runtime": "python3.12",
                    "Handler": "index.handler",
                    "InlineCode": "def handler(e, c): return 1",
                    property_name: value,
                },
            },
            "Target": {"Type": "AWS::ApiGateway::RestApi", "DependsOn": "Function"},
            "First": {"Type": "AWS::SQS::Queue", "DependsOn": "Second"},
            "Second": {"Type": "AWS::SQS::Queue", "DependsOn": "First"},
        },
    }
    cfn = Template("test.json", template)
    original_template = deepcopy(template)
    graph_edges = list(cfn.graph.graph.edges(data=True, keys=True))

    matches = CircularDependency().match(cfn)

    expected_resources = {"First", "Second"}
    if property_name != "Events":
        expected_resources.update({"Function", "Target"})
    assert {match.path[1] for match in matches} == expected_resources
    assert list(cfn.graph.graph.edges(data=True, keys=True)) == graph_edges
    assert template == original_template


@pytest.mark.parametrize("dependency", ["Ref", "Fn::GetAtt", "Fn::Sub", "DependsOn"])
def test_real_sam_self_dependency(dependency):
    function = {"Type": "AWS::Serverless::Function", "Properties": {}}
    if dependency == "DependsOn":
        function["DependsOn"] = "Function"
    else:
        value = {dependency: "Function"}
        if dependency == "Fn::GetAtt":
            value = {dependency: ["Function", "Arn"]}
        elif dependency == "Fn::Sub":
            value = {dependency: "${Function.Arn}"}
        function["Properties"] = {"Environment": {"Variables": {"SELF": value}}}
    matches = CircularDependency().match(
        Template("", {"Resources": {"Function": function}})
    )
    assert [match.path for match in matches] == [["Resources", "Function"]]


def test_unused_policies_do_not_create_dependencies():
    template = {
        "Resources": {
            "Function": {
                "Type": "AWS::Serverless::Function",
                "Properties": {
                    "Role": "arn:aws:iam::123456789012:role/existing",
                    "Policies": [{"Statement": [{"Resource": {"Ref": "Function"}}]}],
                },
            }
        }
    }
    assert CircularDependency().match(Template("", template)) == []
