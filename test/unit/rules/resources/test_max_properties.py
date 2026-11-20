"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.unit.rules import BaseRuleTestCase

import pytest

from cfnlint.jsonschema import CfnTemplateValidator
from cfnlint.rules.resources.ApproachingMaxProperties import ApproachingMaxProperties
from cfnlint.rules.resources.Configuration import Configuration
from cfnlint.rules.resources.MaxProperties import (
    MaxProperties,
    post_sam_transform_resource_count,
)
from cfnlint.template import Template

SAM_TRANSFORM = "AWS::Serverless-2016-10-31"


def _sam_function(**properties):
    base = {"Runtime": "python3.12", "Handler": "index.handler"}
    base.update(properties)
    return {"Type": "AWS::Serverless::Function", "Properties": base}


def _sam_template(count, **function_properties):
    return {
        "AWSTemplateFormatVersion": "2010-09-09",
        "Transform": SAM_TRANSFORM,
        "Resources": {
            f"Fn{i:04d}": _sam_function(**function_properties) for i in range(count)
        },
    }


class TestPostSamTransformResourceCount(BaseRuleTestCase):
    """Test the post-SAM-transform resource count used by E3010"""

    def test_plain_resources_counted_as_written(self):
        resources = {
            "Bucket": {"Type": "AWS::S3::Bucket"},
            "Topic": {"Type": "AWS::SNS::Topic"},
        }
        self.assertEqual(post_sam_transform_resource_count(resources), 2)

    def test_function_without_role_generates_role(self):
        resources = {"Fn": _sam_function()}
        self.assertEqual(post_sam_transform_resource_count(resources), 2)

    def test_function_with_explicit_role_generates_no_role(self):
        resources = {"Fn": _sam_function(Role="arn:aws:iam::123456789012:role/my-role")}
        self.assertEqual(post_sam_transform_resource_count(resources), 1)

    def test_connector_generates_no_resource(self):
        resources = {"Conn": {"Type": "AWS::Serverless::Connector", "Properties": {}}}
        self.assertEqual(post_sam_transform_resource_count(resources), 0)

    def test_function_with_api_event(self):
        resources = {
            "Fn": _sam_function(
                Events={
                    "Api": {
                        "Type": "Api",
                        "Properties": {"Path": "/", "Method": "GET"},
                    }
                }
            )
        }
        # function + role + permission + implicit api + implicit api stage
        self.assertEqual(post_sam_transform_resource_count(resources), 5)

    def test_function_with_deployment_preference(self):
        resources = {"Fn": _sam_function(DeploymentPreference={"Type": "AllAtOnce"})}
        # function + role + version + alias + app + deployment group + role
        self.assertEqual(post_sam_transform_resource_count(resources), 7)

    def test_function_without_deployment_preference_has_no_codedeploy(self):
        resources = {"Fn": _sam_function()}
        self.assertEqual(post_sam_transform_resource_count(resources), 2)

    def test_api_resource(self):
        resources = {
            "Api": {
                "Type": "AWS::Serverless::Api",
                "Properties": {
                    "StageName": "prod",
                    "Domain": {"DomainName": "api.example.com"},
                    "Auth": {"ApiKeyRequired": True},
                },
            }
        }
        # api + stage + domain name + usage plan
        self.assertEqual(post_sam_transform_resource_count(resources), 4)

    def test_generated_ids_are_not_double_counted(self):
        resources = {
            "Fn": _sam_function(),
            "FnRole": {"Type": "AWS::IAM::Role"},
        }
        # the generated FnRole collides with the written one: no double count
        self.assertEqual(post_sam_transform_resource_count(resources), 2)

    def test_non_dict_resources_counted_once(self):
        resources = {"Bad": "not-a-dict", "Bucket": {"Type": "AWS::S3::Bucket"}}
        self.assertEqual(post_sam_transform_resource_count(resources), 2)

    def test_issue_4883_repro_counts_520(self):
        template = _sam_template(260)
        self.assertEqual(post_sam_transform_resource_count(template["Resources"]), 520)


