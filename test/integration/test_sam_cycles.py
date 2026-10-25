"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

import pytest

from cfnlint import lint
from cfnlint.rules.resources.CircularDependency import CircularDependency
from cfnlint.schema import ResourceNotFoundError
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


@pytest.mark.parametrize(
    "resource_type",
    [
        pytest.param("AWS::Serverless::Function", id="missing-schema"),
        pytest.param("AWS::Serverless::Unknown", id="unmapped-type"),
    ],
)
@pytest.mark.parametrize("explicit_dependency", [False, True])
def test_sam_dependencies_without_property_schema(resource_type, explicit_dependency):
    template = {
        "Resources": {
            "Sam": {
                "Type": resource_type,
                "Properties": {
                    "Environment": {"Variables": {"TARGET": {"Ref": "Target"}}},
                    "Policies": [{"Statement": [{"Resource": {"Ref": "Target"}}]}],
                },
            },
            "Target": {"Type": "AWS::SQS::Queue", "DependsOn": "Sam"},
            "First": {"Type": "AWS::SQS::Queue", "DependsOn": "Second"},
            "Second": {"Type": "AWS::SQS::Queue", "DependsOn": "First"},
        }
    }
    if explicit_dependency:
        template["Resources"]["Sam"]["DependsOn"] = "Target"
    cfn = Template("", template)
    original_template = deepcopy(template)
    original_graph = cfn.graph
    graph_edges = deepcopy(list(original_graph.graph.edges(data=True, keys=True)))

    with patch(
        "cfnlint.rules.resources.CircularDependency."
        "PROVIDER_SCHEMA_MANAGER.get_resource_schema",
        side_effect=ResourceNotFoundError("AWS::Lambda::Function", cfn.regions[0]),
    ) as get_schema:
        matches = CircularDependency().match(cfn)

    if resource_type == "AWS::Serverless::Function":
        get_schema.assert_called_once_with(cfn.regions[0], "AWS::Lambda::Function")
    else:
        get_schema.assert_not_called()

    # Uncertain property dependencies are discarded, while explicit and native
    # cycles still apply even when the SAM resource's properties are unknown.
    expected_resources = {"First", "Second"}
    if explicit_dependency:
        expected_resources.update({"Sam", "Target"})
    assert {match.path[1] for match in matches} == expected_resources
    assert len(matches) == len(expected_resources)
    assert cfn.graph is original_graph
    assert list(original_graph.graph.edges(data=True, keys=True)) == graph_edges
    assert template == original_template
