"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.testlib.testcase import BaseTestCase
from cfnlint import Transform
from cfnlint.decode import cfn_yaml


class TestTransform(BaseTestCase):
    """Test Transform Parsing """

    def test_parameter_for_autopublish_version(self):
        """Test Parameter is created for autopublish version run"""
        filename = 'test/fixtures/templates/good/transform/auto_publish_alias.yaml'
        region = 'us-east-1'
        template = cfn_yaml.load(filename)
        transformed_template = Transform(filename, template, region)
        transformed_template.transform_template()
        self.assertDictEqual(transformed_template._parameters, {
                             'Stage1': 'Alias', 'Stage2': 'Alias'})
        self.assertDictEqual(
            transformed_template._template.get('Resources').get(
                'SkillFunctionAliasAlias').get('Properties'),
            {
                'Name': 'Alias',
                'FunctionName': {'Ref': 'SkillFunction'},
                'FunctionVersion': {'Fn::GetAtt': ['SkillFunctionVersionb3d38083f6', 'Version']}
            })

    def test_parameter_for_autopublish_version_bad(self):
        """Test Parameter is created for autopublish version run"""
        filename = 'test/fixtures/templates/bad/transform/auto_publish_alias.yaml'
        region = 'us-east-1'
        template = cfn_yaml.load(filename)
        transformed_template = Transform(filename, template, region)
        transformed_template.transform_template()
        self.assertDictEqual(transformed_template._parameters, {})