class TestMaxPropertiesSamTransform(BaseRuleTestCase):
    """Test E3010 counts post-transform resources on SAM templates"""

    def setUp(self):
        super(TestMaxPropertiesSamTransform, self).setUp()
        self.config_rule = Configuration()
        self.e3010 = MaxProperties()
        self.e3010.child_rules = {"I3010": ApproachingMaxProperties()}
        self.config_rule.child_rules["E3010"] = self.e3010

    def _validate(self, template):
        validator = CfnTemplateValidator({}).evolve(cfn=Template("", template))
        return list(
            self.config_rule.validate(validator, "Resources", template["Resources"], {})
        )

    def _max_properties_errors(self, template):
        return [e for e in self._validate(template) if e.validator == "maxProperties"]

    def test_issue_4883_repro_fires_e3010(self):
        errors = self._max_properties_errors(_sam_template(260))
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].rule.id, "E3010")
        self.assertIn(
            "has 520 properties, more than the limit of 500", errors[0].message
        )

    def test_sam_template_under_limit_is_clean(self):
        errors = self._max_properties_errors(_sam_template(200))
        self.assertEqual(errors, [])

    def test_sam_template_approaching_limit_fires_i3010(self):
        errors = self._max_properties_errors(_sam_template(240))
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].rule.id, "I3010")

    def test_serverless_resources_without_transform_count_as_written(self):
        template = _sam_template(260)
        del template["Transform"]
        errors = self._max_properties_errors(template)
        self.assertEqual(errors, [])

    def test_non_sam_template_unchanged(self):
        template = {
            "AWSTemplateFormatVersion": "2010-09-09",
            "Resources": {
                f"Bucket{i:04d}": {"Type": "AWS::S3::Bucket"} for i in range(501)
            },
        }
        errors = self._max_properties_errors(template)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].rule.id, "E3010")

    def test_non_sam_template_under_limit_is_clean(self):
        template = {
            "AWSTemplateFormatVersion": "2010-09-09",
            "Resources": {
                f"Bucket{i:04d}": {"Type": "AWS::S3::Bucket"} for i in range(400)
            },
        }
        errors = self._max_properties_errors(template)
        self.assertEqual(errors, [])

    def test_sam_transform_in_list(self):
        template = _sam_template(260)
        template["Transform"] = [SAM_TRANSFORM, "AWS::LanguageExtensions"]
        errors = self._max_properties_errors(template)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].rule.id, "E3010")


@pytest.fixture
def rule():
    config_rule = Configuration()
    e3010 = MaxProperties()
    e3010.child_rules = {"I3010": ApproachingMaxProperties()}
    config_rule.child_rules["E3010"] = e3010
    yield config_rule


def _e3010_errors(rule, validator, template):
    return [
        e
        for e in rule.validate(validator, "Resources", template["Resources"], {})
        if e.validator == "maxProperties" and e.rule.id == "E3010"
    ]


@pytest.mark.parametrize(
    "name,deployment_preference,expected_count",
    [
        (
            "DeploymentPreference without Enabled defaults to enabled",
            {"Type": "AllAtOnce"},
            7,
        ),
        (
            "DeploymentPreference with Enabled true",
            {"Type": "AllAtOnce", "Enabled": True},
            7,
        ),
        (
            "DeploymentPreference with Enabled false",
            {"Type": "AllAtOnce", "Enabled": False},
            4,
        ),
        (
            "DeploymentPreference with Enabled as a string takes the cheaper branch",
            {"Type": "AllAtOnce", "Enabled": "false"},
            4,
        ),
        (
            "DeploymentPreference with Enabled as a Ref takes the cheaper branch",
            {"Type": "AllAtOnce", "Enabled": {"Ref": "EnableDeploy"}},
            4,
        ),
        (
            "DeploymentPreference with Enabled as an Fn::If takes the cheaper branch",
            {
                "Type": "AllAtOnce",
                "Enabled": {"Fn::If": ["UseDeploy", True, False]},
            },
            4,
        ),
    ],
)
def test_function_deployment_preference_enabled(
    name, deployment_preference, expected_count
):
    resources = {"Fn": _sam_function(DeploymentPreference=deployment_preference)}
    count = post_sam_transform_resource_count(resources)
    assert count == expected_count, f"Test {name!r} got {count!r}"


@pytest.mark.parametrize(
    "name,count,expected_count",
    [
        ("250 functions is exactly 500", 250, 500),
        ("251 functions expands past the limit", 251, 502),
    ],
)
def test_sam_function_count_boundary(name, count, expected_count):
    template = _sam_template(count)
    actual = post_sam_transform_resource_count(template["Resources"])
    assert actual == expected_count, f"Test {name!r} got {actual!r}"


@pytest.mark.parametrize(
    "name,template,err_count,message",
    [
        (
            "250 functions is exactly 500, no E3010",
            _sam_template(250),
            0,
            None,
        ),
        (
            "251 functions expands to 502, fires E3010",
            _sam_template(251),
            1,
            "has 502 properties, more than the limit of 500",
        ),
        (
            "100 functions with unresolvable Enabled take the cheaper branch",
            _sam_template(
                100,
                DeploymentPreference={
                    "Type": "AllAtOnce",
                    "Enabled": {"Ref": "EnableDeploy"},
                },
            ),
            0,
            None,
        ),
    ],
    indirect=["template"],
)
def test_sam_function_count_boundary_rule(
    name, template, err_count, message, rule, validator
):
    errors = _e3010_errors(rule, validator, template)
    assert len(errors) == err_count, f"Test {name!r} got {errors!r}"
    if message:
        assert message in errors[0].message
