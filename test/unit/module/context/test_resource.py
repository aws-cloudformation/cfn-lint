"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import os
from unittest.mock import patch

import pytest

from cfnlint.context.context import Resource, _init_resources
from cfnlint.match import Match
from cfnlint.rules.errors.parse import ParseError
from cfnlint.schema import AttributeDict


@pytest.mark.parametrize(
    "name,instance,expected_ref",
    [
        (
            "Valid resource",
            {"Type": "AWS::EC2::VPC"},
            {"description": "", "format": "AWS::EC2::VPC.Id", "type": "string"},
        ),
    ],
)
def test_resource(name, instance, expected_ref):
    region = "us-east-1"
    resource = Resource(instance)

    assert expected_ref == resource.ref(region), (
        f"{name!r} test got {resource.ref(region)}"
    )


@pytest.mark.parametrize(
    "name,instance",
    [
        ("Invalid Type", {"Type": {}}),
    ],
)
def test_errors(name, instance):
    with pytest.raises(ValueError):
        Resource(instance)


def test_resources():
    with pytest.raises(ValueError):
        _init_resources([])


@pytest.mark.parametrize(
    "name,instance,filename,decode_results,expected_getatts",
    [
        (
            "Nested stack with no Properties",
            {"Type": "AWS::CloudFormation::Stack"},
            "foo/bar.yaml",
            None,
            AttributeDict({"Outputs\\..*": "/properties/CfnLintStringType"}),
        ),
        (
            "Nested stack with template URL",
            {
                "Type": "AWS::CloudFormation::Stack",
                "Properties": {"TemplateURL": "https://bucket/path.yaml"},
            },
            "foo/bar.yaml",
            None,
            AttributeDict({"Outputs\\..*": "/properties/CfnLintStringType"}),
        ),
        (
            "Nested stack with a None filename",
            {
                "Type": "AWS::CloudFormation::Stack",
                "Properties": {"TemplateURL": "application.yaml"},
            },
            None,
            None,
            AttributeDict({"Outputs\\..*": "/properties/CfnLintStringType"}),
        ),
        (
            "Nested stack with a local file",
            {
                "Type": "AWS::CloudFormation::Stack",
                "Properties": {"TemplateURL": "./bar.yaml"},
            },
            "foo/bar.yaml",
            (
                {
                    "Resources": {"Bucket": {"Type": "AWS::S3::Bucket"}},
                    "Outputs": {"MyValue": {"Type": "String"}},
                },
                None,
            ),
            AttributeDict({"Outputs.MyValue": "/properties/CfnLintStringType"}),
        ),
        (
            "Nested stack with a local file and no outputs",
            {
                "Type": "AWS::CloudFormation::Stack",
                "Properties": {"TemplateURL": "./bar.yaml"},
            },
            "foo/bar.yaml",
            ({"Resources": {"Bucket": {"Type": "AWS::S3::Bucket"}}}, None),
            AttributeDict({}),
        ),
        (
            "Nested stack with a local file that isn't a template",
            {
                "Type": "AWS::CloudFormation::Stack",
                "Properties": {"TemplateURL": "./bar.yaml"},
            },
            "foo/bar.yaml",
            ({"Outputs": {"MyValue": {"Type": "String"}}}, None),
            AttributeDict({"Outputs\\..*": "/properties/CfnLintStringType"}),
        ),
        (
            "Nested stack with a local file with empty resources",
            {
                "Type": "AWS::CloudFormation::Stack",
                "Properties": {"TemplateURL": "./bar.yaml"},
            },
            "foo/bar.yaml",
            ({"Resources": {}, "Outputs": {"MyValue": {"Type": "String"}}}, None),
            AttributeDict({"Outputs\\..*": "/properties/CfnLintStringType"}),
        ),
        (
            "Nested stack with a TemplateURL that isn't a string",
            {
                "Type": "AWS::CloudFormation::Stack",
                "Properties": {"TemplateURL": {"Ref": "NestedTemplate"}},
            },
            "foo/bar.yaml",
            None,
            AttributeDict({"Outputs\\..*": "/properties/CfnLintStringType"}),
        ),
        (
            "Nested stack with a local file but match error",
            {
                "Type": "AWS::CloudFormation::Stack",
                "Properties": {"TemplateURL": "./bar.yaml"},
            },
            "foo/bar.yaml",
            (None, Match("test", rule=ParseError())),
            AttributeDict({"Outputs\\..*": "/properties/CfnLintStringType"}),
        ),
    ],
)
def test_nested_stacks(name, instance, filename, decode_results, expected_getatts):
    region = "us-east-1"

    with patch("cfnlint.decode.decode") as mock_decode:
        if decode_results is not None:
            mock_decode.return_value = decode_results

        resource = Resource(instance, filename)

        assert expected_getatts == resource.get_atts(region), (
            f"{name!r} test got {resource.get_atts(region)}"
        )


