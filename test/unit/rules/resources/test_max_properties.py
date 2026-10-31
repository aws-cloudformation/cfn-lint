"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.unit.rules import BaseRuleTestCase

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
        self.assertIn("has more than 500 properties", errors[0].message)

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
