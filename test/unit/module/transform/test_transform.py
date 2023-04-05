"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.testlib.testcase import BaseTestCase

from cfnlint import Transform
from cfnlint.decode import cfn_yaml


class TestTransform(BaseTestCase):
    """Test Transform Parsing"""

    def test_parameter_for_autopublish_version(self):
        """Test Parameter is created for autopublish version run"""
        filename = "test/fixtures/templates/good/transform/auto_publish_alias.yaml"
        region = "us-east-1"
        template = cfn_yaml.load(filename)
        transformed_template = Transform(filename, template, region)
        transformed_template.transform_template()
        self.assertDictEqual(
            transformed_template._parameters, {"Stage1": "Alias", "Stage2": "Alias"}
        )
        self.assertDictEqual(
            transformed_template._template.get("Resources")
            .get("SkillFunctionAliasAlias")
            .get("Properties"),
            {
                "Name": "Alias",
                "FunctionName": {"Ref": "SkillFunction"},
                "FunctionVersion": {
                    "Fn::GetAtt": ["SkillFunctionVersion55ff35af87", "Version"]
                },
            },
        )

    def test_conversion_of_step_function_definition_uri(self):
        """Tests that the a serverless step function can convert a local path to a s3 path"""
        filename = (
            "test/fixtures/templates/good/transform/step_function_local_definition.yaml"
        )
        region = "us-east-1"
        template = cfn_yaml.load(filename)
        transformed_template = Transform(filename, template, region)
        transformed_template.transform_template()
        self.assertDictEqual(
            transformed_template._template.get("Resources")
            .get("StateMachine")
            .get("Properties")
            .get("DefinitionS3Location"),
            {"Bucket": "bucket", "Key": "value"},
        )

    def test_conversion_of_application_location(self):
        """Tests if serverless application converts location to string when dict"""
        filename = "test/fixtures/templates/good/transform/applications_location.yaml"
        region = "us-east-1"
        template = cfn_yaml.load(filename)
        transformed_template = Transform(filename, template, region)
        transformed_template.transform_template()
        self.assertEqual(
            transformed_template._template.get("Resources")
            .get("App1")
            .get("Properties")
            .get("TemplateURL"),
            "./step_function_local_definition.yaml",
        )
        self.assertEqual(
            transformed_template._template.get("Resources")
            .get("App2")
            .get("Properties")
            .get("TemplateURL"),
            "s3://bucket/value",
        )

    def test_conversion_of_step_function_definition_uri(self):
        """Tests that the a serverless step function can convert a local path to a s3 path"""
        filename = (
            "test/fixtures/templates/good/transform/step_function_local_definition.yaml"
        )
        region = "us-east-1"
        template = cfn_yaml.load(filename)
        transformed_template = Transform(filename, template, region)
        transformed_template.transform_template()
        self.assertDictEqual(
            transformed_template._template.get("Resources")
            .get("StateMachine")
            .get("Properties")
            .get("DefinitionS3Location"),
            {"Bucket": "bucket", "Key": "value"},
        )

    def test_conversion_of_serverless_function_uri(self):
        """Tests that the a serverless function can convert a CodeUri Sub"""
        filename = "test/fixtures/templates/good/transform/function_use_s3_uri.yaml"
        region = "us-east-1"
        template = cfn_yaml.load(filename)
        transformed_template = Transform(filename, template, region)
        transformed_template.transform_template()
        self.assertDictEqual(
            transformed_template._template.get("Resources")
            .get("Function")
            .get("Properties")
            .get("Code"),
            {"S3Bucket": "bucket", "S3Key": "value"},
        )

    def test_parameter_for_autopublish_version_bad(self):
        """Test Parameter is created for autopublish version run"""
        filename = "test/fixtures/templates/bad/transform/auto_publish_alias.yaml"
        region = "us-east-1"
        template = cfn_yaml.load(filename)
        transformed_template = Transform(filename, template, region)
        transformed_template.transform_template()
        self.assertDictEqual(transformed_template._parameters, {})

    def test_test_function_using_image_good(self):
        """Test Parameter is created for autopublish version run"""
        filename = "test/fixtures/templates/good/transform/function_using_image.yaml"
        region = "us-east-1"
        template = cfn_yaml.load(filename)
        transformed_template = Transform(filename, template, region)
        transformed_template.transform_template()
        self.assertDictEqual(transformed_template._parameters, {})

    def test_sam_with_language_extension(self):
        """Test language extension"""
        filename = "test/fixtures/templates/good/transform/language_extension.yaml"
        region = "us-east-1"
        template = cfn_yaml.load(filename)
        transformed_template = Transform(filename, template, region)
        results = transformed_template.transform_template()
        self.assertEqual(results, [])
