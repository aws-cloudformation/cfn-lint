"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import pytest

from cfnlint.rules.outputs.ExportUnique import ExportUnique
from cfnlint.template import Template


@pytest.fixture(scope="module")
def rule():
    yield ExportUnique()


def _template(outputs, conditions=None):
    template = {
        "AWSTemplateFormatVersion": "2010-09-09",
        "Parameters": {"Env": {"Type": "String", "Default": "prod"}},
        "Resources": {"Topic": {"Type": "AWS::SNS::Topic"}},
        "Outputs": outputs,
    }
    if conditions:
        template["Conditions"] = conditions
    return Template("", template, ["us-east-1"])


def _output(name, condition=None):
    output = {"Value": {"Ref": "Topic"}, "Export": {"Name": name}}
    if condition:
        output["Condition"] = condition
    return output


_CONDITIONS = {
    "IsProd": {"Fn::Equals": [{"Ref": "Env"}, "prod"]},
    "IsNotProd": {"Fn::Not": [{"Fn::Equals": [{"Ref": "Env"}, "prod"]}]},
}


@pytest.mark.parametrize(
    "name,outputs,conditions,expected",
    [
        (
            "Unique export names",
            {"A": _output("export-a"), "B": _output("export-b")},
            None,
            0,
        ),
        (
            "Duplicate export names",
            {"A": _output("dup"), "B": _output("dup")},
            None,
            2,
        ),
        (
            "Three outputs sharing a name",
            {"A": _output("dup"), "B": _output("dup"), "C": _output("dup")},
            None,
            3,
        ),
        (
            "Duplicate names with the same condition",
            {"A": _output("dup", "IsProd"), "B": _output("dup", "IsProd")},
            _CONDITIONS,
            2,
        ),
        (
            "Duplicate names with mutually exclusive conditions",
            {"A": _output("dup", "IsProd"), "B": _output("dup", "IsNotProd")},
            _CONDITIONS,
            0,
        ),
        (
            "Duplicate names, one output unconditioned",
            {"A": _output("dup"), "B": _output("dup", "IsProd")},
            _CONDITIONS,
            2,
        ),
        (
            "Intrinsic export names are skipped",
            {
                "A": _output({"Fn::Sub": "${AWS::StackName}-topic"}),
                "B": _output({"Fn::Sub": "${AWS::StackName}-topic"}),
            },
            None,
            0,
        ),
        (
            "Outputs without exports",
            {
                "A": {"Value": {"Ref": "Topic"}},
                "B": {"Value": {"Ref": "Topic"}},
            },
            None,
            0,
        ),
    ],
)
def test_export_unique(name, outputs, conditions, expected, rule):
    matches = rule.match(_template(outputs, conditions))
    assert len(matches) == expected, f"{name}: got {matches}"
