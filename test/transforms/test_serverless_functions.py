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


class TestServerlessFunction(BaseTransformTestCase):
    """Test Rules Get Att """
    def setUp(self):
        super(TestServerlessFunction, self).setUp()
        self.template = {
            "AWSTemplateFormatVersion": "2010-09-09",
            "Transform": "AWS::Serverless-2016-10-31",
            "Resources": {
                "myFunction": {
                    "Type": "AWS::Serverless::Function",
                    "Properties": {
                        "Handler": "index.handler",
                        "Runtime": "nodejs4.3",
                        "CodeUri": "s3://testBucket/mySourceCode.zip"
                    }
                }
            }
        }

    def test_function_autopublish_positive(self):
        """Test converstion of serverless function to include AutoPublish"""

        def test_success(template):
            """Test success"""
            resources = template.get('Resources', {})
            if resources.get('myFunctionVersionLive') and resources.get('myFunctionAliasLive'):
                return True
            return False

        self.template['Resources']['myFunction']['Properties']['AutoPublishAlias'] = 'Live'

        self.helper_transform_template(self.template, test_success)

    def test_function_role_positive(self):
        """Test converstion of serverless function to include Role"""

        def test_success(template):
            """Test success"""
            resource = template.get('Resources', {}).get('myFunctionRole')
            if resource:
                return True
            return False

        self.helper_transform_template(self.template, test_success)

    def test_function_event_api_positive(self):
        """Test converstion of serverless function to API Event"""

        def test_success(template):
            """Test success"""
            resources = template.get('Resources', {})
            if resources.get('ServerlessRestApi') and resources.get('ServerlessRestApiProdStage'):
                return True
            return False

        self.template['Resources']['myFunction']['Properties']['Events'] = {
            "ThumbnailApi": {
                "Type": "Api",
                "Properties": {
                    "Path": "/thumbnail",
                    "Method": "GET"
                }
            }
        }

        self.helper_transform_template(self.template, test_success)
