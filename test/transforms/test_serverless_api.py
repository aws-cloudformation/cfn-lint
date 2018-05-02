"""
  Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.

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
from . import BaseTransformTestCase


class TestServerlessApi(BaseTransformTestCase):
    """Test Transform API """
    def setUp(self):
        super(TestServerlessApi, self).setUp()
        self.template = {
            "AWSTemplateFormatVersion": "2010-09-09",
            "Transform": "AWS::Serverless-2016-10-31",
            "Resources": {
                "myApi": {
                    "Type": "AWS::Serverless::Api",
                    "Properties": {
                        "DefinitionUri": "s3://bucket/swagger.json",
                        "StageName": "Dev"
                    }
                }
            }
        }

    def test_function_autopublish_positive(self):
        """Test converstion of serverless function to include AutoPublish"""

        def test_success(template):
            """Test success"""
            resources = template.get('Resources', {})
            if resources.get('myApiDevStage') and resources.get('myApiDeploymentSHA'):
                return True
            return False

        self.helper_transform_template(self.template, test_success)
