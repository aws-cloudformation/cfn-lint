"""
  Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.

  Permission is hereby granted, free of charge, to any person obtaining a copy of this
  software and associated documentation files (the "Software"), to deal in the Software
  without restriction, including without limitation the rights to use, copy, modify,
  merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
  permit persons to whom the Software is furnished to do so.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
  INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
  PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
  HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
  OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
  SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import json
from cfnlint import Transform
from cfnlint.decode import cfn_yaml
from testlib.testcase import BaseTestCase

class TestTransform(BaseTestCase):
    """Test Transform Parsing """

    def test_parameter_for_autopublish_version(self):
        """Test Parameter is created for autopublish version run"""
        filename = 'test/fixtures/templates/good/transform/auto_publish_alias.yaml'
        region = 'us-east-1'
        template = cfn_yaml.load(filename)
        transformed_template = Transform(filename, template, region)
        transformed_template.transform_template()
        self.assertDictEqual(transformed_template._parameters, {'Stage': 'Alias'})
        self.assertDictEqual(
          transformed_template._template.get('Resources').get('SkillFunctionAliasAlias').get('Properties'),
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