@pytest.mark.parametrize(
    "name,template_url",
    [
        (
            "Absolute path",
            "/etc/passwd",
        ),
        (
            "Absolute path with Windows style",
            "C:\\Windows\\System32\\config\\SAM",
        ),
        (
            "Path traversal escaping cwd",
            "../../../../etc/passwd",
        ),
        (
            "Path traversal to root",
            "../../../../../../../etc/passwd",
        ),
    ],
)
def test_nested_stack_path_traversal_blocked(name, template_url):
    """
    Test that path traversal attempts are blocked and decode is never called.
    This prevents reading arbitrary files outside the current working directory.
    """
    region = "us-east-1"
    instance = {
        "Type": "AWS::CloudFormation::Stack",
        "Properties": {"TemplateURL": template_url},
    }
    # Use a filename within the cwd
    filename = "templates/main.yaml"

    with patch("cfnlint.decode.decode") as mock_decode:
        # decode should never be called for traversal attempts
        mock_decode.side_effect = AssertionError("decode should not be called")

        resource = Resource(instance, filename)

        # Should fall back to default GetAtts pattern (no file read)
        expected = AttributeDict({"Outputs\\..*": "/properties/CfnLintStringType"})
        assert expected == resource.get_atts(region), f"{name!r} should block traversal"


_NESTED_TEMPLATE = """AWSTemplateFormatVersion: "2010-09-09"
Resources:
  Bucket:
    Type: AWS::S3::Bucket
Outputs:
  VpcId:
    Value: value
"""

_NOT_A_TEMPLATE = """version: 2
Outputs:
  billing_db_password: reference
"""

_PERMISSIVE = AttributeDict({"Outputs\\..*": "/properties/CfnLintStringType"})
_RESOLVED = AttributeDict({"Outputs.VpcId": "/properties/CfnLintStringType"})


@pytest.fixture
def workspace(tmp_path):
    """A template directory, a sibling directory, and one outside both"""
    (tmp_path / "workspace" / "templates").mkdir(parents=True)
    (tmp_path / "workspace" / "common").mkdir()
    (tmp_path / "outside").mkdir()
    (tmp_path / "workspace" / "templates" / "nested.yaml").write_text(_NESTED_TEMPLATE)
    (tmp_path / "workspace" / "common" / "nested.yaml").write_text(_NESTED_TEMPLATE)
    (tmp_path / "workspace" / "common" / "config.yaml").write_text(_NOT_A_TEMPLATE)
    (tmp_path / "outside" / "nested.yaml").write_text(_NESTED_TEMPLATE)
    return tmp_path


def _nested_get_atts(workspace, template_url):
    instance = {
        "Type": "AWS::CloudFormation::Stack",
        "Properties": {"TemplateURL": template_url},
    }
    filename = str(workspace / "workspace" / "templates" / "main.yaml")
    return Resource(instance, filename).get_atts("us-east-1")


@pytest.mark.parametrize(
    "name,cwd,template_url,expected",
    [
        (
            "Same directory",
            "workspace",
            "./nested.yaml",
            _RESOLVED,
        ),
        (
            "Sibling directory below the cwd",
            "workspace",
            "../common/nested.yaml",
            _RESOLVED,
        ),
        (
            "Sibling directory above the cwd",
            "workspace/templates",
            "../common/nested.yaml",
            _PERMISSIVE,
        ),
        (
            "Outside the cwd",
            "workspace",
            "../../outside/nested.yaml",
            _PERMISSIVE,
        ),
        (
            "Drive root as the cwd",
            None,
            "../common/nested.yaml",
            _RESOLVED,
        ),
        (
            "Missing file",
            "workspace",
            "../common/no-such-file.yaml",
            _PERMISSIVE,
        ),
        (
            "File that isn't a template",
            "workspace",
            "../common/config.yaml",
            _PERMISSIVE,
        ),
    ],
)
def test_nested_stack_containment(
    name, cwd, template_url, expected, workspace, monkeypatch
):
    """A nested template resolves below the working directory and nowhere else"""
    monkeypatch.chdir(workspace.anchor if cwd is None else workspace / cwd)

    assert expected == _nested_get_atts(workspace, template_url), (
        f"{name!r} got {_nested_get_atts(workspace, template_url)}"
    )


def test_nested_stack_absolute_path_blocked(workspace, monkeypatch):
    monkeypatch.chdir(workspace)
    template_url = str(workspace / "workspace" / "common" / "nested.yaml")

    assert _PERMISSIVE == _nested_get_atts(workspace, template_url)


@pytest.mark.skipif(os.name == "nt", reason="symlinks need privileges on Windows")
def test_nested_stack_symlink_cannot_escape_cwd(workspace, monkeypatch):
    (workspace / "workspace" / "vendor").symlink_to(workspace / "outside")
    monkeypatch.chdir(workspace / "workspace")

    assert _PERMISSIVE == _nested_get_atts(workspace, "../vendor/nested.yaml")


def test_nested_stack_unrelated_drive(workspace, monkeypatch):
    """commonpath raises when the cwd and the template are on different drives"""

    def _different_drives(paths):
        raise ValueError("Paths don't have the same drive")

    monkeypatch.setattr(os.path, "commonpath", _different_drives)
    monkeypatch.chdir(workspace)

    assert _PERMISSIVE == _nested_get_atts(workspace, "./nested.yaml")
